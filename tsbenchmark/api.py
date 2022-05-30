import json
import os
import time

import pandas as pd
from typing import Dict

from tsbenchmark.tasks import TSTask
from tsbenchmark.consts import DEFAULT_REPORT_METRICS, DEFAULT_GLOBAL_RANDOM_STATE
from tsbenchmark import tasks







# __all__ = ['get_task', 'get_local_task', 'send_report_data']


def get_task() -> TSTask:
    """Get a TsTask from benchmark server.

    TsTask is a unit task, which help Player get the data and metadata.
    It will get TsTaskConfig from benchmark server and construct it to TSTask. Call TSTask.ready() method init start
    time and load data.

    See Also:
        TSTask : Player will get the data and metadata from the TSTask then run algorithm for compete.

    Notes:
        1. You can get attributes description from TSTask.
        2. In the report it support 'smape', 'mape', 'mae' and 'rmse'.

    Returns: TSTask, The TsTask  for player get the data and metadata.
    """
    from hypernets.hyperctl import api as hyperctl_api
    from tsbenchmark.players import JobParams
    hyperctl_job_params = hyperctl_api.get_job_params()

    job_params = JobParams(**hyperctl_job_params)

    task_config = tasks.get_task_config(job_params.task_config_id, cache_path=job_params.dataset_cache_path)

    t = TSTask(task_config=task_config, random_state=job_params.random_state,
               max_trials=job_params.max_trials, reward_metric=job_params.reward_metric)
    t.ready()
    return t


def get_local_task(data_path, dataset_id='512754',
                   random_state=DEFAULT_GLOBAL_RANDOM_STATE, max_trials=3, reward_metric='smape') -> TSTask:
    """Get a TsTask from local for develop a new player and test.

    TsTask is a unit task, which help Player get the data and metadata.
    It will get a TsTaskConfig locally and construct it to TSTask. Call TSTask.ready() method init start
    time and load data.

    Args:
        data_path : str, default='~/tmp/data_cache'.
            The path locally to cache data. TSLoader will download data and cache it in data_path.
        dataset_id : str, default='512754'.
            The unique id for a dataset task. You can get it from tests/dataset_desc.csv.
        random_state : int, consts.GLOBAL_RANDOM_STATE.
           Determines random number for automl framework.
        max_trials : int, default=3.
            Maximum number of tests for automl framework, optional.
        reward_metric : str, default='smape'.
             The optimize direction for model selection.
             Hypernets search reward metric name or callable. Possible values: 'accuracy', 'auc', 'mse',
             'mae','rmse', 'mape', 'smape', and 'msle'.

    Notes:
        1. You can get attributes description from TSTask.
        2. In the report it support 'smape', 'mape', 'mae' and 'rmse'.


    See Also:
        TSTask: Player will get the data and metadata from the TSTask then run algorithm for compete.

    Returns: TSTask, The TsTask for player get the data and metadata.

    """

    from tsbenchmark.tsloader import TSTaskLoader
    from tsbenchmark.tasks import TSTask
    data_path = data_path
    task_loader = TSTaskLoader(data_path)
    task_config = task_loader.load(dataset_id)
    task = TSTask(task_config, random_state=random_state, max_trials=max_trials, reward_metric=reward_metric)
    task.ready()
    setattr(task, "_local_model", True)
    return task


def report_task(report_data: Dict, bm_task_id=None, api_server_uri=None):
    """Report metrics or running information to api server.

    Args:
        report_data: Dict. The report data generate by send_report_data.
        bm_task_id: str, optional, BenchmarkTask id, if is None will get from current job
        api_server_uri: str, optional, tsbenchmark api server uri, if is None will get from environment or
            use default value

    """

    bm_task_id = _get_bm_task_id(bm_task_id)
    assert bm_task_id
    api_server_uri = _get_api_server_api(api_server_uri)
    assert api_server_uri

    report_url = f"{api_server_uri}/tsbenchmark/api/benchmark-task/{bm_task_id}/report"

    request_dict = {
        'data': report_data
    }

    from hypernets.hyperctl import utils
    utils.post_request(report_url, json.dumps(request_dict))


def send_report_data(task: TSTask, y_pred: pd.DataFrame, key_params='', best_params=''):
    """Send report data.

    This interface used for send report data to benchmark server.
    1. Prepare the data which can be call be tsb.api.report_task.
    2. Call method report_task, send the report data to the Benchmark Server.


    Args:
        y_pred: pandas.DataFrame,
            The predicted values by the players.
        key_params: str, default=''
            The params which user want to save to the report datas.
        best_params: str, default=''
            The best model's params, for automl, there are many models will be trained.
            If user want to save the best params, user may assign the best_params.

    Notes:
        When develop a new play locally, this method will help user validate the predicted and params.

    """
    task._end_time = time.time()
    default_metrics = DEFAULT_REPORT_METRICS
    target_metrics = default_metrics

    assert y_pred is not None
    if y_pred.shape[0] != task.get_test().shape[0]:
        raise Exception(f"The result should have {task.get_test().shape[0]} rows but got {y_pred.shape[0]}. ")

    from tsbenchmark.util import cal_task_metrics
    task_metrics = cal_task_metrics(y_pred, task.get_test()[task.series_name], task.date_name,
                                    task.series_name,
                                    task.covariables_name, target_metrics, 'regression')

    report_data = {
        'duration': time.time() - task.start_time - task.download_time,
        'y_predict': y_pred[task.series_name].to_json(orient='records')[1:-1].replace('},{', '} {'),
        'y_real': task.get_test()[task.series_name].to_json(orient='records')[1:-1].replace('},{', '} {'),
        'metrics': task_metrics,
        'key_params': key_params,
        'best_params': best_params
    }

    if not hasattr(task, "_local_model"):
        report_task(report_data)
    else:
        from hypernets.utils import logging as hyn_logging
        hyn_logging.set_level(hyn_logging.DEBUG)
        logger = hyn_logging.get_logger(__name__)
        logger.info("Successfully validation for local test mode.")


def _get_api_server_api(api_server_uri=None):

    if api_server_uri is None:
        from hypernets.hyperctl import consts
        api_server_portal = os.getenv(consts.KEY_ENV_SERVER_PORTAL)
        assert api_server_portal
        return api_server_portal
    else:
        return api_server_uri


def _get_bm_task_id(bm_task_id):
    if bm_task_id is None:
        from hypernets.hyperctl import api as hyperctl_api
        from tsbenchmark.players import JobParams
        hyperctl_job_params = hyperctl_api.get_job_params()
        job_params = JobParams(**hyperctl_job_params)
        return job_params.bm_task_id
    else:
        return bm_task_id

