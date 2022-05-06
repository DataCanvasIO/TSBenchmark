from tsbenchmark.tasks import TSTask
from tsbenchmark.reporter import Reporter
from hypernets.utils import logging

import os
import tempfile
from typing import Dict
from pathlib import Path

import pytest

from hypernets.hyperctl.appliation import BatchApplication

from hypernets.utils import ssh_utils
from tsbenchmark.benchmark import LocalBenchmark, load_players, RemoteSSHBenchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.tasks import TSTask
from hypernets.tests.utils import ssh_utils_test

logging.set_level('DEBUG')  # TODO
logger = logging.getLogger(__name__)

import tsbenchmark.tasks

HERE = Path(__file__).parent


def create_tasks_new():
    tasks = [TSTask(tsbenchmark.tasks.get_task_config(t_id), random_state=8086, max_trails=1, reward_metric='rmse') for
             t_id in [694826, 309496]]
    return tasks


def create_benchmark_local_cfg():
    benchmark_config = {'report.path': r'D:\文档\0 DAT\3 Benchmark\benchmark-output\hyperts',
                        'name': 'report_local_1',
                        'desc': 'report_local_1',
                        'random_states': [8086],
                        'task_filter.tasks': ['univariate-forecast']
                        }
    return benchmark_config


def create_benchmark_remote_cfg():
    benchmark_config = {'report.path': '/tmp/report_path',
                        'name': 'report_remote',
                        'desc': 'report_remote',
                        'random_states': [8086],
                        'task_filter.tasks': ['univariate-forecast']
                        }
    return benchmark_config


class ReporterCallback(BenchmarkCallback):
    def __init__(self, benchmark_config):
        self.reporter = Reporter(benchmark_config)

    def on_start(self, bm):
        print('on_start')

    def on_task_start(self, bm, bm_task):
        print('on_task_start')

    def on_task_finish(self, bm, bm_task, elapsed: float):
        print('on_task_finish')

    def on_task_message(self, bm, bm_task, message: Dict):
        self.reporter.save_results(message, bm_task)
        print('on_task_message')

    def on_task_break(self, bm, bm_task, elapsed: float):
        print('on_task_break')

    def on_finish(self, bm):
        self.reporter.generate_report()
        print('on_finish')


def atest_benchmark_reporter():
    # define players
    players = load_players([(HERE / "players" / "am_pyaf_player").as_posix()])
    task_list = [TSTask(tsbenchmark.tasks.get_task_config(t_id), random_state=8086, max_trails=1, reward_metric='rmse')
                 for
                 t_id in [694826, 309496]]

    # Mock data for benchmark_config
    benchmark_config = create_benchmark_remote_cfg()
    callbacks = [ReporterCallback(benchmark_config=benchmark_config)]

    lb = LocalBenchmark(name=benchmark_config['name'], desc=benchmark_config['desc'], players=players,
                        random_states=benchmark_config['random_states'], ts_tasks_config=task_list,
                        scheduler_exit_on_finish=True,
                        constraints={}, callbacks=callbacks)
    lb.run()


def atest_reporter_generate():
    benchmark_config = create_benchmark_local_cfg()
    rc = ReporterCallback(benchmark_config=benchmark_config)
    rc.reporter.generate_report()


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


def create_task():
    task_config_id = 694826
    task_config = tsbenchmark.tasks.get_task_config(task_config_id)
    return task_config


@ssh_utils_test.need_psw_auth_ssh
@need_server_host
class TestRemoteCustomPythonBenchmark:
    """Benchmark with constraints:
        - remote benchmark
        - custom python
    """

    def setup_class(self):
        self.connection = ssh_utils_test.load_ssh_psw_config()
        players = load_players([(HERE / "players" / "hyperts_stat_player").as_posix(),
                                (HERE / "players" / "hyperts_dl_player").as_posix()])
        task0 = create_task()
        benchmark_config = create_benchmark_remote_cfg()
        rc = ReporterCallback(benchmark_config=benchmark_config)
        callbacks = [rc]
        self.working_dir_path = Path(tempfile.mkdtemp(prefix="benchmark-test-batches"))
        self.benchmark_name = 'remote-benchmark'

        lb = RemoteSSHBenchmark(name=self.benchmark_name, desc='desc', players=players,
                                random_states=[8086], ts_tasks_config=[task0],
                                working_dir=self.working_dir_path.as_posix(),
                                scheduler_exit_on_finish=True,
                                server_host=os.getenv('TSB_SERVER_HOST'),  # external ip
                                constraints={}, callbacks=callbacks,
                                machines=[self.connection])
        self.lb = lb

    def atest_run_benchmark(self):
        self.lb.run()

        # assert local files
        batch_path = self.working_dir_path / "batches" / self.benchmark_name
        assert batch_path.exists()
        batch_app: BatchApplication = self.lb._batch_app
        jobs = batch_app.batch.jobs
        assert len(jobs) == 2
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

    def teardown_class(self):
        self.lb.stop()
