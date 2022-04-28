from typing import Dict

from tsbenchmark.benchmark import LocalBenchmark, load_players
from tsbenchmark.callbacks import BenchmarkCallback
from tsbenchmark.tasks import TSTask
from tsbenchmark.reporter import Reporter
from hypernets.utils import logging

logging.set_level('DEBUG')  # TODO
logger = logging.getLogger(__name__)

import tsbenchmark.tasks


def create_tasks_new():
    tasks = [TSTask(tsbenchmark.tasks.get_task_config(t_id), random_state=8086, max_trails=1, reward_metric='rmse') for
             t_id in [694826, 309496]]
    return tasks


def create_benchmark_cfg():
    benchmark_config = {'report.path': '/tmp/report_path',
                        'name': 'hyperts_release_0.4.0',
                        'desc': 'develop for pytest hyperts_release_0.3.0',
                        'random_states': [8086],
                        'task_filter.tasks': ['univariate-forecast']
                        }
    return benchmark_config


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
        self.reporter.save_results(message, bm_task)
        print('on_task_message')

    def on_task_break(self, bm, bm_task, elapsed: float):
        print('on_task_break')

    def on_finish(self, bm):
        self.reporter.generate_report()
        print('on_finish')


def atest_benchmark_reporter():
    # define players
    players = load_players(['hyperts_dl_player', 'hyperts_stat_player'])
    task_list = [TSTask(tsbenchmark.tasks.get_task_config(t_id), random_state=8086, max_trails=1, reward_metric='rmse')
                 for
                 t_id in [694826, 309496]]

    # Mock data for benchmark_config
    benchmark_config = create_benchmark_cfg()
    callbacks = [ReporterCallback(benchmark_config=benchmark_config)]

    lb = LocalBenchmark(name=benchmark_config['name'], desc=benchmark_config['desc'], players=players,
                        random_states=benchmark_config['random_states'], ts_tasks_config=task_list,
                        scheduler_exit_on_finish=True,
                        constraints={}, callbacks=callbacks)
    lb.run()


def atest_reporter_generate():
    benchmark_config = create_benchmark_cfg()
    rc = ReporterCallback(benchmark_config=benchmark_config)
    rc.reporter.generate_report()
