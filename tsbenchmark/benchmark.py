import abc
import os
from pathlib import Path
import yaml, os
from typing import List

from hypernets.hyperctl.batch import ShellJob, Batch, BackendConf, ServerConf
from hypernets.hyperctl.appliation import BatchApplication

# from hypernets.hyperctl.scheduler import run_batch
from hypernets.hyperctl.callbacks import BatchCallback
from hypernets.hyperctl.server import create_hyperctl_handlers
from hypernets.hyperctl.utils import load_yaml
from hypernets.utils import logging
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.players import Player, load_players, JobParams, PythonEnv
from tsbenchmark.server import BenchmarkBatchApplication
import tsbenchmark.tasks
from tsbenchmark.tasks import TSTask, TSTaskConfig
from collections import Iterable
logging.set_level('DEBUG')

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


class EnvMGR:

    KIND_CONDA = 'conda'

    def __init__(self, kind, conda=None):
        self.kind = kind
        self.conda = conda

    @property
    def conda_home(self):
        if self.conda is not None:
            return self.conda.get('home')
        else:
            return None


class Benchmark(metaclass=abc.ABCMeta):

    def __init__(self, name, desc, players, ts_tasks_config: List[TSTaskConfig], random_states: List[int],
                 constraints, conda_home=None, working_dir=None, callbacks: List[BenchmarkCallback] = None):

        self.name = name
        self.desc = desc
        self.players: List[Player] = players
        self.ts_tasks_config = ts_tasks_config
        self.random_states = random_states
        self.constraints = constraints
        self.callbacks = callbacks if callbacks is not None else []

        if working_dir is None:
            self.working_dir = Path("~/tsbenchmark-working-dir").expanduser().absolute().as_posix()
        else:
            self.working_dir = Path(working_dir).absolute().as_posix()

        venvs = set([p.env.venv_kind for p in self.players])
        if conda_home is None:
            # check whether all players use custom_python
            if PythonEnv.KIND_CONDA in venvs:
                raise ValueError(f"'conda_home' can not be None because of some player using conda virtual env.")
        else:
            self.conda_home = conda_home


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

    def get_batches_data_dir(self):
        return (Path(self.working_dir) / "batches").as_posix()


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
        pass


class BenchmarkBaseOnHyperctl(Benchmark, metaclass=abc.ABCMeta):
    def __init__(self, scheduler_exit_on_finish=False,
                 scheduler_interval=5000, **kwargs):
        self.scheduler_exit_on_finish = scheduler_exit_on_finish
        self.scheduler_interval = scheduler_interval
        super(BenchmarkBaseOnHyperctl, self).__init__(**kwargs)

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

    def add_job(self, bm_task: BenchmarkTask, batch: Batch):
        task_id = bm_task.ts_task.id
        player: Player = bm_task.player
        random_state = bm_task.ts_task.random_state
        name = f'{player.name}_{task_id}_{random_state}'
        # TODO handle max_trials and reward_metric
        job_params = JobParams(bm_task_id=bm_task.id, task_config_id=task_id,
                               random_state=random_state, max_trails=3, reward_metric='rmse')

        # TODO support conda yaml
        # TODO support windows
        # if self.envmgr is not None:
        #     if self.envmgr.kind != EnvMGR.KIND_CONDA:
        #         raise ValueError(f"only {EnvMGR.KIND_CONDA} virtual env manager is supported currently.")

        working_dir_path = batch.data_dir_path() / name
        working_dir = working_dir_path.as_posix()

        if player.env.venv_kind == PythonEnv.KIND_CUSTOM_PYTHON:
            command = self.make_run_custom_pythonenv_command(bm_task, batch, name)
        elif player.env.venv_kind == PythonEnv.KIND_CONDA:
            if player.env.reqs_kind == PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT:
                command = self.make_run_requirements_requirements_txt_command(working_dir_path,
                                                                              player)  # TODO
            else:
                raise NotImplemented
        else:
            raise NotImplemented

        logger.info(f"command of job {name} is {command} ")

        batch.add_job(name=name,
                      params=job_params.to_dict(),
                      command=command,
                      output_dir=working_dir,
                      working_dir=working_dir,
                      assets=self.get_job_asserts(bm_task))

    def _handle_on_start(self):
        for callback in self.callbacks:
            callback.on_start(self)

    def _handle_on_finish(self):
        for callback in self.callbacks:
            callback.on_finish(self)

    def run(self):
        self._handle_on_start()  # callback start
        self._tasks = []
        players = self.players
        # create batch app
        batches_data_dir = self.get_batches_data_dir()

        # backend_conf = BackendConf(type = 'local', conf = {})
        from hypernets.utils import common
        batch_name = self.name
        batch: Batch = Batch(batch_name, batches_data_dir)
        for ts_task_config in self.ts_tasks_config:
            for player in players:
                for random_state in self.random_states:
                    ts_task = TSTask(ts_task_config, random_state, 3, 'rmse')   # TODO replace max_trials and reward metric
                    self._tasks.append(BenchmarkTask(ts_task, player))

        # generate Hyperctl Jobs
        for bm_task in self._tasks:
            self.add_job(bm_task, batch)

        self._batch_app = self.create_batch_app(batch)
        self._batch_app.start()

        self._handle_on_finish()  # FIXME if exit_on_finish=False

    def stop(self):
        self._batch_app.stop()

    def create_batch_app(self, batch) -> BatchApplication:
        if self.callbacks is not None and len(self.callbacks) > 0:
            scheduler_callbacks = [HyperctlBatchCallback(self)]
        else:
            scheduler_callbacks = None
        batch_app = BenchmarkBatchApplication(benchmark=self, batch=batch,
                                              scheduler_exit_on_finish=self.scheduler_exit_on_finish,
                                              scheduler_interval=self.scheduler_interval,
                                              scheduler_callbacks=scheduler_callbacks,
                                              backend_type=self.get_backend_type(),
                                              backend_conf=self.get_backend_conf())
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


class LocalBenchmark(BenchmarkBaseOnHyperctl):

    def get_backend_type(self):
        return 'local'

    def make_run_custom_pythonenv_command(self,  bm_task: BenchmarkTask, batch: Batch ,name):
        player_exec_file_path = bm_task.player.abs_exec_file_path()
        player_exec_file = player_exec_file_path.as_posix()

        custom_py_executable = bm_task.player.env.venv_config.py_executable
        command = f"/bin/sh -x {self.get_runpy_shell()}  --venv-kind={PythonEnv.KIND_CUSTOM_PYTHON} --custom-py-executable={custom_py_executable} --python-script={player_exec_file}"
        return command

    def make_run_requirements_requirements_txt_command(self, working_dir_path, player):
        local_requirements_txt_file = player.base_dir_path / player.env.requirements.file_name
        player_exec_file = player.abs_exec_file_path().as_posix()
        command = f"/bin/sh -x {self.get_runpy_shell()} --venv-kind={PythonEnv.KIND_CONDA}  --conda-home={self.conda_home} --venv-name={player.env.venv_config.name} --requirements-kind={PythonEnv.REQUIREMENTS_REQUIREMENTS_TXT} --requirements-txt-file={local_requirements_txt_file} --requirements-txt-py-version={player.env.requirements.py_version} --python-script={player_exec_file}"
        return command

    def get_runpy_shell(self):
        runpy_script = (HERE / "runpy.sh").absolute().as_posix()
        return runpy_script

    def get_job_asserts(self, bm_task: BenchmarkTask):
        return []

    def get_backend_conf(self):
        return {}


class RemoteSSHBenchmark(BenchmarkBaseOnHyperctl):
    def __init__(self, *args, **kwargs):
        machines = kwargs.pop("machines")
        super(RemoteSSHBenchmark, self).__init__(*args, **kwargs)
        self.machines = machines

    def get_backend_type(self):
        return 'remote'

    def get_backend_conf(self):
        return {
            'machines': self.machines
        }

    def make_run_requirements_requirements_txt_command(self, working_dir_path, player, player_exec_file):  # FIXME
        remote_requirements_txt_file = (working_dir_path / "resources" / player.env.requirements.file_name).as_posix()
        command = f"/bin/sh -x {self.get_runpy_shell()} --venv-kind=conda  --conda-home={self.conda_home} --venv-name={player.env.venv_config.name} --requirements-kind=requirements_txt --requirements-txt-file={remote_requirements_txt_file} --requirements-txt-py-version={player.env.requirements.py_version} --python-script={player_exec_file}"
        return command

    def get_runpy_shell(self):
        return "resources/runpy.sh"

    def get_job_asserts(self, bm_task: BenchmarkTask):
        run_py_shell = (HERE / "runpy.sh").absolute().as_posix()
        return [run_py_shell, bm_task.player.base_dir]

    def make_run_custom_pythonenv_command(self,  bm_task: BenchmarkTask, batch: Batch, name):
        player = bm_task.player
        working_dir_path = batch.data_dir_path() / name
        remote_player_exec_file = (working_dir_path / "resources" / player.name / player.exec_file).as_posix()
        custom_py_executable = bm_task.player.env.venv_config.py_executable
        command = f"/bin/sh -x {self.get_runpy_shell()}  --venv-kind={PythonEnv.KIND_CUSTOM_PYTHON} --custom-py-executable={custom_py_executable} --python-script={remote_player_exec_file}"
        return command


def load(config_file):
    config_dict = load_yaml(config_file)
    name = config_dict['name']
    desc = config_dict['desc']
    kind = config_dict.get('kind', 'local')  # benchmark kind

    # load players
    players_name_or_path = config_dict.get('players')
    players = load_players(players_name_or_path)

    # select tasks
    tasks_ids = config_dict.get('tasks')  # Optional
    task_filter = config_dict.get('task_filter')
    if tasks_ids is None:
        if task_filter is None:
            # select all tasks
            tasks = tsbenchmark.tasks.list_task_configs()  # TODO to ids
        else:
            # filter task
            tasks = tsbenchmark.tasks.list_task_configs(**task_filter)
    else:
        tasks = tasks_ids

    constraints = config_dict.get('constraints')
    report = config_dict['report']  # TODO add a callback

    if kind == 'local':
        benchmark = LocalBenchmark(name=name, desc=desc, players=players, tasks=tasks, constraints=constraints)
        return benchmark
    elif kind == 'remote':
        machines = config_dict['machines']
        benchmark = RemoteSSHBenchmark(name=name, desc=desc, players=players,
                                       ts_tasks=tasks, constraints=constraints, machines=machines)
        return benchmark
    else:
        raise RuntimeError(f"Unseen kind {kind}")
