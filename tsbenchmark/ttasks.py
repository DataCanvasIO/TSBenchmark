class TSTaskConfig:

    def __init__(self, dataset_id, dataset, date_name, task, horizon, series_name, covariables_name, dtformat):
        self.dataset_id = dataset_id
        self.dataset = dataset
        self.date_name = date_name
        self.task = task
        self.horizon = horizon
        self.series_name = series_name
        self.covariables_name = covariables_name
        self.dtformat = dtformat


class TSTask(TSTaskConfig):

    def __init__(self, task_config, random_state, max_trails, reward_metric):
        self.id = task_config.dataset_id
        self.random_state = random_state
        self.max_trails = max_trails
        self.reward_metric = reward_metric
        self.dataset = task_config.dataset
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
        return self.dataset.get_train(), self.dataset.get_test()

    def get_train(self):
        return self.dataset.get_train()

    def get_test(self):
        return self.dataset.get_test()


def get_task(task_id):
    return TSTask(0, task='multivariate-forecast',
                  target='Var_1', time_series='TimeStamp',
                  dataset_id=0,
                  covariables=['HourSin', 'WeekCos', 'CBWD'])


def list_tasks(tags=None, data_sizes=None, tasks=()):
    return [get_task(0)]  # TODO
