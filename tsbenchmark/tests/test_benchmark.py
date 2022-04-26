import tempfile
from typing import Dict
from pathlib import Path

from tsbenchmark.benchmark import LocalBenchmark, load_players, RemoteSSHBenchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.datasets import TSDataset
from tsbenchmark.tasks import TSTask, TSTaskConfig
from hypernets.tests.utils import ssh_utils_test

import tsbenchmark.tasks

HERE = Path(__file__).parent


class NetworkTrafficMockDataset(TSDataset):
    """Test dataset"""

    def __init__(self):
        super(NetworkTrafficMockDataset, self).__init__(0, 'network_traffic', None)

    def get_train(self):
        from hyperts.datasets.base import load_network_traffic
        df = load_network_traffic()
        return df

    def get_test(self):
        return self.get_train()

    def get_data(self):
        return self.get_train(), self.get_test()


def create_task():
    dataset = NetworkTrafficMockDataset()

    config = TSTaskConfig(taskconfig_id=0, dataset_id=0, taskdata=dataset, date_name='TimeStamp', task='multivariate-forecast',
                          horizon=7, series_name='Var_1',
                          covariables_name=['HourSin', 'WeekCos', 'CBWD'], dtformat='%Y-%m-%d')
    # t = TSTask(task_config=config, random_state=8086, max_trails=3, reward_metric='rmse')
    # setattr(t, 'id', 0)  # TODO remove
    # return t
    return config


def create_task_new(task_config_id):
    task_config = tsbenchmark.tasks.get_task_config(task_config_id)

    task = TSTask(task_config, random_state=8086, max_trails=5, reward_metric='rmse')
    assert task.task == 'univariate-forecast' and task.dataset_id == 694826
    assert task.get_train().shape[0] == 124 and task.get_test().shape[0] == 6
    assert task.random_state == 8086
    return task


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


class TestLocalBenchmark:

    def setup_class(self):
        # define players
        players = load_players(['plain_player'])
        task_config_id = 694826
        task0 = create_task_new(task_config_id)

        callbacks = [ConsoleCallback()]
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        custom_py_executable = '~/miniconda3/envs/ts-plain_player_requirements_txt/bin/python'
        lb = LocalBenchmark(name='local-benchmark', desc='desc', players=players,
                            random_states=[8060], ts_tasks_config=[task0],
                            custom_py_executable=custom_py_executable,
                            scheduler_exit_on_finish=True,
                            working_dir=batches_data_dir,
                            constraints={}, callbacks=callbacks)
        self.lb = lb

    def test_run(self):
        self.lb.run()

    def teardown_class(self):
        self.lb.stop()


@ssh_utils_test.need_psw_auth_ssh
def test_remote_benchmark():
    # define players
    players = load_players(['plain_player'])
    task_config_id = 694826
    task0 = create_task_new(task_config_id)

    callbacks = [ConsoleCallback()]
    machines = [ssh_utils_test.load_ssh_psw_config()]
    print(machines)
    lb = RemoteSSHBenchmark(name='remote-benchmark', desc='desc', players=players,
                            random_states=[8060], ts_tasks_config=[task0],
                            scheduler_exit_on_finish=True,
                            constraints={}, callbacks=callbacks,
                            machines=machines)
    lb.run()


@ssh_utils_test.need_psw_auth_ssh
class TestRemoteBenchmark:

    def setup_class(self):
        # define players
        players = load_players([(HERE / "players" / "plain_player_requirements_txt").as_posix()])
        task_config_id = 694826
        task0 = create_task_new(task_config_id)

        callbacks = [ConsoleCallback()]
        machines = [ssh_utils_test.load_ssh_psw_config()]
        print(machines)
        batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
        lb = RemoteSSHBenchmark(name='remote-benchmark', desc='desc', players=players,
                                random_states=[8060], ts_tasks_config=[task0],
                                working_dir=batches_data_dir,
                                scheduler_exit_on_finish=True,
                                constraints={}, callbacks=callbacks,
                                machines=machines)
        self.lb = lb

    def test_run_benchmark(self):
        self.lb.run()


def create_local_benchmark():
    players = load_players(['plain_player'])
    task_config_id = 694826
    task0 = create_task_new(task_config_id)

    callbacks = [ConsoleCallback()]
    batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")
    lb = LocalBenchmark(name='local-benchmark', desc='desc', players=players,
                        random_states=[8060], ts_tasks_config=[task0],
                        working_dir=batches_data_dir,
                        scheduler_exit_on_finish=True,
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


if __name__ == '__main__':
    t = TestLocalBenchmark()
    t.setup_class()
    t.test_run()

