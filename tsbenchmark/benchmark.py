import abc
import os
from pathlib import Path
from typing import List

from hypernets.hyperctl.appliation import BatchApplication
from hypernets.hyperctl.batch import ShellJob, Batch
from hypernets.hyperctl.callbacks import BatchCallback
from hypernets.utils import logging
from tsbenchmark import consts
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.consts import DEFAULT_WORKING_DIR
from tsbenchmark.players import Player, JobParams, PythonEnv
from tsbenchmark.server import BenchmarkBatchApplication
from tsbenchmark.tasks import TSTask, TSTaskConfig

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class BenchmarkTask:

    def __init__(self, ts_task: TSTask, player):
        self.player = player
        self.ts_task = ts_task

        self._status = None

    def status(self):
        return self._status

    @property
    def id(self):
        return f"{self.player.name}_{self.ts_task.id}_{self.ts_task.random_state}"


class Benchmark(metaclass=abc.ABCMeta):

    def __init__(self, name, desc, players, ts_tasks_config: List[TSTaskConfig], random_states: List[int],
                 task_constraints=None, working_dir=None, callbacks: List[BenchmarkCallback] = None):

        self.name = name
        self.desc = desc
        self.players: List[Player] = players
        self.ts_tasks_config = ts_tasks_config
        self.random_states = random_states
        # preset_task_constraints = {
        #     'max_trials': 10,
        #     'reward_metric': 'rmse'
        # }
        # user_task_constraints = {} if task_constraints is None else task_constraints
        # preset_task_constraints.update(user_task_constraints)
        # self.task_constraints = preset_task_constraints
        self.task_constraints = {} if task_constraints is None else task_constraints
        self.callbacks = callbacks if callbacks is not None else []

        if working_dir is None:
            self.working_dir = os.path.join(DEFAULT_WORKING_DIR, name)
        else:
            self.working_dir = Path(working_dir).absolute().as_posix()

        self._tasks = None

    def tasks(self):
        return self._tasks

    @abc.abstractmethod
    def run(self):
        pass

    def stop(self):
        pass

    def get_task(self, bm_task_id):
        if self._tasks is None:
            return None
        for bm_task in self._tasks:
            if bm_task.id == bm_task_id:
                return bm_task
        return None

    def find_task(self, player_name, random_state, task_config_id):
        for bm_task in self._tasks:
            bm_task: BenchmarkTask = bm_task
            if bm_task.ts_task.id == task_config_id and bm_task.ts_task.random_state == random_state\
                    and player_name == bm_task.player.name:
                return bm_task
        return None

    def get_batch_working_dir(self):
        return (Path(self.working_dir) / "batch").as_posix()


class HyperctlBatchCallback(BatchCallback):

    def __init__(self, bm: Benchmark):
        self.bm: Benchmark = bm

    def on_start(self, batch):
        pass

    def on_job_start(self, batch, job, executor):
        for bm_callback in self.bm.callbacks:
            # bm, bm_task
            bm_task = self.find_ts_task(job)  # TODO check None
            bm_callback.on_task_start(self.bm, bm_task)

    def find_ts_task(self, job):
        job: ShellJob = job
        job_params = JobParams(**job.params)

        random_state = job_params.random_state
        task_config_id = job_params.task_config_id
        for bm_task in self.bm.tasks():
            bm_task: BenchmarkTask = bm_task
            if bm_task.ts_task.id == task_config_id and bm_task.ts_task.random_state == random_state:
                return bm_task
        return None

    def on_job_finish(self, batch, job, executor, elapsed: float):
        for bm_callback in self.bm.callbacks:
            # bm, bm_task
            bm_task = self.find_ts_task(job)  # TODO check None
            bm_callback.on_task_finish(self.bm, bm_task, elapsed)

    def on_job_break(self, batch, job, executor, elapsed: float):  # TODO
        pass

    def on_finish(self, batch, elapsed: float):
        for callback in self.bm.callbacks:
            callback.on_finish(self)


class BenchmarkBaseOnHyperctl(Benchmark, metaclass=abc.ABCMeta):

    def __init__(self, *args,  **kwargs):
        self.batch_app_init_kwargs = kwargs.pop('batch_app_init_kwargs', {})  # use to init Hyperctl batch application
        super(BenchmarkBaseOnHyperctl, self).__init__(*args, **kwargs)

        self._batch_app = None

    @property
    def batch_app(self):
        return self._batch_app

    def make_run_conda_yaml_env_command(self):
        pass

    @abc.abstractmethod
    def make_run_custom_pythonenv_command(self, bm_task: BenchmarkTask, batch: Batch, name):
        raise NotImplemented

    @abc.abstractmethod
    def make_run_requirements_requirements_txt_command(self, working_dir_path, player):
        raise NotImplemented

    @abc.abstractmethod
    def make_run_requirements_conda_yaml_command(self, working_dir_path, player):
        raise NotImplemented

    def add_job(self, bm_task: BenchmarkTask, batch: Batch):
        task_id = bm_task.ts_task.id
        player: Player = bm_task.player
        random_state = bm_task.ts_task.random_state
        job_name = f'{player.name}_{task_id}_{random_state}'

        def safe_getattr(obj, attr_name):
            if hasattr(obj, attr_name):
                return getattr(obj, attr_name)
            else:
                return None

        job_params = JobParams(bm_task_id=bm_task.id, task_config_id=task_id,
                               random_state=random_state, max_trials=safe_getattr(bm_task.ts_task, 'max_trials'),
                               reward_metric=safe_getattr(bm_task.ts_task, 'reward_metric'))

        # TODO support windows
        job_working_dir_path = batch.working_dir_path / job_name
        working_dir = job_working_dir_path.as_posix()
        venv_kind = player.env.venv_kind
        if player.env.venv_kind == PythonEnv.KIND_CUSTOM_PYTHON:
            command = self.make_run_custom_pythonenv_command(bm_task, batch, job_name)
        elif player.env.venv_kind == PythonEnv.KIND_CONDA:
            if player.env.reqs_kind == PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT:
                command = self.make_run_requirements_requirements_txt_command(job_working_dir_path, player)
            else:
                command = self.make_run_requirements_conda_yaml_command(job_working_dir_path, player)
        else:
            raise ValueError(f"unseen venv kind {venv_kind}")

        merged_command = f"{self.get_command_prefix()} {command} " \
                         f"{self.get_exec_py_args(job_working_dir_path, player)} {self.get_datasets_cache_path_args()}" \
                         f"  --python-path={os.getcwd()}"

        logger.info(f"command of job {job_name} is {merged_command}")

        batch.add_job(name=job_name,
                      params=job_params.to_dict(),
                      command=merged_command,
                      output_dir=working_dir,
                      working_dir=working_dir,
                      assets=self.get_job_asserts(bm_task))

    def _handle_on_start(self):
        for callback in self.callbacks:
            callback.on_start(self)

    def _create_tasks(self, ts_task_config):
        for player in self.players:
            player: Player = player
            if player.tasks is not None:
                # check the player whether support the task type
                if ts_task_config.task not in player.tasks:
                    skip_msg = f"skip {ts_task_config.id} for {player.name} because of not supported this task type."
                    logger.debug(skip_msg)
                    continue
            if player.random is True:
                for random_state in self.random_states:
                    ts_task = TSTask(ts_task_config, random_state=random_state, **self.task_constraints)
                    self._tasks.append(BenchmarkTask(ts_task, player))
            else:
                ts_task = TSTask(ts_task_config, random_state=None, **self.task_constraints)
                self._tasks.append(BenchmarkTask(ts_task, player))

    @staticmethod
    def get_datasets_cache_path_args():
        datasets_cache_path = os.environ.get(consts.ENV_DATASETS_CACHE_PATH)
        if datasets_cache_path is not None:
            return f"--datasets-cache-path={datasets_cache_path}"
        else:
            return ""

    def run(self):
        self._handle_on_start()  # callback start
        self._tasks = []

        logger.info(f"benchmark name: {self.name}")
        logger.info(f"benchmark working dir: {self.working_dir}")

        # create batch app
        batch_name = self.name
        batch: Batch = Batch(batch_name, self.get_batch_working_dir())
        for ts_task_config in self.ts_tasks_config:
            self._create_tasks(ts_task_config)

        # generate Hyperctl Jobs
        for bm_task in self._tasks:
            self.add_job(bm_task, batch)

        self._batch_app = self.create_batch_app(batch)
        self._batch_app.start()

    def stop(self):
        self._batch_app.stop()

    def create_batch_app(self, batch) -> BatchApplication:
        if self.callbacks is not None and len(self.callbacks) > 0:
            scheduler_callbacks = [HyperctlBatchCallback(self)]
        else:
            scheduler_callbacks = None
        init_dict = dict(benchmark=self, batch=batch, scheduler_callbacks=scheduler_callbacks,
                         backend_type=self.get_backend_type(), backend_conf=self.get_backend_conf())
        copy_dict = self.batch_app_init_kwargs.copy()
        copy_dict.update(init_dict)

        batch_app = BenchmarkBatchApplication(**copy_dict)
        return batch_app

    @abc.abstractmethod
    def get_backend_type(self):
        raise NotImplemented

    @abc.abstractmethod
    def get_backend_conf(self):
        raise NotImplemented

    @abc.abstractmethod
    def get_job_asserts(self,  bm_task: BenchmarkTask):
        raise NotImplemented

    @abc.abstractmethod
    def get_command_prefix(self):
        raise NotImplemented

    @abc.abstractmethod
    def get_exec_py_args(self, working_dir_path, player):
        raise NotImplemented


class LocalBenchmark(BenchmarkBaseOnHyperctl):

    def __init__(self, *args, **kwargs):
        if "conda_home" in kwargs:
            self.conda_home = kwargs.pop("conda_home")
        else:
            self.conda_home = None

        super(LocalBenchmark, self).__init__(*args, **kwargs)

        # check whether all players use custom_python
        venvs = set([p.env.venv_kind for p in self.players])
        if PythonEnv.KIND_CONDA in venvs and self.conda_home is None:
            raise ValueError(f"'conda_home' can not be None because of some player using conda virtual env.")

    def get_backend_type(self):
        return 'local'

    def get_backend_conf(self):
        if self.conda_home is not None:
            return {'environments': {consts.ENV_TSB_CONDA_HOME: self.conda_home}}
        else:
            return {}

    def make_run_custom_pythonenv_command(self,  bm_task: BenchmarkTask, batch: Batch, name):
        custom_py_executable = bm_task.player.env.venv.py_executable
        command = f"--venv-kind={PythonEnv.KIND_CUSTOM_PYTHON} --custom-py-executable={custom_py_executable}"
        return command

    def make_run_requirements_requirements_txt_command(self, working_dir_path, player):
        local_requirements_txt_file = player.base_dir_path / player.env.requirements.file_name
        command = f"--venv-kind={PythonEnv.KIND_CONDA} " \
                  f"--venv-name={player.env.venv.name} " \
                  f"--requirements-kind={PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT} " \
                  f"--requirements-txt-file={local_requirements_txt_file} " \
                  f"--requirements-txt-py-version={player.env.requirements.py_version}"
        return command

    def make_run_requirements_conda_yaml_command(self, working_dir_path, player):
        local_requirements_txt_file = player.base_dir_path / player.env.requirements.file_name
        command = f"--venv-kind={PythonEnv.KIND_CONDA} " \
                  f"--venv-name={player.env.venv.name} " \
                  f"--requirements-kind={PythonEnv.REQUIREMENTS_CONDA_YAML} " \
                  f"--requirements-yaml-file={local_requirements_txt_file}"
        return command

    def get_command_prefix(self):
        run_py_script = (HERE / "run_py.sh").absolute().as_posix()
        return f"/bin/bash -x {run_py_script}"

    def get_exec_py_args(self, working_dir_path, player):
        player_exec_file = player.abs_exec_file_path().as_posix()
        return f"--python-script={player_exec_file}"

    def get_job_asserts(self, bm_task: BenchmarkTask):
        return []


class RemoteSSHBenchmark(BenchmarkBaseOnHyperctl):

    def __init__(self, *args, **kwargs):
        if "machines" in kwargs:
            self.machines = kwargs.pop("machines")
        else:
            raise ValueError("missing args 'machines' ")

        super(RemoteSSHBenchmark, self).__init__(*args, **kwargs)

        # check whether all players use custom_python
        venvs = set([p.env.venv_kind for p in self.players])
        if PythonEnv.KIND_CONDA in venvs:
            for machine in self.machines:
                if machine.get('environments', {}).get(consts.ENV_TSB_CONDA_HOME) is None:
                    raise ValueError(f"'conda_home' in machines can not be None"
                                     f" because of some player using conda virtual env.")

    def get_backend_type(self):
        return 'remote'

    def get_backend_conf(self):
        return {
            'machines': self.machines
        }

    def make_run_requirements_requirements_txt_command(self, working_dir_path, player):
        remote_requirements_txt_file = (working_dir_path / "resources" / player.name / player.env.requirements.file_name).as_posix()
        command = f"--venv-kind=conda --venv-name={player.env.venv.name} " \
                  f"--requirements-kind={PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT} " \
                  f"--requirements-txt-file={remote_requirements_txt_file} " \
                  f"--requirements-txt-py-version={player.env.requirements.py_version}"
        return command

    def get_job_asserts(self, bm_task: BenchmarkTask):
        run_py_shell = (HERE / "run_py.sh").absolute().as_posix()
        return [run_py_shell, bm_task.player.base_dir]

    def make_run_custom_pythonenv_command(self,  bm_task: BenchmarkTask, batch: Batch, name):
        custom_py_executable = bm_task.player.env.venv.py_executable
        command = f"--venv-kind={PythonEnv.KIND_CUSTOM_PYTHON} --custom-py-executable={custom_py_executable}"
        return command

    def make_run_requirements_conda_yaml_command(self, working_dir_path, player):
        conda_yaml_file = (working_dir_path / "resources" / player.name / player.env.requirements.file_name).as_posix()
        command = f"--venv-kind={PythonEnv.KIND_CONDA} " \
                  f"--venv-name={player.env.venv.name} --requirements-kind={PythonEnv.REQUIREMENTS_CONDA_YAML} " \
                  f"--requirements-yaml-file={conda_yaml_file}"
        return command

    def get_command_prefix(self):
        return f"/bin/bash -x  resources/run_py.sh"

    def get_exec_py_args(self, working_dir_path, player):
        remote_player_exec_file = (working_dir_path / "resources" / player.name / player.exec_file).as_posix()
        return f"--python-script={remote_player_exec_file}"
