# -*- encoding: utf-8 -*-

from hypernets.hyperctl.appliation import BatchApplication
from hypernets.hyperctl.server import RestCode, BaseHandler, create_hyperctl_handlers, \
    HyperctlWebApplication
from hypernets.utils import logging as hyn_logging

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

    def post(self, bm_task_id, operation,  **kwargs):
        request_body = self.get_request_as_dict()
        benchmark = self.benchmark
        message_dict = request_body

        # check bm_task_id
        bm_task = benchmark.get_task(bm_task_id)
        if bm_task is None:
            self.response({"msg": "resource not found"}, RestCode.Exception)
            return

        if operation == 'report':
            for callback in benchmark.callbacks:
                from tsbenchmark.callbacks import BenchmarkCallback
                callback: BenchmarkCallback = callback
                callback.on_task_message(benchmark, bm_task, message_dict.get('data'))

            return self.response({}, code=RestCode.Success)
        else:
            # TODO kill operation
            pass

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

    def __init__(self, benchmark, **kwargs):  # TODO
        self.benchmark = benchmark
        super(BenchmarkBatchApplication, self).__init__(**kwargs)

    def _create_web_app(self, server_host, server_port, batch):
        hyperctl_handlers = create_hyperctl_handlers(batch, self.job_scheduler)
        tsbenchmark_handlers = [
            (r'/tsbenchmark/api/task/(?P<task_id>.+)', TSTaskHandler),
            (r'/tsbenchmark/api/benchmark-task/(?P<bm_task_id>.+)/(?P<operation>.+)',
             BenchmarkTaskOperationHandler, dict(benchmark=self.benchmark)),
            (r'/tsbenchmark/api/job', TSTaskListHandler),
            (r'/tsbenchmark', IndexHandler)
        ]

        handlers = tsbenchmark_handlers + hyperctl_handlers
        application = HyperctlWebApplication(host=server_host, port=server_port, handlers=handlers)
        return application
