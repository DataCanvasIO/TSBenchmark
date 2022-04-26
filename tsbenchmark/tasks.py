from pathlib import Path

PWD = Path(__file__).parent


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

    def __init__(self, task_config, random_state, max_trails, reward_metric, id=None):
        self.id = None
        self.random_state = random_state
        self.max_trails = max_trails
        self.reward_metric = reward_metric
        self.taskdata = task_config.taskdata
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
        return self.taskdata.get_train()

    def get_test(self):
        return self.taskdata.get_test()


def get_task_config(task_id) -> TSTaskConfig:
    from tsbenchmark.tsloader import TSTaskLoader
    data_path = (PWD / "datas").absolute().as_posix()
    task_loader = TSTaskLoader(data_path)
    task_config: TSTaskConfig = task_loader.load(task_id)
    return task_config


def list_task_configs(tags=None, data_sizes=None, tasks=()):
    from tsbenchmark.tsloader import TSTaskLoader
    data_path = (Path(HERE).parent.parent / "datas").absolute().as_posix()
    task_loader = TSTaskLoader(data_path)
    return task_loader.list()
