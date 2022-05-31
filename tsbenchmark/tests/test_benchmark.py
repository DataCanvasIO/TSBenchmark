import asyncio
import os
import sys
from pathlib import Path

import pytest

import tsbenchmark.tasks
from hypernets.hyperctl.appliation import BatchApplication
from hypernets.hyperctl.batch import ShellJob
from hypernets.tests.hyperctl.test_scheduler import assert_batch_finished
from hypernets.tests.utils import ssh_utils_test
from hypernets.utils import ssh_utils
from hypernets.utils.common import generate_short_id
from tsbenchmark import consts
from tsbenchmark.benchmark import BenchmarkBaseOnHyperctl
from tsbenchmark.tests.benchmark_factory import create_local_benchmark, create_multivariable_task, \
    create_univariate_task, create_remote_benchmark
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


def get_server_host():
    return os.getenv("TSB_SERVER_HOST")


# e.g.: export TSB_CONDA_HOME=/opt/miniconda3
need_conda = pytest.mark.skipif(not _conda_ready(),
                                reason='The test case need conda to be installed and set env "TSB_CONDA_HOME"')

# e.g.: export TSB_SERVER_HOST=192.168.2.200
need_server_host = pytest.mark.skipif(get_server_host() is None,
                                      reason='The test case need to set env "TSB_SERVER_HOST"')
# e.g.: export TSB_PYPI=true
need_private_pypi = pytest.mark.skipif(os.getenv("TSB_PYPI") is None,
                                       reason='The test case need a private pypi created in ~/.pip/pip.conf to '
                                              'install requirements"')


def load_player_with_random_env_name(env_name):
    player = load_test_player(env_name)
    player.env.venv.name = generate_short_id()
    return player


DEFAULT_RANDOM_STATE = 8086


def assert_local_bm_batch_succeed(lb):
    # assert does not upload any assets
    batch_app: BatchApplication = lb.batch_app
    for job in batch_app.batch.jobs:
        job: ShellJob = job
        assert not job.resources_path.exists()

    # assert batch succeed
    assert_batch_finished(batch_app.batch, ShellJob.STATUS_SUCCEED)


def assert_remote_bm_batch_succeed(benchmark: BenchmarkBaseOnHyperctl, connection, asserts, job_index=0):
    batch_app: BatchApplication = benchmark.batch_app

    # assert local files
    batch_path = Path(benchmark.get_batch_working_dir())
    assert batch_path.exists()
    batch_app: BatchApplication = benchmark.batch_app

    job = batch_app.batch.jobs[job_index]

    # assert remote files
    job_working_dir_path = batch_path / job.name
    with ssh_utils.sftp_client(**connection) as client:
        # working dir
        assert ssh_utils.exists(client, job_working_dir_path.as_posix())
        for asset in asserts:
            assert ssh_utils.exists(client, (job_working_dir_path / "resources" / asset).as_posix())

    # assert batch succeed
    assert_batch_finished(batch_app.batch, ShellJob.STATUS_SUCCEED)


class BaseBenchmarkTest:

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


class TestLocalCustomPythonTestBenchmark(BaseBenchmarkTest):
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
        lb = create_local_benchmark(players=[player])

        cls.benchmark = lb

    def test_run(self):
        self.benchmark.run()
        assert_local_bm_batch_succeed(self.benchmark)


class TestPlayerFilterTask(BaseBenchmarkTest):

    @classmethod
    def setup_class(cls):
        super(TestPlayerFilterTask, cls).setup_class()

        # define players
        player = load_test_player('plain_player_univariate')
        tasks = [create_univariate_task(), create_multivariable_task()]
        lb = create_local_benchmark(players=[player], tasks=tasks)
        cls.benchmark = lb

    def test_filter_task(self):
        self.benchmark.run()
        assert_local_bm_batch_succeed(self.benchmark)
        tasks = self.benchmark.tasks()
        assert len(tasks) == 1
        bm_task = tasks[0]
        # is multivariable task
        assert bm_task.ts_task.id == create_univariate_task().id


class TestNonRandomPlayer(BaseBenchmarkTest):

    @classmethod
    def setup_class(cls):
        super(TestNonRandomPlayer, cls).setup_class()

        # define players
        non_random_player = load_test_player('non_random_player_univariate')
        plain_player = load_test_player('plain_player')

        tasks = [create_univariate_task()]

        lb = create_local_benchmark(players=[non_random_player, plain_player],
                                    tasks=tasks, random_states=[DEFAULT_RANDOM_STATE, 8087])
        cls.benchmark = lb

    def test_no_random_player(self):
        self.benchmark.run()
        assert_local_bm_batch_succeed(self.benchmark)
        tasks = self.benchmark.tasks()
        assert len(tasks) == 3
        ts_task = tasks[0].ts_task
        assert ts_task.random_state is None


class TestRunBasePreviousBatchRemoteCustomPythonTest(BaseBenchmarkTest):

    bc2 = None

    @classmethod
    def setup_class(cls):
        super(TestRunBasePreviousBatchRemoteCustomPythonTest, cls).setup_class()

        base_bc = create_local_benchmark()
        base_bc.run()
        base_bc._batch_app.stop()
        cls.base_bc = base_bc

        bc2 = create_local_benchmark()
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
        super(TestRunBasePreviousBatchRemoteCustomPythonTest, cls).teardown_class()


class TestRunBasePreviousBatchLocalCustomPythonTest(BaseBenchmarkTest):
    bc2 = None

    @classmethod
    def setup_class(cls):
        super(TestRunBasePreviousBatchLocalCustomPythonTest, cls).setup_class()

        base_bc = cls.create_local_benchmark(8064)
        base_bc.run()
        base_bc._batch_app._http_server.stop()
        cls.base_bc = base_bc

        bc2 = cls.create_local_benchmark(8065)
        cls.bc2 = bc2

    @staticmethod
    def create_local_benchmark(port):
        player = load_test_player('plain_player_custom_python')
        player.env.venv.py_executable = sys.executable

        return create_local_benchmark(players=[player])

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


class TestMultipleTasks(BaseBenchmarkTest):

    @classmethod
    def setup_class(cls):
        super(TestMultipleTasks, cls).setup_class()

        player = load_test_player('plain_player')
        tasks = [create_univariate_task(), create_multivariable_task()]

        lb = create_local_benchmark(players=[player], tasks=tasks)
        cls.benchmark = lb

    def test_2_tasks(self):
        self.benchmark.run()
        assert_local_bm_batch_succeed(self.benchmark)


@need_conda
@need_private_pypi
class TestLocalCondaReqsTxtTestBenchmark(BaseBenchmarkTest):
    @classmethod
    def setup_class(cls):
        super(TestLocalCondaReqsTxtTestBenchmark, cls).setup_class()
        # define players
        player = load_player_with_random_env_name('plain_player_requirements_txt')
        conda_home = get_conda_home()
        cls.env_dir_path = Path(conda_home) / "envs" / player.env.venv.name
        if cls.env_dir_path.exists():
            raise ValueError(f"Please remove the conda env {player.env.venv.name}")

        lb = create_local_benchmark(players=[player], conda_home=get_conda_home())
        cls.benchmark = lb

    def test_run_benchmark(self):
        self.benchmark.run()
        # asserts virtual env
        assert self.env_dir_path.exists()

        # bm batch succeed
        assert_local_bm_batch_succeed(self.benchmark)


@need_conda
@need_private_pypi
class TestLocalCondaReqsCondaYamlBenchmark(BaseBenchmarkTest):
    @classmethod
    def setup_class(cls):
        super(TestLocalCondaReqsCondaYamlBenchmark, cls).setup_class()
        # define players
        player = load_player_with_random_env_name('plain_player_conda_yaml')

        lb = create_local_benchmark(players=[player], conda_home=get_conda_home())
        cls.benchmark = lb

    def test_run_benchmark(self):
        self.benchmark.run()

        # asserts virtual env
        # assert self.env_dir_path.exists()
        # bm batch succeed
        assert_local_bm_batch_succeed(self.benchmark)


@ssh_utils_test.need_psw_auth_ssh
@need_server_host
class TestRemoteCustomPythonTestBenchmark(BaseBenchmarkTest):
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

        lb = create_remote_benchmark(machines=[{ 'connection': cls.connection } ], server_host=get_server_host())
        cls.benchmark = lb

    def test_run_benchmark(self):
        self.benchmark.run()

        # assert local files
        batch_path = Path(self.benchmark.get_batch_working_dir())
        assert batch_path.exists()
        batch_app: BatchApplication = self.benchmark.batch_app
        jobs = batch_app.batch.jobs
        assert len(jobs) == 1

        assets = ["run_py.sh", "plain_player_custom_python/exec.py", "plain_player_custom_python/player.yaml"]
        assert_remote_bm_batch_succeed(self.benchmark, self.connection, assets)


@need_conda
@ssh_utils_test.need_psw_auth_ssh
@need_server_host
@need_private_pypi
class TestRemoteCondaReqsTxtPlayerTestBenchmark(BaseBenchmarkTest):

    @classmethod
    def setup_class(cls):
        super(TestRemoteCondaReqsTxtPlayerTestBenchmark, cls).setup_class()
        # define players
        player = load_player_with_random_env_name("plain_player_requirements_txt")

        cls.connection = ssh_utils_test.load_ssh_psw_config()

        environments = {
            consts.ENV_TSB_CONDA_HOME: get_conda_home()
        }
        lb = create_remote_benchmark(players=[player],
                                     machines=[{'connection': cls.connection, 'environments': environments}],
                                     server_host=get_server_host())

        cls.benchmark = lb

    def test_run_benchmark(self):
        self.benchmark.run()

        jobs = self.benchmark.batch_app.batch.jobs
        assert len(jobs) == 1

        assets = ["run_py.sh", "plain_player_requirements_txt/exec.py", "plain_player_requirements_txt/player.yaml",
                  "plain_player_requirements_txt/requirements.txt"]
        assert_remote_bm_batch_succeed(self.benchmark, self.connection, assets)


@need_conda
@ssh_utils_test.need_psw_auth_ssh
@need_server_host
@need_private_pypi
class TestRemoteCondaReqsCondaYamlBenchmark(BaseBenchmarkTest):
    @classmethod
    def setup_class(cls):
        super(TestRemoteCondaReqsCondaYamlBenchmark, cls).setup_class()
        # define players
        player = load_player_with_random_env_name('plain_player_conda_yaml')

        cls.connection = ssh_utils_test.load_ssh_psw_config()
        environments = {
            consts.ENV_TSB_CONDA_HOME: get_conda_home()
        }
        lb = create_remote_benchmark(players=[player],
                                     machines=[{'connection': cls.connection, 'environments': environments}],
                                     server_host=get_server_host())
        cls.benchmark = lb
    
    def test_run_benchmark(self):
        self.benchmark.run()

        # assert self.env_dir_path.exists()

        jobs = self.benchmark.batch_app.batch.jobs
        assert len(jobs) == 1

        assets = ["run_py.sh", "plain_player_conda_yaml/exec.py",
                  "plain_player_conda_yaml/player.yaml", "plain_player_conda_yaml/env.yaml"]
        assert_remote_bm_batch_succeed(self.benchmark, self.connection, assets)
