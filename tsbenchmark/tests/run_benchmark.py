from tsbenchmark.benchmark import LocalBenchmark, load_players
from tsbenchmark.tdatasets import TSDataset
from tsbenchmark.ttasks import TSTaskConfig

# define players
players = load_players(['plain_player'])

# define task list
class NetworkTrafficDataset(TSDataset):
    """Test dataset"""

    def __init__(self):
        super(NetworkTrafficDataset, self).__init__(0)

    def get_data(self):
        from hyperts.datasets.base import load_network_traffic
        df = load_network_traffic()
        return df


task1 = TSTaskConfig(1, task='multivariate-forecast',
                     target='Var_1', time_series='TimeStamp',
                     dataset_id=NetworkTrafficDataset(),
                     covariables=['HourSin', 'WeekCos', 'CBWD'])

lb = LocalBenchmark(name='name', desc='desc', players=players, tasks=[task1], constraints={})

lb.run()

