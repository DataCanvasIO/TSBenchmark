from pathlib import Path
from tsbenchmark.util import cal_task_metrics
import time

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
        self.__start_time = time.time()
        self.__end_time = None
        self.__download_time = 0
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

    def make_report_data(self, y_pred, *args):
        self.__end_time = time.time()
        default_metrics = ['smape', 'mape', 'rmse', 'mae']  # todo
        target_metrics = default_metrics
        task_metrics = cal_task_metrics(y_pred, self.get_test()[super.series_name], super.date_name,
                                        super.series_name,
                                        super.covariables_name, target_metrics, 'regression')

        report_data = {
            'duration': self.__end_time - self.__end_time - self.__download_time,
            'y_predict': y_pred[super.series_name].to_json(orient='records')[1:-1].replace('},{', '} {'),
            'y_real': self.get_test()[super.series_name].to_json(orient='records')[1:-1].replace('},{', '} {'),
            'metrics': task_metrics,
            'args': args
        }
        return report_data


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
