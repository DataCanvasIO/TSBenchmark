import os
import sys
from pathlib import Path

from hypernets.hyperctl.utils import load_yaml
from hypernets.utils import logging

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
    def __init__(self, base_dir, exec_file: str, env: PythonEnv, tasks=None, random=True):
        self.base_dir = base_dir
        self.base_dir_path = Path(base_dir)

        self.env: PythonEnv = env
        self.exec_file = exec_file
        self.tasks = tasks  # default is None, mean support all task type
        self.random = random

        assert self.abs_exec_file_path().exists(), "exec_file not exists"

    @property
    def name(self):
        return Path(self.base_dir).name

    def abs_exec_file_path(self):
        return self.base_dir_path / self.exec_file


class JobParams:
    def __init__(self, bm_task_id, task_config_id,  random_state,  max_trials=None,
                 reward_metric=None, dataset_cache_path=None, **kwargs):
        self.bm_task_id = bm_task_id
        self.task_config_id = task_config_id
        self.random_state = random_state
        self.max_trials = max_trials
        self.reward_metric = reward_metric
        self.dataset_cache_path = dataset_cache_path

    def to_dict(self):
        return self.__dict__


def load_player(player_dir):

    player_dir_path = Path(player_dir)

    def read_env_name_from_conda_yaml(conda_yaml_file_name):
        conda_yaml_file_path = player_dir_path / conda_yaml_file_name
        conda_yaml_dict = load_yaml(conda_yaml_file_path.as_posix())
        return conda_yaml_dict['name']

    config_file = Path(player_dir) / "player.yaml"
    if not config_file.exists():
        raise FileNotFoundError(config_file)

    assert config_file.exists()
    play_dict = load_yaml(config_file)

    play_dict['exec_file'] = "exec.py"

    env_dict = play_dict['env']

    env_venv_dict = env_dict.get('venv')
    env_mgr_kind = env_venv_dict['kind']
    env_mgr_config = env_venv_dict.get('config', {})

    player_name = player_dir_path.name
    if env_mgr_kind == PythonEnv.KIND_CONDA:
        requirements_dict = env_dict.get('requirements')
        requirements_kind = requirements_dict['kind']
        requirements_config = requirements_dict.get('config', {})
        if requirements_kind == PythonEnv.REQUIREMENTS_CONDA_YAML:
            # set env name
            configured_env_name = env_mgr_config.get('name')
            if configured_env_name is not None:
                logger.warning(f"you have configured env name {configured_env_name} will be"
                            f" instead of by the name from conda yaml file.")
            env_mgr_config['name'] = read_env_name_from_conda_yaml(requirements_config.get('file_name', "env.yaml"))
            reqs_config = ReqsCondaYamlConfig(**requirements_config)
        elif requirements_kind == PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT:
            env_mgr_config['name'] = env_mgr_config.get('name', f'tbs-{player_name}')  # set default env name
            requirements_config['py_version'] = str(requirements_config['py_version'])
            reqs_config = ReqsRequirementsTxtConfig(**requirements_config)
        else:
            raise Exception(f"Unsupported env manager {env_mgr_kind}")

        mgr_config = CondaVenvMRGConfig(**env_mgr_config)

    elif env_mgr_kind == PythonEnv.KIND_CUSTOM_PYTHON:
        env_mgr_config['py_executable'] = env_mgr_config.get('py_executable', sys.executable)
        mgr_config = CustomPyMRGConfig(**env_mgr_config)
        reqs_config = None
    else:
        raise Exception(f"Unsupported env manager {env_mgr_kind}")

    play_dict['env'] = PythonEnv(venv=mgr_config, requirements=reqs_config)
    play_dict['base_dir'] = Path(player_dir).absolute().as_posix()
    return Player(**play_dict)
