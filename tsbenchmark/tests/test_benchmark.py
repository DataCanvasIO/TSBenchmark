from tsbenchmark.benchmark import LocalBenchmark, load_players, RemoteSSHBenchmark
from tsbenchmark.tdatasets import TSDataset
from tsbenchmark.ttasks import TSTask, TSTaskConfig

import tsbenchmark.ttasks


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
    config = TSTaskConfig(dataset_id=0, dataset=dataset, date_name='TimeStamp', task='multivariate-forecast',
                          horizon=7, series_name='Var_1',
                          covariables_name=['HourSin', 'WeekCos', 'CBWD'], dtformat='%Y-%m-%d')
    t = TSTask(task_config=config, random_state=8086, max_trails=3, reward_metric='rmse')
    setattr(t, 'id', 0)  # TODO remove
    return t


def test_local_benchmark():
    # define players
    players = load_players(['plain_player'])
    task0 = create_task()
    lb = LocalBenchmark(name='name', desc='desc', players=players, tasks=[task0], constraints={})
    lb.run()


def atest_remote_benchmark():
    # define players
    players = load_players(['plain_player'])
    task0 = tsbenchmark.ttasks.get_task(0)
    machines = []
    lb = RemoteSSHBenchmark(name='name', desc='desc', players=players, tasks=[task0], constraints={}, machines=machines)
    lb.run()
