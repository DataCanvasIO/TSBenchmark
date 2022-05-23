import os
from pathlib import Path
import time

from tsbenchmark.consts import DEFAULT_CACHE_PATH, ENV_DATASETS_CACHE_PATH


class TSTaskConfig(object):

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


class TSTask(object):
    """ Player will get the data and metadata from the TSTask then run algorithm for compete.
    Attributes:
        dataset_id: str, not None.
            The unique identification id.
        date_name: str, not None.
            The name of the date column.
        task: str, not None.
            The type of forecast. In time series task, it could be 'univariate-forecast' or 'multivariate-forecast'.
        horizon: int, not None.
            Number of periods of data to forecast ahead.
        shape: str, not None.
            The dataset shape from the train dataframe. The result from pandas.DataFrame.shape().
        series_name: str or arr.
            The names of the series columns.
            For 'univariate-forecast' task, it should not be None.For 'multivariate-forecast' task, it should be None.
            In the task from tsbenchmark.api.get_task() or tsbenchmark.api.get_local_task or called function TSTask.ready,
            series_name should not be None.

        covariables_name: str or arr, may be None.
            The names of the covariables columns.
            It should be get after called function TSTask.ready(), or from task from tsbenchmark.api.get_task() or tsbenchmark.api.get_local_task.

        dtformat: str, not None.
            The format of the date column.

    Methods:
        get_train, get_test
    """
    def __init__(self, task_config, **kwargs):
        for k, v in task_config.__dict__.items():
            self.__dict__[k] = v

        if "random_state" in kwargs:
            self.random_state = kwargs.pop("random_state")
        if "max_trials" in kwargs:
            self.max_trials = kwargs.pop("max_trials")
        if "reward_metric" in kwargs:
            self.reward_metric = kwargs.pop("reward_metric")

        self.start_time = time.time()
        self.download_time = 0
        self.end_time = None

        self.__train = None
        self.__test = None

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

    def ready(self):
        metadata = self.taskdata.taskdata_loader.dataset_loader.ready(self.id)
        for k, v in metadata.items():
            self.__dict__[k] = v



def _get_task_load(cache_path=None):
    if cache_path is None:
        cache_path = os.getenv(ENV_DATASETS_CACHE_PATH)
        if cache_path is None:
            cache_path = DEFAULT_CACHE_PATH

    from tsbenchmark.tsloader import TSTaskLoader
    task_loader = TSTaskLoader(cache_path)
    return task_loader


def get_task_config(task_id, cache_path=None) -> TSTaskConfig:
    task_loader = _get_task_load(cache_path)
    task_config: TSTaskConfig = task_loader.load(task_id)
    return task_config


def list_task_configs(*args, **kwargs):
    if 'cache_path' in kwargs:
        cache_path = kwargs.pop("cache_path")
    else:
        cache_path = None

    if 'ids' in kwargs:
        dataset_ids = kwargs.pop("ids")
    else:
        dataset_ids = None

    task_loader = _get_task_load(cache_path)
    tasks = task_loader.list(*args, **kwargs)

    if dataset_ids is not None and len(dataset_ids) > 0:
        ret_tasks = list(filter(lambda t: get_task_config(t).dataset_id in list(map(str,dataset_ids)), tasks))
    else:
        ret_tasks = tasks

    return ret_tasks
