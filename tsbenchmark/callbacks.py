from typing import Dict

from tsbenchmark.benchmark import Benchmark, BenchmarkTask


class BenchmarkCallback:

    def on_start(self, bm: Benchmark):
        pass

    def on_task_start(self, bm: Benchmark, bm_task: BenchmarkTask):
        pass

    def on_task_finish(self, bm: Benchmark, bm_task: BenchmarkTask, elapsed: float):
        pass

    def on_task_message(self, bm: Benchmark, bm_task: BenchmarkTask, message: Dict):
        # reward, reward_metric, hyperparams, elapsed
        pass

    def on_task_break(self, bm: Benchmark, bm_task: BenchmarkTask, elapsed: float):
        pass

    def on_finish(self, bm: Benchmark):
        pass

