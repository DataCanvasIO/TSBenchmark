# -*- encoding: utf-8 -*-
import json
import sys
from typing import Optional, Awaitable

from tornado.log import app_log
from tornado.web import RequestHandler, Finish, HTTPError, Application

from hypernets.hyperctl.batch import Batch
from hypernets.hyperctl.batch import ShellJob
from hypernets.hyperctl.executor import RemoteSSHExecutorManager
from hypernets.hyperctl.scheduler import JobScheduler
from hypernets.hyperctl.server import RestCode, RestResult, BaseHandler
from hypernets.hyperctl.utils import http_portal
from hypernets.utils import logging as hyn_logging

logger = hyn_logging.getLogger(__name__)


class IndexHandler(BaseHandler):

    def get(self, *args, **kwargs):
        return self.finish("Welcome to tsbenchmark.")


class TSTaskHandler(BaseHandler):

    def get(self, job_name, **kwargs):
        job = self.batch.get_job_by_name(job_name)
        if job is None:
            self.response({"msg": "resource not found"}, RestCode.Exception)
        else:
            ret_dict = job.to_dict()
            return self.response(ret_dict)

    def initialize(self, batch: Batch):
        self.batch = batch


class TSTaskListHandler(BaseHandler):

    def get(self, *args, **kwargs):
        jobs_dict = []
        for job in self.batch.jobs:
            jobs_dict.append(job.to_dict())
        self.response({"jobs": jobs_dict})

    def initialize(self, batch: Batch):
        self.batch = batch


class TsBenchmarkWebApplication(Application):

    def __init__(self, host="localhost", port=8060, **kwargs):
        self.host = host
        self.port = port
        super().__init__(**kwargs)

    @property
    def portal(self):
        return http_portal(self.host, self.port)


def create_tsbenchmark_webapp(server_host, server_port, batch, job_scheduler) -> TsBenchmarkWebApplication:
    handlers = [
        (r'/hyperctl/api/job/(?P<job_name>.+)', TSTaskHandler, dict(batch=batch)),
        (r'/hyperctl/api/job', TSTaskListHandler, dict(batch=batch)),
        (r'/hyperctl', IndexHandler)
    ]
    application = TsBenchmarkWebApplication(host=server_host, port=server_port, handlers=handlers)
    return application
