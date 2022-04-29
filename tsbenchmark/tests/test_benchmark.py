import os
import tempfile
import sys
from typing import Dict
from pathlib import Path

import pytest

from hypernets.hyperctl.appliation import BatchApplication
from hypernets.hyperctl.batch import ShellJob
from hypernets.tests.hyperctl.test_scheduler import assert_batch_finished
from hypernets.utils import ssh_utils
from tsbenchmark.benchmark import LocalBenchmark, load_players, RemoteSSHBenchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.players import load_player
from tsbenchmark.tasks import TSTask
from hypernets.tests.utils import ssh_utils_test

import tsbenchmark.tasks

HERE = Path(__file__).parent


def get_conda_home():
    return os.getenv("TSB_CONDA_HOME")


def _conda_ready():
    conda_home = get_conda_home()
    if conda_home is not None:
        return Path(conda_home).exists()
    else:
        return False


# export TSB_CONDA_HOME=/opt/miniconda3
need_conda = pytest.mark.skipif(not _conda_ready(),
                                reason='The test case need conda to be installed and set env "TSB_CONDA_HOME"')

need_private_pypi = pytest.mark.skipif(not os.getenv("TSB_PYPI") is None,
                                       reason='The test case need a private pypi to install requirements"')


def create_task():
    task_config_id = 694826
    task_config = tsbenchmark.tasks.get_task_config(task_config_id)
    return task_config


class ConsoleCallback(BenchmarkCallback):

    def on_start(self, bm):
        print('on_start')

    def on_task_start(self, bm, bm_task):
        print('on_task_start')

    def on_task_finish(self, bm, bm_task, elapsed: float):
        print('on_task_finish')

    def on_task_message(self, bm, bm_task, message: Dict):
        # reward, reward_metric, hyperparams, elapsed
        print('on_task_message')

    def on_task_break(self, bm, bm_task, elapsed: float):
        print('on_task_break')

    def on_finish(self, bm):
        print('on_finish')


@ssh_utils_test.need_psw_auth_ssh
class TestRemoteCustomPythonBenchmark:
    """Benchmark with constraints:
        - remote benchmark
        - builtin players
        - custom python
    """

    def setup_class(self):
        self.connection = ssh_utils_test.load_ssh_psw_config()
        players = load_players([(HERE / "players" / "plain_player_custom_python").as_posix()])
        task0 = create_task()
        callbacks = [ConsoleCallback()]
        self.working_dir_path = Path(tempfile.mkdtemp(prefix="benchmark-test-batches"))
        self.benchmark_name = 'remote-benchmark'

        lb = RemoteSSHBenchmark(name=self.benchmark_name, desc='desc', players=players,
                                random_states=[8060], ts_tasks_config=[task0],
                                working_dir=self.working_dir_path.as_posix(),
                                scheduler_exit_on_finish=True,
                                constraints={}, callbacks=callbacks,
                                machines=[self.connection])
        self.lb = lb

    def test_run_benchmark(self):
        self.lb.run()

        # assert local files
        batch_path = self.working_dir_path / "batches" / self.benchmark_name
        assert batch_path.exists()
        batch_app: BatchApplication = self.lb._batch_app
        jobs = batch_app.batch.jobs
        assert len(jobs) == 1
        job = jobs[0]
        # job succeed
        assert (batch_path / f"{job.name}.succeed").exists()

        # assert remote files
        job_working_dir_path = batch_path / job.name
        with ssh_utils.sftp_client(**self.connection) as client:
            # working dir
            assert ssh_utils.exists(client, job_working_dir_path.as_posix())
            # runpy.sh
            assert ssh_utils.exists(client, (job_working_dir_path / "resources" / "runpy.sh").as_posix())
            # player
            assert ssh_utils.exists(client, (job_working_dir_path / "resources" / "plain_player_custom_python" / "exec.py").as_posix())
            assert ssh_utils.exists(client, (job_working_dir_path / "resources" / "plain_player_custom_python" / "player.yaml").as_posix())

    def teardown_class(self):
        self.lb.stop()


@need_private_pypi
@need_conda
@ssh_utils_test.need_psw_auth_ssh
class TestRemoteCondaReqsTxtPlayerBenchmark:
    def setup_class(self):
        # define players
        players = load_players([(HERE / "players" / "plain_player_requirements_txt").as_posix()])
        task0 = create_task()

        callbacks = [ConsoleCallback()]
        machines = [ssh_utils_test.load_ssh_psw_config()]
        print(machines)
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        lb = RemoteSSHBenchmark(name='remote-benchmark', desc='desc', players=players,
                                random_states=[8060], ts_tasks_config=[task0],
                                working_dir=batches_data_dir,
                                scheduler_exit_on_finish=True,
                                conda_home="~/miniconda3/",
                                constraints={}, callbacks=callbacks,
                                machines=machines
        self.lb = lb

    def test_run_benchmark(self):
        self.lb.run()


class TestRemoteCondaReqsTxtExternalPlayerBenchmark:

    def setup_class(self):
        pass

    def test_run_benchmark(self):
        pass


class BaseLocalBenchmark:

    def assert_bm_batch_succeed(self, lb):
        # assert does not upload any assets
        batch_app: BatchApplication = lb.batch_app
        for job in batch_app.batch.jobs:
            job: ShellJob = job
            assert not job.resources_path.exists()

        # assert batch succeed
        assert_batch_finished(batch_app.batch, ShellJob.STATUS_SUCCEED)


class TestLocalCustomPythonBenchmark(BaseLocalBenchmark):
    """Benchmark with constraints:
        - local benchmark
        - builtin players
        - custom python
    """

    def setup_class(self):
        # define players
        players = load_players(['plain_player'])
        task0 = create_task()

        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")

        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=players,
                            random_states=[8060], ts_tasks_config=[task0],
                            scheduler_exit_on_finish=True,
                            working_dir=batches_data_dir,
                            constraints={}, callbacks=callbacks)
        self.lb = lb

    def test_run(self):
        self.lb.run()
        self.assert_bm_batch_succeed(self.lb)

    def teardown_class(self):
        self.lb.stop()


@need_conda
@need_private_pypi
class TestLocalCondaReqsTxtBenchmark(BaseLocalBenchmark):
    def test_run_benchmark(self):
        # define players
        player = load_player((HERE / "players" / "plain_player_requirements_txt").as_posix())
        conda_home = get_conda_home()
        self.env_dir_path = Path(conda_home) / "envs" / player.env.venv_config.name
        if self.env_dir_path.exists():
            print("Please remove the conda env")

        task0 = create_task()
        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[player],
                            random_states=[8060], ts_tasks_config=[task0],
                            working_dir=batches_data_dir,
                            scheduler_exit_on_finish=True,
                            scheduler_interval=1,
                            conda_home=get_conda_home(),
                            constraints={},
                            callbacks=callbacks)
        self.lb = lb

        self.lb.run()

        # asserts virtual env
        assert self.env_dir_path.exists()

        # bm batch succeed
        self.assert_bm_batch_succeed(self.lb)
        self.lb.stop()


def create_local_benchmark():
    players = load_players(['plain_player'])
    task0 = create_task()

    callbacks = [ConsoleCallback()]
    batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
    lb = LocalBenchmark(name='local-benchmark', desc='desc', players=players,
                        random_states=[8060], ts_tasks_config=[task0],
                        working_dir=batches_data_dir,
                        scheduler_exit_on_finish=True,
                        scheduler_interval=1,
                        constraints={}, callbacks=callbacks)
    return lb


def test_run_base_previous_batch():
    bc1 = create_local_benchmark()
    bc1.run()
    bc1._batch_app._http_server.stop()

    bc2 = create_local_benchmark()
    bc2.run()
    bc2._batch_app._http_server.stop()

    ba1 = bc1._batch_app.batch
    ba2 = bc2._batch_app.batch

    assert ba1.name == ba2.name
    assert len(ba1.jobs) == len(ba2.jobs)
    assert set([_.name for _ in ba1.jobs]) == set([_.name for _ in ba2.jobs])
