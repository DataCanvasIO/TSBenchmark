import json
import random
import shutil
from pathlib import Path
import os

import tsbenchmark
from hypernets.hyperctl.utils import load_yaml
from tsbenchmark import consts
from tsbenchmark.benchmark import LocalBenchmark, RemoteSSHBenchmark, Benchmark
import tsbenchmark.tasks
from tsbenchmark.callbacks import BenchmarkCallback
from . import util

from tsbenchmark.consts import DEFAULT_BENCHMARK_DATA_DIR
from tsbenchmark.players import Player, load_player
from hypernets.utils import logging


SRC_DIR = os.path.dirname(__file__)

logger = logging.getLogger(__name__)


def _load_players(player_folders):

    def put_player(dict_obj, _: Player):
        if _.name not in dict_obj:
            dict_obj[_.name] = _
        else:
            raise RuntimeError(f"already exists key {_.name}")

    # default_players = {}

    # 1. load default players
    # default_players_dir = Path(SRC_DIR).parent / "players"
    # logger.debug(f"default players dir is at {default_players_dir}")
    # for player_folder in os.listdir(default_players_dir):
    #     # filter dirs
    #     player_dir = default_players_dir / str(player_folder)
    #     if os.path.isdir(player_dir):
    #         logger.debug(f'detected player at {player_dir}')
    #         player = load_player(player_dir)
    #         put_player(default_players, player)

    # 2. load user custom players
    selected_players = {}
    for player_name_or_path in player_folders:
        # if player_name_or_path not in default_players:  # is a path
        # load as a directory
        abs_player_path = os.path.abspath(player_name_or_path)
        logger.debug(f"read player from dir {abs_player_path}")

        player = load_player(Path(player_name_or_path))
        put_player(selected_players, player)

    return list(selected_players.values())


class CopyCfgCallback(BenchmarkCallback):

    def __init__(self, config_file, random_state_file_name='random_states'):
        self.config_file = config_file
        self.random_state_file_name = random_state_file_name

    def on_start(self, bm):
        bm: Benchmark = bm
        config_file_path = Path(self.config_file)

        # write config file
        config_file_destination_path = Path(bm.data_dir) / config_file_path.name
        os.makedirs(config_file_destination_path.parent.as_posix(), exist_ok=True)
        shutil.copy(self.config_file, config_file_destination_path.as_posix())

        # write status file
        random_state_path = Path(bm.data_dir) / self.random_state_file_name
        with open(random_state_path, 'w') as f:
            json.dump(bm.random_states, f)


def load_benchmark(config_file: str, benchmarks_data_dir=None):
    config_dict = load_yaml(config_file)
    name = config_dict['name']
    desc = config_dict.get('desc', '')
    kind = config_dict.get('kind', 'local')
    assert kind in ['local', 'remote']

    # check name
    assert util.is_safe_dir_name(name), "benchmark can only contains letters, numbers, '-' and '_' ."

    # data_dir
    if benchmarks_data_dir is None:
        benchmarks_data_dir = config_dict.get('benchmarks_data_dir', DEFAULT_BENCHMARK_DATA_DIR)

    data_dir = (Path(benchmarks_data_dir).expanduser() / name).as_posix()

    # select datasets and tasks
    datasets_config = config_dict.get('tasks', {})
    datasets_config_cache_path = datasets_config.get('cache_path')
    if datasets_config_cache_path is not None:
        os.environ[consts.ENV_DATASETS_CACHE_PATH] = datasets_config_cache_path

    datasets_filter_config = datasets_config.get('filter', {})
    datasets_filter_tasks = datasets_filter_config.get('task_types')

    datasets_filter_data_sizes = datasets_filter_config.get('data_sizes')

    datasets_filter_dataset_ids = datasets_filter_config.get('dataset_ids')

    datasets_filter_task_ids = datasets_filter_config.get('task_ids')

    task_configs = tsbenchmark.tasks.list_task_configs(task_types=datasets_filter_tasks,
                                                       dataset_sizes=datasets_filter_data_sizes,
                                                       dataset_ids=datasets_filter_dataset_ids,
                                                       task_ids=datasets_filter_task_ids)

    assert task_configs is not None and len(task_configs) > 0, "no task selected"

    # load tasks
    # task_configs = [tsbenchmark.tasks.get_task_config(tid) for tid in selected_task_ids]

    # load players
    players_name_or_path = config_dict.get('players')
    players = _load_players(players_name_or_path)
    assert players is not None and len(players) > 0, "no players selected"

    # random_states
    random_states = config_dict.get('random_states')
    if random_states is None or len(random_states) < 1:
        n_random_states = config_dict.get('n_random_states', 3)
        random_states = [random.Random().randint(1000, 10000) for _ in range(n_random_states)]

    # constraints
    task_constraints = config_dict.get('constraints', {}).get('task')

    # copy configs
    copy_cfg_callback = CopyCfgCallback(config_file)
    callbacks = [copy_cfg_callback]

    # report
    report = config_dict.get('report', {})
    report_enable = report.get('enable', True)
    if report_enable is True:
        default_report_dir = (Path(data_dir) / "report").as_posix()
        report_dir = Path(report.get('path', default_report_dir)).expanduser().as_posix()
        if not os.path.exists(report_dir):
            os.makedirs(report_dir, exist_ok=True)

        task_types = list(set(t.task for t in task_configs))
        # datasets_filter_tasks if datasets_filter_tasks is not None else []
        from tsbenchmark.callbacks import ReporterCallback
        benchmark_config = {
            'report.path': report_dir,
            'name': name,
            'desc': desc,
            'random_states': random_states,
            'task_filter.tasks': task_types
         }
        callbacks.append(ReporterCallback(benchmark_config=benchmark_config))

    # batch_application_config
    batch_application_config = config_dict.get('batch_application_config', {})

    init_kwargs = dict(name=name, desc=desc, players=players, callbacks=callbacks,
                       batch_app_init_kwargs=batch_application_config,
                       data_dir=data_dir, random_states=random_states,
                       ts_tasks_config=task_configs, task_constraints=task_constraints)

    if kind == 'local':
        # venvs
        conda_home = config_dict.get('venv', {}).get('conda', {}).get('home')
        benchmark = LocalBenchmark(conda_home=conda_home, **init_kwargs)
        return benchmark
    elif kind == 'remote':
        machines = config_dict['machines']
        benchmark = RemoteSSHBenchmark(**init_kwargs, machines=machines)
        return benchmark
    else:
        raise RuntimeError(f"Unseen kind {kind}")
