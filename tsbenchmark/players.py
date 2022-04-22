import abc
import os
from pathlib import Path
import yaml, os
from typing import List

from hypernets.hyperctl.batch import ShellJob, Batch, BackendConf, ServerConf
from hypernets.hyperctl.appliation import BatchApplication

# from hypernets.hyperctl.scheduler import run_batch
from hypernets.hyperctl.server import create_hyperctl_handlers
from hypernets.utils import logging
from tsbenchmark.server import BenchmarkBatchApplication


class PythonEnv:

    def __init__(self, kind, custom_python=None, pip=None, conda=None):
        self.kind = kind
        self.custom_python = custom_python
        self.pip = pip
        self.conda = conda

    KIND_CUSTOM_PYTHON = 'custom_python'

logging.set_level('DEBUG')

logger = logging.getLogger(__name__)

SRC_DIR = os.path.dirname(__file__)


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


class JobParams:
    def __init__(self, bm_task_id, task_config_id,  random_state,  max_trails, reward_metric, **kwargs):
        self.bm_task_id = bm_task_id
        self.task_config_id = task_config_id
        self.random_state = random_state
        self.max_trails = max_trails
        self.reward_metric = reward_metric

    def to_dict(self):
        return self.__dict__


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

