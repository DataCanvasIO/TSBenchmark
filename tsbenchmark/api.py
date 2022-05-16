from typing import Dict

from hypernets.hyperctl import api as hyperctl_api
from tsbenchmark import tasks
from tsbenchmark.util import cal_task_metrics
import pandas as pd
import json
import os
import time

from hypernets.hyperctl import consts
from hypernets.hyperctl import utils

from hypernets.utils import logging as hyn_logging
from tsbenchmark.players import JobParams
from tsbenchmark.tasks import TSTask
from tsbenchmark.consts import DEFAULT_REPORT_METRICS

hyn_logging.set_level(hyn_logging.DEBUG)

logger = hyn_logging.get_logger(__name__)


def get_task():
    hyperctl_job_params = hyperctl_api.get_job_params()

    job_params = JobParams(**hyperctl_job_params)

    # task_id = hyperctl_job_params['task_id']
    # random_state = hyperctl_job_params['random_state']
    # max_trials = hyperctl_job_params['max_trials']
    # reward_metric = hyperctl_job_params['reward_metric']

    task_config = tasks.get_task_config(job_params.task_config_id)

    t = TSTask(task_config=task_config, random_state=job_params.random_state,
               max_trials=job_params.max_trials, reward_metric=job_params.reward_metric)
    return t


def get_local_task(data_path, dataset_id, random_state, max_trials, reward_metric):
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
        report_data:
        bm_task_id: str, optional, BenchmarkTask id, if is None will get from current job
        api_server_uri: str, optional, tsbenchmark api server uri, if is None will get from environment or
            use default value

    Returns:

    """

    bm_task_id = _get_bm_task_id(bm_task_id)
    assert bm_task_id
    api_server_uri = _get_api_server_api(api_server_uri)
    assert api_server_uri

    report_url = f"{api_server_uri}/tsbenchmark/api/benchmark-task/{bm_task_id}/report"

    request_dict = {
        'data': report_data
    }

    utils.post_request(report_url, json.dumps(request_dict))


def send_report_data(task: TSTask, y_pred: pd.DataFrame, key_params='', best_params=''):
    """Send report data.

          Args:
              y_pred: pandas dataframe, required, The predicted values by the players.
              key_params: str, optional, The params which user want to save to the report datas.
              best_params: str, optional, The best model's params, for automl, there are many models will be trained.
                           If user want to save the best params, user may assign the best_params.

          Returns:

          ------------------------------------------------------------------------------------------------------------
          Description:
              1. Prepare the data which can be call be tsb.api.report_task.
              2. Call method report_task, send the report data to the Master Server.
              When develop a new play locally, this method will help user validate the predicted and params.

          """
    task.__end_time = time.time()
    default_metrics = DEFAULT_REPORT_METRICS
    target_metrics = default_metrics
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


def _get_api_server_api(api_server_uri=None):
    if api_server_uri is None:
        api_server_portal = os.getenv(consts.KEY_ENV_SERVER_PORTAL)
        assert api_server_portal
        return api_server_portal
    else:
        return api_server_uri


def _get_bm_task_id(bm_task_id):
    if bm_task_id is None:
        hyperctl_job_params = hyperctl_api.get_job_params()
        job_params = JobParams(**hyperctl_job_params)
        return job_params.bm_task_id
    else:
        return bm_task_id

