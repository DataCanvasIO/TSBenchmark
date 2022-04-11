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
from tsbenchmark.players import Player, load_players
from tsbenchmark.server import BenchmarkBatchApplication

logging.set_level('DEBUG')

logger = logging.getLogger(__name__)

SRC_DIR = os.path.dirname(__file__)


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

    def setup(self):
        for player in self.players:
            self.setup_player(player)

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

    @abc.abstractmethod
    def create_batch_app(self, batch) -> BatchApplication:
        raise NotImplemented

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

        batch_app = self.create_batch_app(batch)
        batch_app.start()


class LocalBenchmark(BenchmarkBaseOnHyperctl):

    def create_batch_app(self, batch):
        batch_app = BenchmarkBatchApplication(batch, scheduler_exit_on_finish=True)
        return batch_app

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


class RemoteSSHBenchmark(BenchmarkBaseOnHyperctl):
    def __init__(self, name, desc, players, tasks, constraints, machines):
        super(RemoteSSHBenchmark, self).__init__(name, desc, players, tasks, constraints)
        self.machines = machines

    def create_batch_app(self, batch):
        backend_conf = {
            'machines': self.machines
        }
        batch_app = BenchmarkBatchApplication(batch, backend_type='remote', backend_conf=backend_conf, scheduler_exit_on_finish=True)
        return batch_app

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
