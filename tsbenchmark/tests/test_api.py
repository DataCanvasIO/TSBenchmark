import asyncio
import os
import threading
import time

import tsbenchmark.tasks
from tsbenchmark import api
from tsbenchmark.benchmark import LocalBenchmark, load_players, Benchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.tasks import TSTask


class BenchmarkRunner(threading.Thread):

    def __init__(self, benchmark):
        super(BenchmarkRunner, self).__init__()
        self.benchmark = benchmark

    def run(self) -> None:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        self.benchmark.run()
        print("BenchmarkRunner thread exited")

    def stop(self):
        self.benchmark.stop()


class PlainCallback(BenchmarkCallback):
    def __init__(self):
        self.message_dict = {}

    def on_task_message(self, bm, bm_task, message):
        print("on_task_message")
        print(message)
        self.message_dict[bm_task] = message


class TestAPI:

    def setup_class(self):
        player_name = 'plain_player'

        self.task_config_id = 694826
        self.random_state = 8086
        self.api_server_url = 'http://localhost:8060'
        self.bm_task_id = f'{player_name}_{self.task_config_id}_{self.random_state}'

        task_config_id = self.task_config_id
        random_state = self.random_state

        os.environ['HYPERCTL_JOB_NAME'] = self.bm_task_id
        os.environ['HYPERCTL_SERVER_PORTAL'] = self.api_server_url

        players = load_players(['plain_player'])
        task_config = tsbenchmark.tasks.get_task_config(task_config_id)

        lb = LocalBenchmark(name='name', desc='desc', players=players,
                            random_states=[random_state], ts_tasks_config=[task_config],
                            constraints={}, scheduler_exit_on_finish=False,
                            callbacks=[PlainCallback()])

        self.runner = BenchmarkRunner(lb)
        self.runner.start()  # run benchmark in backend

        time.sleep(2)

    def test_get_task(self):
        # request task info
        task: TSTask = api.get_task()

        # assert task info
        assert task.random_state == self.random_state
        assert task.id == self.task_config_id

    def test_report_metric(self):
        api.report_task(report_data={'reward_metric': 0.7, 'bm_task_id': 0, },
                        bm_task_id=self.bm_task_id, api_server_uri=self.api_server_url)

        benchmark: Benchmark = self.runner.benchmark
        bm_task = benchmark.get_task(self.bm_task_id)
        assert bm_task

        callback: PlainCallback = benchmark.callbacks[0]
        assert isinstance(callback, PlainCallback)

        message = callback.message_dict.get(bm_task)
        assert message
        assert message['reward_metric'] == 0.7

    def teardown_class(self):
        self.runner.stop()


# if __name__ == '__main__':
#     t = TestAPI()
#     t.setup_class()
#     t.test_get_task()
