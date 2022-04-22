from typing import Dict

from hypernets.hyperctl import api as hyperctl_api
from tsbenchmark import tasks
import json
import os

import requests

from hypernets.hyperctl import consts
from hypernets.hyperctl import utils

from hypernets.utils import logging as hyn_logging
from tsbenchmark.players import JobParams
from tsbenchmark.tasks import TSTask

hyn_logging.set_level(hyn_logging.DEBUG)

logger = hyn_logging.get_logger(__name__)


def get_task():
    hyperctl_job_params = hyperctl_api.get_job_params()

    job_params = JobParams(**hyperctl_job_params)

    # task_id = hyperctl_job_params['task_id']
    # random_state = hyperctl_job_params['random_state']
    # max_trails = hyperctl_job_params['max_trails']
    # reward_metric = hyperctl_job_params['reward_metric']

    task_config = tasks.get_task_config(job_params.task_config_id)

    t = TSTask(task_config=task_config, random_state=job_params.random_state,
               max_trails=job_params.max_trails, reward_metric=job_params.reward_metric)
    return t


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


def _get_job_name_and_damon_portal():
    job_name = os.getenv(consts.KEY_ENV_JOB_NAME)
    api_server_portal = f"{os.getenv(consts.KEY_ENV_SERVER_PORTAL)}"

    assert job_name
    assert api_server_portal

    return job_name, api_server_portal


def get_job_working_dir():
    job_working_dir = os.getenv(consts.KEY_ENV_JOB_WORKING_DIR)
    return job_working_dir


def list_jobs(api_server_portal):
    # if api_server_portal is None:
    #     api_server_portal = os.getenv(consts.KEY_ENV_api_server_portal)
    assert api_server_portal
    url_get_jobs = f"{api_server_portal}/hyperctl/api/job"
    data = _request(url_get_jobs)
    return data['jobs']


def kill_job(api_server_portal, job_name):
    url_kill_job = f"{api_server_portal}/hyperctl/api/job/{job_name}/kill"
    data = _request(url_kill_job, method='post')
    return data
