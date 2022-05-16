from typing import Dict


class BenchmarkCallback:

    def on_start(self, bm):
        pass

    def on_task_start(self, bm, bm_task):
        pass

    def on_task_finish(self, bm, bm_task, elapsed: float):
        pass

    def on_task_message(self, bm, bm_task, message: Dict):
        # reward, reward_metric, hyperparams, elapsed
        pass

    def on_task_break(self, bm, bm_task, elapsed: float):
        pass

    def on_finish(self, bm):
        pass


class ReporterCallback(BenchmarkCallback):
    def __init__(self, benchmark_config):
        from tsbenchmark.reporter import Reporter
        self.reporter = Reporter(benchmark_config)

    def on_start(self, bm):
        pass

    def on_task_start(self, bm, bm_task):
        pass

    def on_task_finish(self, bm, bm_task, elapsed: float):
        pass

    def on_task_message(self, bm, bm_task, message: Dict):
        self.reporter.save_results(message, bm_task)

    def on_task_break(self, bm, bm_task, elapsed: float):
        pass

    def on_finish(self, bm):
        self.reporter.generate_report()
