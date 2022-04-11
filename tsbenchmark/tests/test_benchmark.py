from tsbenchmark.benchmark import LocalBenchmark, load_players, RemoteSSHBenchmark
from tsbenchmark.tdatasets import TSDataset
from tsbenchmark.ttasks import TSTaskConfig
import tsbenchmark.ttasks


def test_local_benchmark():
    # define players
    players = load_players(['plain_player'])
    task0 = tsbenchmark.ttasks.get_task(0)
    lb = LocalBenchmark(name='name', desc='desc', players=players, tasks=[task0], constraints={})
    lb.run()


def atest_remote_benchmark():
    # define players
    players = load_players(['plain_player'])
    task0 = tsbenchmark.ttasks.get_task(0)
    machines = [

    ]
    lb = RemoteSSHBenchmark(name='name', desc='desc', players=players, tasks=[task0], constraints={}, machines=machines)
    lb.run()

