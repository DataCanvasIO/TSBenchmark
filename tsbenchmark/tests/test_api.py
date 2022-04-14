import asyncio
import os
import threading
import time

import tsbenchmark.tasks
from tsbenchmark import api
from tsbenchmark.benchmark import LocalBenchmark, load_players
from tsbenchmark.tasks import TSTask



class BenchmarkRunner(threading.Thread):

    def __init__(self, benchmark):
        super(BenchmarkRunner, self).__init__()
        self.benchmark = benchmark

    def run(self) -> None:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        self.benchmark.run()

    def stop(self):
        self.benchmark.stop()


class TestAPI:

    def setup_class(self):
        player_name = 'plain_player'
        self.task_config_id = 694826
        self.random_state = 8086

        task_config_id = self.task_config_id
        random_state = self.random_state

        os.environ['HYPERCTL_JOB_NAME'] = f'{player_name}_{task_config_id}_{random_state}'
        os.environ['HYPERCTL_SERVER_PORTAL'] = 'http://localhost:8060'

        players = load_players(['plain_player'])
        task_config = tsbenchmark.tasks.get_task_config(task_config_id)

        lb = LocalBenchmark(name='name', desc='desc', players=players,
                            random_states=[random_state], ts_tasks_config=[task_config], constraints={})

        self.runner = BenchmarkRunner(lb)
        self.runner.start()  # run benchmark in backend

        time.sleep(2)

    def test_get_task(self):
        # request task info
        task: TSTask = api.get_task()

        # assert task info
        assert task.random_state == self.random_state
        assert task.id == self.task_config_id

    def teardown_class(self):
        self.runner.stop()
