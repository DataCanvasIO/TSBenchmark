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

