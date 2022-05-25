from typing import Dict

import tsbenchmark
from tsbenchmark.benchmark import LocalBenchmark, RemoteSSHBenchmark
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.tasks import TSTask
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


def create_univariate_task():
    task_config = tsbenchmark.tasks.get_task_config(512754)
    return task_config


def create_multivariable_task():
    task_config = tsbenchmark.tasks.get_task_config(61807)
    return task_config


def load_plain_player_custom_python():
    player = load_test_player('plain_player_custom_python')
    player.env.venv.py_executable = sys.executable
    return player


def _init_benchmark_benchmark(players=None, tasks=None, callbacks=None,
                              random_states=None):
    if players is None:
        players = [load_plain_player_custom_python()]

    if tasks is None:
        tasks = [create_univariate_task()]

    if random_states is None:
        random_states = [DEFAULT_RANDOM_STATE]

    if callbacks is None:
        callbacks = []

    callbacks.append(ConsoleCallback())

    batches_data_dir = tempfile.mkdtemp(prefix="benchmark-test-batches")

    kwargs = dict(desc='desc', players=players,
                  random_states=random_states, ts_tasks_config=tasks,
                  working_dir=batches_data_dir,
                  callbacks=callbacks)
    return kwargs


def create_local_benchmark(batch_app_init_kwargs=None, conda_home=None, **kwargs):
    init_kwargs = _init_benchmark_benchmark(**kwargs)

    if batch_app_init_kwargs is None:
        batch_app_init_kwargs = dict(scheduler_exit_on_finish=True,
                                     scheduler_interval=1,
                                     server_port=8060)
    lb = LocalBenchmark(name='local-benchmark', conda_home=conda_home, batch_app_init_kwargs=batch_app_init_kwargs,
                        **init_kwargs)
    return lb


def create_remote_benchmark(machines, server_host, **kwargs):

    init_kwargs = _init_benchmark_benchmark(**kwargs)

    batch_app_init_kwargs = dict(server_port=8060,
                                 server_host=server_host,
                                 scheduler_interval=1,
                                 scheduler_exit_on_finish=True)

    lb = RemoteSSHBenchmark(name="remote-benchmark",
                            machines=machines,
                            batch_app_init_kwargs=batch_app_init_kwargs,
                            **init_kwargs)

    return lb
