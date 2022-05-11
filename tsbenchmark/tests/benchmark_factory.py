from typing import Dict

import tsbenchmark
from tsbenchmark.benchmark import LocalBenchmark, load_players, RemoteSSHBenchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.datasets import TSDataset
from tsbenchmark.tasks import TSTask, TSTaskConfig
from tsbenchmark.tests.players import load_test_player
import sys,tempfile

DEFAULT_RANDOM_STATE = 8086


class ConsoleCallback(BenchmarkCallback):

    def on_start(self, bm):
        print('on_start')

    def on_task_start(self, bm, bm_task):
        print('on_task_start')

    def on_task_finish(self, bm, bm_task, elapsed: float):
        print('on_task_finish')

    def on_task_message(self, bm, bm_task, message: Dict):
        # reward, reward_metric, hyperparams, elapsed
        print('on_task_message')

    def on_task_break(self, bm, bm_task, elapsed: float):
        print('on_task_break')

    def on_finish(self, bm):
        print('on_finish')


def create_task():
    task_config_id = 694826
    task_config = tsbenchmark.tasks.get_task_config(task_config_id)
    return task_config


def create_minimal_local_benchmark():
    # define players
    player = load_test_player("plain_player_requirements_txt")
    task0 = create_task()
    callbacks = [ConsoleCallback()]
    lb = LocalBenchmark(name='name', desc='desc', players=[player],
                        random_states=[8086], ts_tasks_config=[task0], scheduler_exit_on_finish=True,
                        constraints={}, callbacks=callbacks)
    return lb


def load_plain_player_custom_python():
    player = load_test_player('plain_player_custom_python')
    player.env.venv.py_executable = sys.executable
    return player


def create_local_benchmark(callbacks=None):
    player = load_plain_player_custom_python()
    task0 = create_task()

    batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")

    lb = LocalBenchmark(name='local-benchmark', desc='desc', players=[player],
                        random_states=[DEFAULT_RANDOM_STATE], ts_tasks_config=[task0],
                        batch_app_init_kwargs=dict(scheduler_exit_on_finish=True, server_port=8060),
                        working_dir=batches_data_dir,
                        task_constraints={}, callbacks=callbacks)
    return lb
