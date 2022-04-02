import abc
import os
from pathlib import Path
import yaml, os
from typing import List

from hypernets.hyperctl.batch import ShellJob, Batch, BackendConf, ServerConf
from hypernets.hyperctl.appliation import BatchApplication

# from hypernets.hyperctl.scheduler import run_batch
from hypernets.utils import logging
logging.set_level('DEBUG')

logger = logging.getLogger(__name__)

SRC_DIR = os.path.dirname(__file__)


class PythonEnv:

    def __init__(self, kind, custom_python=None, pip=None, conda=None):
        self.kind = kind
        self.custom_python = custom_python
        self.pip = pip
        self.conda = conda

    KIND_CUSTOM_PYTHON = 'custom_python'


class Player:

    def __init__(self, name, exec_file: str, env: PythonEnv):
        self.name = name
        self.env: PythonEnv = env
        self.exec_file = exec_file
        # 1. check env file
        # 2. check config file

    @property
    def py_executable(self):
        if self.env.kind == PythonEnv.KIND_CUSTOM_PYTHON:
            return self.env.custom_python['executable']
        else:
            raise ValueError(f"unseen env kind {self.env.kind}")


class Benchmark(metaclass=abc.ABCMeta):

    def __init__(self, name, desc, players, tasks, constraints):
        self.name = name
        self.desc = desc
        self.players: List[Player] = players
        self.tasks = tasks
        self.constraints = constraints

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def setup_player(self, player: Player):
        pass

    @abc.abstractmethod
    def run(self):
        pass


class BenchmarkBaseOnHyperctl(Benchmark, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate_hyperctl_jobs(self):
        pass

    def add_job(self, player: Player, task_id, batch: Batch):
        name = f'{player.name}_{task_id}'
        job_params = {
            "task_id": task_id,
        }

        command = f"{player.py_executable} {player.exec_file}"

        working_dir = (batch.data_dir_path() / name).absolute().as_posix()
        batch.add_job(name=name,
                      params=job_params,
                      command=command,
                      output_dir=working_dir,
                      working_dir=working_dir)

    def run(self):
        tasks = self.tasks
        players = self.players
        # create batch app
        batches_data_dir = Path("~/tsbenchmark-hyperctl").expanduser().absolute().as_posix()  # TODO move config file

        # backend_conf = BackendConf(type = 'local', conf = {})
        from hypernets.utils import common
        batch_name = common.generate_short_id()  # TODO move to benchmark
        batch: Batch = Batch(batch_name, batches_data_dir)
        for task in tasks:
            for player in players:
                self.add_job(player, task.id, batch)

        batch_app = BatchApplication(batch)
        batch_app.start()



class LocalBenchmark(BenchmarkBaseOnHyperctl):
    def setup(self):
        for player in self.players:
            self.setup_player(player)

    def generate_hyperctl_jobs(self):
        pass

    def setup_player(self, player: Player):
        # setup environment
        if player.env.kind == 'custom_python':
            pass
        else:
            pass

    def prepare_by_pip(self):
        pass

    def prepare_by_conda(self):
        pass


def load_player(folder):
    config_file = Path(folder) / "player.yaml"
    if not config_file.exists():
        raise FileNotFoundError(config_file)

    assert config_file.exists()
    with open(config_file, 'r') as f:
        content = f.read()

    play_dict = yaml.load(content, Loader=yaml.CLoader)

    # name, exec_file, env: EnvSpec
    if 'name' not in play_dict:
        play_dict['name'] = os.path.basename(folder)

    exec_file = (Path(folder) / "exec.py").absolute().as_posix()

    play_dict['exec_file'] = exec_file
    play_dict['env'] = PythonEnv(**play_dict['env'])

    return Player(**play_dict)


def load_players(player_specs):

    def put_player(dict_obj, _: Player):
        if _.name not in dict_obj:
            dict_obj[_.name] = _
        else:
            raise RuntimeError(f"already exists key {_.name}")

    default_players = {}

    # 1. load default players
    default_players_dir = (Path(SRC_DIR).parent / "players")
    logger.debug(f"default players dir is at {default_players_dir}")
    for player_folder in os.listdir(default_players_dir):
        # filter dirs
        player_dir = default_players_dir / player_folder
        if os.path.isdir(player_dir):
            logger.debug(f'detected player at {player_dir}')
            player = load_player(player_dir)
            put_player(default_players, player)

    # 2. load user custom players
    selected_players = {}
    for player_name_or_path in player_specs:
        if player_name_or_path not in default_players:  # is a path
            # load as a directory
            abs_player_path = os.path.abspath(player_name_or_path)
            logger.info(f"read player from dir {abs_player_path}")

            player = load_player(Path(player_name_or_path))
            put_player(selected_players, player)
        else:
            player_name = player_name_or_path
            put_player(selected_players, default_players[player_name])

    return list(selected_players.values())


def get_benchmark(kind):
    players = load_players(['plain_player'])
    lb = LocalBenchmark(name='name', desc='desc', players=players, constraints={})

    return lb
