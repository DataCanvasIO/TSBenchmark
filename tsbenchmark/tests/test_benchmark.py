from typing import Dict

from tsbenchmark.benchmark import LocalBenchmark, load_players, RemoteSSHBenchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.datasets import TSDataset
from tsbenchmark.tasks import TSTask, TSTaskConfig
from hypernets.tests.utils import ssh_utils_test

import tsbenchmark.tasks


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


def test_local_benchmark():
    # define players
    players = load_players(['plain_player'])
    task_config_id = 694826
    task0 = create_task_new(task_config_id)

    callbacks = [ConsoleCallback()]

    lb = LocalBenchmark(name='name', desc='desc', players=players,
                        random_states=[8060], ts_tasks_config=[task0],
                        scheduler_exit_on_finish=True,
                        constraints={}, callbacks=callbacks)
    lb.run()


# class TestLocalBenchmark:
#     def setup_class(self):
#         pass
#
#
#     def teardown_class(self):
#         self.runner.stop()
#


@ssh_utils_test.need_psw_auth_ssh
def test_remote_benchmark():
    # define players
    players = load_players(['plain_player'])
    task_config_id = 694826
    task0 = create_task_new(task_config_id)

    callbacks = [ConsoleCallback()]
    machines = [ssh_utils_test.load_ssh_psw_config()]
    print(machines)
    lb = RemoteSSHBenchmark(name='name', desc='desc', players=players,
                            random_states=[8060], ts_tasks_config=[task0],
                            scheduler_exit_on_finish=True,
                            constraints={}, callbacks=callbacks,
                            machines=machines)
    lb.run()


# if __name__ == '__main__':
#     test_remote_benchmark()
