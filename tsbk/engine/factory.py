import os


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
        self.random_state = None
        self.time_limit = None
        self.conf_path = None
        self.rounds_per_framework = None

    def result_dir_path(self):
        return self.report_path + os.sep + self.launch_name
