import abc
import os
from pathlib import Path
import yaml, os

from hypernets.hyperctl.batch import ShellJob, Batch
from hypernets.hyperctl.schedule import run_batch
from hypernets.utils import logging
logging.set_level('DEBUG')

logger = logging.getLogger(__name__)

SRC_DIR = os.path.dirname(__file__)


class EnvSpec:

    def __init__(self, kind, custom_python=None, pip=None, conda=None):
        self.kind = kind
        self.custom_python = custom_python
        self.pip = pip
        self.conda = conda


class PlayerSpec:

    def __init__(self, name, env: EnvSpec):
        self.name = name
        self.env = env
        self.exec_file = 'exec.py'
        # 1. check env file
        # 2. check config file


class Benchmark(metaclass=abc.ABCMeta):

    def __init__(self, name, desc, players, constraints):
        self.name = name
        self.desc = desc
        self.players = players
        self.constraints = constraints

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def setup_player(self, player: PlayerSpec):
        pass

    @abc.abstractmethod
    def run(self):
        pass


class BenchmarkBaseOnHyperctl(Benchmark, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate_hyperctl_jobs(self):
        pass

    def add_job(self, player_name, task_id, batch: Batch):
        name = f'{player_name}_{task_id}'
        job_params = {
            "task_id": task_id,
        }
        execution = {
            'command': '/usr/bin/python /home/a.py'
        }
        batch.add_job(name=name, params=job_params, resource=None, execution=execution)

    def run(self):
        tasks = self.get_tasks()
        players = self.get_players()
        batch: Batch = None
        for task in tasks:
            for player in players:
                self.add_job(player.name, task.name, batch)
        run_batch(batch)

    def get_players(self):
        return []

    def get_tasks(self):
        return []


class LocalBenchmark(BenchmarkBaseOnHyperctl):
    def setup(self):
        for player in self.players:
            self.setup_player(player)

    def generate_hyperctl_jobs(self):
        pass

    def setup_player(self, player: PlayerSpec):
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
    play_dict['env'] = EnvSpec(**play_dict['env'])

    return PlayerSpec(**play_dict)


def load_players(player_specs):

    def put_player(dict_obj, _: PlayerSpec):
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
