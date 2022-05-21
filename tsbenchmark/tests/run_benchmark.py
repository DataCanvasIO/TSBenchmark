import asyncio
import os
import threading
import time

import tsbenchmark.tasks
from tsbenchmark import api
from tsbenchmark.benchmark import LocalBenchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.tasks import TSTask
from tsbenchmark.tests.test_api import BenchmarkRunner


class PlainCallback(BenchmarkCallback):
    def __init__(self):
        self.message_dict = {}

    def on_task_message(self, bm, bm_task, message):
        print("on_task_message")
        self.message_dict[bm_task] = message


def main():
    player_name = 'plain_player'

    task_config_id = 512754
    random_state = 8086
    api_server_url = 'http://localhost:8060'
    bm_task_id = f'{player_name}_{task_config_id}_{random_state}'

    task_config_id = task_config_id
    random_state = random_state

    os.environ['HYPERCTL_JOB_NAME'] = bm_task_id
    os.environ['HYPERCTL_SERVER_PORTAL'] = api_server_url

    players = load_players(['plain_player'])
    task_config = tsbenchmark.tasks.get_task_config(task_config_id)

    lb = LocalBenchmark(name='name', desc='desc', players=players,
                        random_states=[random_state], ts_tasks_config=[task_config],
                        constraints={}, callbacks=[PlainCallback()])

    runner = BenchmarkRunner(lb)
    runner.start()  # run benchmark in backend


if __name__ == '__main__':
    main()
