# -*- encoding: utf-8 -*-
import json
import sys
from typing import Optional, Awaitable

from tornado.log import app_log
from tornado.web import RequestHandler, Finish, HTTPError, Application

from hypernets.hyperctl.appliation import BatchApplication
from hypernets.hyperctl.batch import Batch
from hypernets.hyperctl.batch import ShellJob
from hypernets.hyperctl.callbacks import BatchCallback
from hypernets.hyperctl.executor import RemoteSSHExecutorManager
from hypernets.hyperctl.scheduler import JobScheduler
from hypernets.hyperctl.server import RestCode, RestResult, BaseHandler, create_hyperctl_handlers, \
    HyperctlWebApplication
from hypernets.hyperctl.utils import http_portal
from hypernets.utils import logging as hyn_logging
import tsbenchmark.tasks

logger = hyn_logging.getLogger(__name__)


class IndexHandler(BaseHandler):

    def get(self, *args, **kwargs):
        return self.finish("Welcome to tsbenchmark.")


class TSTaskHandler(BaseHandler):

    def get(self, task_id, **kwargs):
        print(task_id)
        task = self.mock_task()
        if task is None:
            self.response({"msg": "resource not found"}, RestCode.Exception)
        else:
            ret_dict = task.to_dict()
            return self.response(ret_dict)

    def mock_task(self):
        from tsbenchmark.tasks import TSTask
        return TSTask(1, task='multivariate-forecast',
                      target='Var_1', time_series='TimeStamp',
                      dataset_id="NetworkTrafficDataset",
                      covariables=['HourSin', 'WeekCos', 'CBWD'])
    # def initialize(self, batch: Batch):
    #     self.batch = batch
    #


class BenchmarkTaskOperationHandler(BaseHandler):

    def post(self, task_name, operation,  **kwargs):
        request_body = self.get_request_as_dict()
        print(task_name)
        # 修改job的状态, 再调用callback事件
        #
        benchmark = self.benchmark
        for task in benchmark.ts_tasks_config:
            if task.name == task_name:
                task._status = 'finished'
                # check

        if task is None:
            self.response({"msg": "resource not found"}, RestCode.Exception)
        else:
            ret_dict = task.to_dict()
            return self.response(ret_dict)

    def initialize(self, benchmark):
        self.benchmark = benchmark


class TSTaskListHandler(BaseHandler):

    def get(self, *args, **kwargs):
        jobs_dict = []
        for job in self.batch.jobs:
            jobs_dict.append(job.to_dict())
        self.response({"jobs": jobs_dict})

    # def initialize(self, batch: Batch):
    #     self.batch = batch


class BenchmarkBatchApplication(BatchApplication):

    def __init__(self, benchmark, **kwargs):
        super(BenchmarkBatchApplication, self).__init__(**kwargs)
        self.benchmark = benchmark

    def _create_web_app(self, server_host, server_port, batch):
        hyperctl_handlers = create_hyperctl_handlers(batch, self.job_scheduler)
        tsbenchmark_handlers = [
            (r'/tsbenchmark/api/task/(?P<task_id>.+)', TSTaskHandler),
            (r'/tsbenchmark/api/benchmark-task/(?P<task_id>.+)/(?P<operation>.+)', BenchmarkTaskOperationHandler),
            (r'/tsbenchmark/api/job', TSTaskListHandler),
            (r'/tsbenchmark', IndexHandler)
        ]

        handlers = tsbenchmark_handlers + hyperctl_handlers
        application = HyperctlWebApplication(host=server_host, port=server_port, handlers=handlers)
        return application
