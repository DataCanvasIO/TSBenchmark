from typing import Dict

from tsbenchmark.benchmark import LocalBenchmark, load_players
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.tasks import TSTask
from tsbenchmark.reporter import Reporter
from hypernets.utils import logging

logging.set_level('DEBUG')  # TODO
logger = logging.getLogger(__name__)

import tsbenchmark.tasks


def create_task_new(task_config_id):
    task_config = tsbenchmark.tasks.get_task_config(task_config_id)

    task = TSTask(task_config, random_state=8086, max_trails=5, reward_metric='rmse')
    assert task.task == 'univariate-forecast' and task.dataset_id == 694826
    assert task.get_train().shape[0] == 124 and task.get_test().shape[0] == 6
    assert task.random_state == 8086
    return task


def mock_data_on_message(message):
    message[
        'metrics'] = "{'smape': 0.012477843773341856, 'mape': 0.012539559200733102, 'rmse': 77950.11909581693, 'mae': 70394.90456656972}"
    message['y_predict'] = "{'date': ['2020','2021','2022'], 's1': [13.2,13.3,13.4], 's2': [13.2,13.3,13.4]}"
    message['y_real'] = "{'date': ['2020','2021','2022'], 's1': [12.2,11.3,11.4], 's2': [14.2,11.3,13.5]}"
    message['duration'] = 6932
    return message


class ReporterCallback(BenchmarkCallback):
    def __init__(self, benchmark_config):
        self.reporter = Reporter(benchmark_config)

    def on_start(self, bm):
        print('on_start')

    def on_task_start(self, bm, bm_task):
        print('on_task_start')

    def on_task_finish(self, bm, bm_task, elapsed: float):
        print('on_task_finish')

    def on_task_message(self, bm, bm_task, message: Dict):
        # reward, reward_metric, hyperparams, elapsed
        message = mock_data_on_message(message)
        self.reporter.save_results_pred(message, bm_task)
        print('on_task_message')

    def on_task_break(self, bm, bm_task, elapsed: float):
        print('on_task_break')

    def on_finish(self, bm):
        self.reporter.generate_report()
        print('on_finish')


def test_local_benchmark():
    # define players
    players = load_players(['plain_player'])
    task_config_id = 694826
    task0 = create_task_new(task_config_id)
    # Mock data for benchmark_config

    benchmark_config = {'report_path': '/tmp/benchmark',
                        'name': 'hyperts_release_0.1.0',
                        'random_states': [8086],
                        'task_filter.tasks': ['univariate-forecast'],
                        'data_sizes': ['small']
                        }
    callbacks = [ReporterCallback(benchmark_config=benchmark_config)]

    lb = LocalBenchmark(name='name', desc='desc', players=players,
                        random_states=[8086], ts_tasks_config=[task0],
                        scheduler_exit_on_finish=True,
                        constraints={}, callbacks=callbacks)
    lb.run()
