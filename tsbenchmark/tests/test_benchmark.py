import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict

import pytest

import tsbenchmark.tasks
from hypernets.hyperctl.appliation import BatchApplication
from hypernets.hyperctl.batch import ShellJob
from hypernets.tests.hyperctl.test_scheduler import assert_batch_finished
from hypernets.tests.utils import ssh_utils_test
from hypernets.utils import ssh_utils
from hypernets.utils.common import generate_short_id
from tsbenchmark.benchmark import LocalBenchmark, RemoteSSHBenchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.cfg import _load_players
from tsbenchmark.players import load_player
from tsbenchmark.tests.players import load_test_player

PWD = Path(__file__).parent


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

need_private_pypi = pytest.mark.skipif(os.getenv("TSB_PYPI") is None,
                                       reason='The test case need a private pypi to install requirements"')

need_server_host = pytest.mark.skipif(os.getenv("TSB_SERVER_HOST") is None,
                                      reason='The test case need to set env "TSB_SERVER_HOST"')


def create_univariate_task():
    task_config = tsbenchmark.tasks.get_task_config(694826)
    return task_config


def create_multivariable_task():
    task_config = tsbenchmark.tasks.get_task_config(890686)
    return task_config


def load_player_with_random_env_name(env_name):
    player = load_test_player(env_name)
    player.env.venv.name = generate_short_id()
    return player


DEFAULT_RANDOM_STATE = 8086


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


def assert_bm_batch_succeed(lb):
    # assert does not upload any assets
    batch_app: BatchApplication = lb.batch_app
    for job in batch_app.batch.jobs:
        job: ShellJob = job
        assert not job.resources_path.exists()

    # assert batch succeed
    assert_batch_finished(batch_app.batch, ShellJob.STATUS_SUCCEED)


class BaseTestBenchmark:

    benchmark = None

    @classmethod
    def setup_class(cls):
        # clear ioloop
        asyncio.set_event_loop(asyncio.new_event_loop())

    @classmethod
    def teardown_class(cls):
        if cls.benchmark is not None:
            cls.benchmark.stop()
        # release resources
        asyncio.get_event_loop().stop()
        asyncio.get_event_loop().close()


class TestLocalCustomPythonTestBenchmark(BaseTestBenchmark):
    """Benchmark with constraints:
        - local benchmark
        - custom python
    """
    benchmark = None

    @classmethod
    def setup_class(cls):
        super(TestLocalCustomPythonTestBenchmark, cls).setup_class()

        # define players
        player = load_test_player('plain_player')
        task0 = create_univariate_task()

        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")

        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[player],
                            random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=[task0],
                            batch_app_init_kwargs=dict(scheduler_exit_on_finish=True, server_port=8060),
                            working_dir=batches_data_dir,
                            task_constraints={}, callbacks=callbacks)
        cls.benchmark = lb

    def test_run(self):
        self.benchmark.run()
        assert_bm_batch_succeed(self.benchmark)


class TestPlayerFilterTask(BaseTestBenchmark):

    @classmethod
    def setup_class(cls):
        super(TestPlayerFilterTask, cls).setup_class()

        # define players
        player = load_test_player('plain_player_univariate')

        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        tasks = [create_univariate_task(), create_multivariable_task()]

        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[player],
                            random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=tasks,
                            batch_app_init_kwargs=dict(scheduler_exit_on_finish=True, server_port=8060),
                            working_dir=batches_data_dir, callbacks=callbacks)
        cls.benchmark = lb

    def test_filter_task(self):
        self.benchmark.run()
        assert_bm_batch_succeed(self.benchmark)
        tasks = self.benchmark.tasks()
        assert len(tasks) == 1
        bm_task = tasks[0]
        # is multivariable task
        assert bm_task.ts_task.id == create_univariate_task().id


class TestNonRandomPlayer(BaseTestBenchmark):

    @classmethod
    def setup_class(cls):
        super(TestNonRandomPlayer, cls).setup_class()

        # define players
        non_random_player = load_test_player('non_random_player_univariate')
        plain_player = load_test_player('plain_player')

        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        tasks = [create_univariate_task()]

        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[non_random_player, plain_player],
                            random_states=[DEFAULT_RANDOM_STATE, 8087], ts_tasks_config=tasks,
                            batch_app_init_kwargs=dict(scheduler_exit_on_finish=True, server_port=8060),
                            working_dir=batches_data_dir, callbacks=callbacks)
        cls.benchmark = lb

    def test_no_random_player(self):
        self.benchmark.run()
        assert_bm_batch_succeed(self.benchmark)
        tasks = self.benchmark.tasks()
        assert len(tasks) == 3
        ts_task = tasks[0].ts_task
        assert ts_task.random_state is None


class TestRunBasePreviousBatchRemoteCustomPythonTest(BaseTestBenchmark):

    bc2 = None

    @classmethod
    def setup_class(cls):
        super(TestRunBasePreviousBatchRemoteCustomPythonTest, cls).setup_class()

        base_bc = cls.create_local_benchmark(8060)
        base_bc.run()
        base_bc._batch_app.stop()
        cls.base_bc = base_bc

        bc2 = cls.create_local_benchmark(8060)
        cls.bc2 = bc2

    @classmethod
    def create_local_benchmark(cls, port):
        player = load_test_player("plain_player")
        task0 = create_univariate_task()

        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[player],
                            random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=[task0],
                            working_dir=batches_data_dir,
                            batch_app_init_kwargs=dict(scheduler_interval=1, scheduler_exit_on_finish=True,
                                                       server_port=port),
                            task_constraints={}, callbacks=callbacks)
        return lb

    def test_run_base_previous_batch(self):
        bc2 = self.bc2
        bc2.run()
        ba1 = self.base_bc._batch_app.batch
        ba2 = bc2._batch_app.batch

        assert ba1.name == ba2.name
        assert len(ba1.jobs) == len(ba2.jobs)
        assert set([_.name for _ in ba1.jobs]) == set([_.name for _ in ba2.jobs])

    @classmethod
    def teardown_class(cls):
        cls.bc2._batch_app._http_server.stop()
        super(TestRunBasePreviousBatchRemoteCustomPythonTest, cls).teardown_class()


@ssh_utils_test.need_psw_auth_ssh
@need_server_host
class TestRemoteCustomPythonTestBenchmark(BaseTestBenchmark):
    """
    Benchmark with constraints:
        - remote benchmark
        - custom python

    Requirements in custom_python:
        - hypernets
        - tsbenchmark
    """
    @classmethod
    def setup_class(cls):
        # clear ioloop
        super(TestRemoteCustomPythonTestBenchmark, cls).setup_class()

        cls.connection = ssh_utils_test.load_ssh_psw_config()
        player = load_player((PWD / "players" / "plain_player_custom_python").as_posix())
        player.env.venv.py_executable = sys.executable
        task0 = create_univariate_task()
        callbacks = [ConsoleCallback()]
        cls.working_dir_path = Path(tempfile.mkdtemp(prefix="benchmark-test-batches"))
        cls.benchmark_name = 'remote-benchmark'

        lb = RemoteSSHBenchmark(name=cls.benchmark_name, desc='desc', players=[player],
                                random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=[task0],
                                working_dir=cls.working_dir_path.as_posix(),
                                batch_app_init_kwargs=dict(server_host=os.getenv('TSB_SERVER_HOST'),
                                                           server_port=8060,
                                                           scheduler_exit_on_finish=True),
                                task_constraints={}, callbacks=callbacks,
                                machines=[cls.connection])
        cls.benchmark = lb

    def test_run_benchmark(self):
        self.benchmark.run()

        # assert local files
        batch_path = self.working_dir_path / "batches" / self.benchmark_name
        assert batch_path.exists()
        batch_app: BatchApplication = self.benchmark._batch_app
        jobs = batch_app.batch.jobs
        assert len(jobs) == 1
        job = jobs[0]

        # batch succeed
        assert_batch_finished(batch_app.batch, ShellJob.STATUS_SUCCEED)

        # assert remote files
        job_working_dir_path = batch_path / job.name
        with ssh_utils.sftp_client(**self.connection) as client:
            # working dir
            assert ssh_utils.exists(client, job_working_dir_path.as_posix())
            # run_py.sh
            assert ssh_utils.exists(client, (job_working_dir_path / "resources" / "run_py.sh").as_posix())
            # player
            assert ssh_utils.exists(client, (job_working_dir_path / "resources" / "plain_player_custom_python" / "exec.py").as_posix())
            assert ssh_utils.exists(client, (job_working_dir_path / "resources" / "plain_player_custom_python" / "player.yaml").as_posix())


@need_private_pypi
@need_conda
@ssh_utils_test.need_psw_auth_ssh
class TestRemoteCondaReqsTxtPlayerTestBenchmark(BaseTestBenchmark):
    @classmethod
    def setup_class(cls):
        super(TestRemoteCondaReqsTxtPlayerTestBenchmark, cls).setup_class()

        # define players
        players = _load_players([(PWD / "players" / "plain_player_requirements_txt").as_posix()])
        task0 = create_univariate_task()

        callbacks = [ConsoleCallback()]
        machines = [ssh_utils_test.load_ssh_psw_config()]
        print(machines)
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        lb = RemoteSSHBenchmark(name='remote-benchmark', desc='desc', players=players,
                                random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=[task0],
                                working_dir=batches_data_dir,
                                batch_app_init_kwargs=dict(scheduler_interval=1,
                                                           scheduler_exit_on_finish=True,
                                                           server_host=os.getenv('TSB_SERVER_HOST'),  # external ip
                                                           server_port=8061),
                                conda_home=get_conda_home(),
                                task_constraints={}, callbacks=callbacks,
                                machines=machines)
        cls.benchmark = lb


@need_conda
class TestLocalCondaReqsTxtTestBenchmark(BaseTestBenchmark):
    def test_run_benchmark(self):

        # define players
        player = load_player_with_random_env_name('plain_player_requirements_txt')
        conda_home = get_conda_home()
        self.env_dir_path = Path(conda_home) / "envs" / player.env.venv.name
        if self.env_dir_path.exists():
            raise ValueError(f"Please remove the conda env {player.env.venv.name}")

        task0 = create_univariate_task()
        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[player],
                            random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=[task0],
                            working_dir=batches_data_dir,
                            batch_app_init_kwargs=dict(scheduler_interval=1, scheduler_exit_on_finish=True,
                                                       server_port=8063),
                            conda_home=get_conda_home(),
                            task_constraints={},
                            callbacks=callbacks)
        self.lb = lb

        self.lb.run()

        # asserts virtual env
        assert self.env_dir_path.exists()

        # bm batch succeed
        self.assert_bm_batch_succeed(self.lb)
        self.lb.stop()


@need_conda
@need_private_pypi
class TestLocalCondaReqsCondaYamlTestBenchmark(BaseTestBenchmark):
    def test_run_benchmark(self):
        # define players
        player = load_test_player('plain_player_conda_yaml')
        conda_home = get_conda_home()

        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        lb = LocalBenchmark(name='TestLocalCondaReqsCondaYamlBenchmark', desc='desc', players=[player],
                            random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=[create_univariate_task()],
                            working_dir=batches_data_dir,
                            batch_app_init_kwargs=dict(scheduler_interval=1, scheduler_exit_on_finish=True,
                                                       server_port=8063),
                            conda_home=get_conda_home(),
                            callbacks=callbacks)
        self.lb = lb

        self.lb.run()

        # asserts virtual env
        # assert self.env_dir_path.exists()

        # bm batch succeed
        self.assert_bm_batch_succeed(self.lb)
        self.lb.stop()


class TestRunBasePreviousBatchLocalCustomPythonTest(BaseTestBenchmark):

    bc2 = None

    @staticmethod
    def create_local_benchmark(port):
        player = load_test_player('plain_player_custom_python')
        player.env.venv.py_executable = sys.executable
        task0 = create_univariate_task()

        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[player],
                            random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=[task0],
                            working_dir=batches_data_dir,
                            batch_app_init_kwargs=dict(scheduler_interval=1,
                                                       scheduler_exit_on_finish=True,
                                                       server_port=port),
                            task_constraints={}, callbacks=callbacks)
        return lb

    @classmethod
    def setup_class(cls):
        super(TestRunBasePreviousBatchLocalCustomPythonTest, cls).setup_class()

        base_bc = cls.create_local_benchmark(8064)
        base_bc.run()
        base_bc._batch_app._http_server.stop()
        cls.base_bc = base_bc

        bc2 = cls.create_local_benchmark(8065)
        cls.bc2 = bc2

    def test_run_base_previous_batch(self):
        bc2 = self.bc2
        bc2.run()
        ba1 = self.base_bc._batch_app.batch
        ba2 = bc2._batch_app.batch

        assert ba1.name == ba2.name
        assert len(ba1.jobs) == len(ba2.jobs)
        assert set([_.name for _ in ba1.jobs]) == set([_.name for _ in ba2.jobs])

    @classmethod
    def teardown_class(cls):
        cls.bc2._batch_app._http_server.stop()
        super(TestRunBasePreviousBatchLocalCustomPythonTest, cls).teardown_class()


def test_2_tasks():
    asyncio.set_event_loop(asyncio.new_event_loop())

    player = load_test_player('plain_player_custom_python')
    t1 = tsbenchmark.tasks.get_task_config(694826)
    t2 = tsbenchmark.tasks.get_task_config(890686)
    tasks = [t1, t2]
    callbacks = [ConsoleCallback()]
    batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
    lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[player],
                        random_states=[8086], ts_tasks_config=tasks,
                        working_dir=batches_data_dir,
                        batch_app_init_kwargs=dict(scheduler_interval=1, scheduler_exit_on_finish=True,
                                                   server_port=8898),
                        task_constraints={}, callbacks=callbacks)
    lb.run()
    asyncio.get_event_loop().stop()  # release res
    asyncio.get_event_loop().close()
