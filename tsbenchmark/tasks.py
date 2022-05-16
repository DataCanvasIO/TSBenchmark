from pathlib import Path
import time

from tsbenchmark.consts import DEFAULT_CACHE_PATH


class TSTaskConfig:

    def __init__(self, taskconfig_id, dataset_id, taskdata, date_name, task, horizon, data_size, shape, series_name,
                 covariables_name,
                 dtformat):
        self.id = taskconfig_id
        self.dataset_id = dataset_id
        self.taskdata = taskdata
        self.date_name = date_name
        self.task = task
        self.horizon = horizon
        self.data_size = data_size
        self.shape = shape
        self.series_name = series_name
        self.covariables_name = covariables_name
        self.dtformat = dtformat


class TSTask(TSTaskConfig):

    def __init__(self, task_config, random_state, max_trials, reward_metric, id=None):
        self.id = None
        self.random_state = random_state
        self.max_trails = max_trials
        self.reward_metric = reward_metric
        self.taskdata = task_config.taskdata
        self.start_time = time.time()
        self.end_time = None
        self.download_time = 0
        self.__train = None
        self.__test = None
        for k, v in task_config.__dict__.items():
            self.__dict__[k] = v

    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task,
            "target": self.target,
            "time_series": self.time_series,
            "dataset": self.dataset_id,
            "covariables": self.covariables,
        }

    def get_data(self):
        return self.taskdata.get_train(), self.taskdata.get_test()

    def get_train(self):
        if self.__train is None:
            self.__train = self.taskdata.get_train()
        return self.__train

    def get_test(self):
        if self.__test is None:
            self.__test = self.taskdata.get_test()
        return self.__test


def get_task_config(task_id, cache_path=None) -> TSTaskConfig:
    if cache_path is None:
        cache_path = DEFAULT_CACHE_PATH

    from tsbenchmark.tsloader import TSTaskLoader
    task_loader = TSTaskLoader(cache_path)
    task_config: TSTaskConfig = task_loader.load(task_id)
    return task_config


def list_task_configs(*args, **kwargs):
    if 'cache_path' in kwargs:
        cache_path = kwargs.pop("cache_path")
    else:
        cache_path = DEFAULT_CACHE_PATH

    from tsbenchmark.tsloader import TSTaskLoader
    dataset_ids = kwargs.pop('ids')

    task_loader = TSTaskLoader(cache_path)
    tasks = task_loader.list(*args, **kwargs)
    if dataset_ids is not None and len(dataset_ids) > 0:
        ret_tasks = list(filter(lambda t: get_task_config(t).dataset_id in dataset_ids, tasks))
    else:
        ret_tasks = tasks

    return ret_tasks
