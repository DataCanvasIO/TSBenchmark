from amlb.benchmark import TaskConfig
from tsbenchmark.benchmark import Benchmark


class TSBenchmarkCallback:

    def on_start(self, bm: Benchmark):
        pass

    def on_task_start(self, task_config: TaskConfig):
        pass

    def on_task_finish(self, task_config: TaskConfig, player, elapsed: int, reward, player_hyperparams):
        pass

    def on_task_break(self):
        pass

    def on_finish(self):
        pass
