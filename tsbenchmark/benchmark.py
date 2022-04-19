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
from tsbenchmark.players import Player, load_players, JobParams
from tsbenchmark.server import BenchmarkBatchApplication
import tsbenchmark.tasks
from tsbenchmark.tasks import TSTask, TSTaskConfig
from collections import Iterable
logging.set_level('DEBUG')

logger = logging.getLogger(__name__)

SRC_DIR = os.path.dirname(__file__)


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
                 constraints, callbacks: List[BenchmarkCallback] = None):
        self.name = name
        self.desc = desc
        self.players: List[Player] = players
        self.ts_tasks_config = ts_tasks_config
        self.random_states = random_states
        self.constraints = constraints
        self.callbacks = callbacks if callbacks is not None else []

        self._tasks = None

    def tasks(self):
        return self._tasks

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def setup_player(self, player: Player):
        pass

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

    def setup(self):
        for player in self.players:
            self.setup_player(player)

    def add_job(self, bm_task: BenchmarkTask, batch: Batch):
        task_id = bm_task.ts_task.id
        player = bm_task.player
        random_state = bm_task.ts_task.random_state
        name = f'{player.name}_{task_id}_{random_state}'
        # TODO handle max_trials and reward_metric
        job_params = JobParams(bm_task_id=bm_task.id, task_config_id=task_id, random_state=random_state, max_trails=3, reward_metric='rmse')

        command = f"{player.py_executable} {player.exec_file}"

        working_dir = (batch.data_dir_path() / name).absolute().as_posix()
        batch.add_job(name=name,
                      params=job_params.to_dict(),
                      command=command,
                      output_dir=working_dir,
                      working_dir=working_dir)

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
        batches_data_dir = Path("/tmp/tsbenchmark-hyperctl").expanduser().absolute().as_posix()  # TODO move config file

        # backend_conf = BackendConf(type = 'local', conf = {})
        from hypernets.utils import common
        batch_name = common.generate_short_id()  # TODO move to benchmark
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

        self._handle_on_finish()

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


class LocalBenchmark(BenchmarkBaseOnHyperctl):

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

    def get_backend_type(self):
        return 'local'

    def get_backend_conf(self):
        return {
        }


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
