import abc
import os
import sys
from pathlib import Path
import yaml, os
from typing import List

from hypernets.hyperctl.batch import ShellJob, Batch, BackendConf, ServerConf
from hypernets.hyperctl.appliation import BatchApplication

# from hypernets.hyperctl.scheduler import run_batch
from hypernets.hyperctl.server import create_hyperctl_handlers
from hypernets.utils import logging
from tsbenchmark.server import BenchmarkBatchApplication
logging.set_level('DEBUG')

logger = logging.getLogger(__name__)


SRC_DIR = os.path.dirname(__file__)


class BaseMRGConfig:
    pass


class CondaVenvMRGConfig(BaseMRGConfig):
    def __init__(self, name):
        self.name = name


class CustomPyMRGConfig(BaseMRGConfig):
    def __init__(self, py_executable):
        self.py_executable = py_executable


class BaseReqsConfig:
    pass


class ReqsRequirementsTxtConfig(BaseReqsConfig):

    def __init__(self, py_version, file_name):
        self.py_version = py_version
        self.file_name = file_name


class ReqsCondaYamlConfig(BaseReqsConfig):

    def __init__(self, file_name):
        self.file_name = file_name


class PythonEnv:

    def __init__(self, venv: BaseMRGConfig, requirements: BaseReqsConfig):
        self.venv = venv
        self.requirements = requirements

    KIND_CUSTOM_PYTHON = 'custom_python'
    KIND_CONDA = 'conda'

    REQUIREMENTS_REQUIREMENTS_TXT = 'requirements_txt'
    REQUIREMENTS_CONDA_YAML = 'conda_yaml'

    @property
    def venv_kind(self):
        if isinstance(self.venv, CondaVenvMRGConfig):
            return PythonEnv.KIND_CONDA
        elif isinstance(self.venv, CustomPyMRGConfig):
            return PythonEnv.KIND_CUSTOM_PYTHON
        else:
            raise ValueError(f"unknown venv manager {self.venv}")

    @property
    def reqs_kind(self):
        if isinstance(self.requirements,  ReqsRequirementsTxtConfig):
            return PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT
        elif isinstance(self.requirements,  ReqsCondaYamlConfig):
            return PythonEnv.REQUIREMENTS_CONDA_YAML
        else:
            raise ValueError(f"unknown requirements config {self.venv}")


class Player:
    def __init__(self, base_dir, exec_file: str, env: PythonEnv, tasks=None):
        self.base_dir = base_dir
        self.base_dir_path = Path(base_dir)

        self.env: PythonEnv = env
        self.exec_file = exec_file
        self.tasks = tasks  # default is None, mean support all task type

        assert self.abs_exec_file_path().exists(), "exec_file not exists"

    @property
    def name(self):
        return Path(self.base_dir).name

    def abs_exec_file_path(self):
        return self.base_dir_path / self.exec_file


class JobParams:
    def __init__(self, bm_task_id, task_config_id,  random_state,  max_trails=None, reward_metric=None, **kwargs):
        self.bm_task_id = bm_task_id
        self.task_config_id = task_config_id
        self.random_state = random_state
        self.max_trails = max_trails
        self.reward_metric = reward_metric

    def to_dict(self):
        return self.__dict__


def load_player(folder):
    folder_path = Path(folder)

    config_file = Path(folder) / "player.yaml"
    if not config_file.exists():
        raise FileNotFoundError(config_file)

    assert config_file.exists()
    with open(config_file, 'r') as f:
        content = f.read()

    play_dict = yaml.load(content, Loader=yaml.CLoader)

    play_dict['exec_file'] = "exec.py"

    env_dict = play_dict['env']

    env_venv_dict = env_dict.get('venv')
    env_mgr_kind = env_venv_dict['kind']
    env_mgr_config = env_venv_dict.get('config', {})

    player_name = folder_path.name
    if env_mgr_kind == PythonEnv.KIND_CONDA:
        env_mgr_config['name'] = env_mgr_config.get('name', f'tbs-{player_name}')  # set default env name
        mgr_config = CondaVenvMRGConfig(**env_mgr_config)
        requirements_dict = env_dict.get('requirements')
        requirements_kind = requirements_dict['kind']
        requirements_config = requirements_dict.get('config', {})

        if requirements_kind == PythonEnv.REQUIREMENTS_CONDA_YAML:
            reqs_config = ReqsCondaYamlConfig(**requirements_config)
        elif requirements_kind == PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT:
            requirements_config['py_version'] = str(requirements_config['py_version'])
            reqs_config = ReqsRequirementsTxtConfig(**requirements_config)
        else:
            raise Exception(f"Unsupported env manager {env_mgr_kind}")

    elif env_mgr_kind == PythonEnv.KIND_CUSTOM_PYTHON:
        env_mgr_config['py_executable'] = env_mgr_config.get('py_executable', sys.executable)
        mgr_config = CustomPyMRGConfig(**env_mgr_config)
        reqs_config = None
    else:
        raise Exception(f"Unsupported env manager {env_mgr_kind}")

    play_dict['env'] = PythonEnv(venv=mgr_config, requirements=reqs_config)
    play_dict['base_dir'] = Path(folder).absolute().as_posix()
    return Player(**play_dict)


