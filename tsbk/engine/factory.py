import os
from utils.util import get_dir_path


class Factory:
    def get_benchmark(self, type, params):
        if type == 'local':
            from engine.benchmark_wrappers import BenchmarkLocal
            return BenchmarkLocal(params)
        elif type == 'threads':
            from engine.benchmark_wrappers import BenchmarkMultiThread
            return BenchmarkMultiThread(params)
        elif type == 'remote':
            from engine.benchmark_wrappers import BenchmarkRemote
            return BenchmarkRemote(params)
        else:
            msg = '[{}] is not illegal, it should be one of [local,threads,remote].'.format(type)
            raise ValueError(msg)


class BenchmarkBase:
    def __init__(self, params):
        self.params = params

    def run(self):
        raise NotImplementedError(
            'run is a protected abstract method, it must be implemented.'
        )

    def gen_report(self):
        raise NotImplementedError(
            'run is a protected abstract method, it must be implemented.'
        )


class Params:
    def __init__(self, tasks, data_sizes, frameworks):
        self.tasks = tasks
        self.data_sizes = data_sizes
        self.frameworks = frameworks
        self.metrics_target = ['smape', 'mape', 'rmse', 'mae']
        self.task_calc_score = 'regression'
        self.launch_name = ''
        self.launch_desc = ''
        self.white_list = []
        self.env = None
        self.data_path = None
        self.report_path = None
        self.max_trials = None
        self.random_states = None
        self.time_limit = None
        self.conf_path = None
        self.rounds_per_framework = None

    # e.g. /mnt/result/hyperts_v0.1.0/
    def result_dir_path(self):
        return get_dir_path(self.report_path + os.sep + self.launch_name)

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/
    def task_dir(self, task):
        return get_dir_path(os.path.join(self.result_dir_path(), task))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/datas
    def datas_results_dir(self, task):
        return get_dir_path(os.path.join(self.task_dir(task), 'datas'))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/report
    def report_dir(self, task):
        return get_dir_path(os.path.join(self.task_dir(task), 'report'))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/report/imgs
    def report_imgs_dir(self, task):
        return get_dir_path(os.path.join(self.report_dir(task), 'imgs'))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/datas/hyperts_release_0.1.0_prod_hyperts_dl.csv
    def data_results_file(self, task, filename):
        return os.path.join(self.datas_results_dir(task), filename)

    def params_runtime_file(self):
        return os.path.join(self.result_dir_path(), 'params_runtime')
