from engine.factory import BenchmarkBase

from utils.util import save_metrics, get_metadata, cal_metric
import time
import os
import sys
import traceback
import pandas as pd
from engine.report import Report
import random

from utils.util import logging

logger = logging.getLogger(__name__)

import importlib

metrics_target = ['smape', 'mape', 'rmse', 'mae']
task_calc_score = 'regression'

benchmark_report = Report()


class BenchmarkLocal(BenchmarkBase):
    def __init__(self, params):
        BenchmarkBase.__init__(self, params)

    def run(self):
        logger.debug("===============================")
        logger.debug(os.path.abspath(r'..{}frameworks'.format(os.sep)))
        os.environ['PATH'] += os.path.abspath(r'..\frameworks')
        sys.path.append(os.path.abspath(r'..{}frameworks'.format(os.sep)))
        logger.debug(os.path)
        logger.debug("===============================")
        params = self.params
        for framework in params.frameworks:
            trail_moudle = framework + '.run'
            self._run(trail_moudle, framework)
        logger.info(benchmark_report.get_count_msg())

    def _run(self, trail_moudle, framework):
        params = self.params
        logger.info("start run framework: {} {}".format(framework, params.tasks))
        tasks = params.tasks
        data_sizes = params.data_sizes
        white_list = params.white_list
        data_base_path = params.data_path
        vers = 'TODO'
        trail = importlib.import_module(trail_moudle).trail

        result_dir_path = self.params.result_dir_path()
        if not os.path.exists(result_dir_path):
            os.makedirs(result_dir_path)
        result_file_path = os.path.join(result_dir_path, params.launch_name + '_' + framework + '.csv')
        logger.info('result_file_path : {}'.format(result_file_path))
        no_and_dataset = []
        if os.path.exists(result_file_path):
            df_result_old = pd.read_csv(result_file_path)[['round_no', 'dataset']]
            no_and_dataset = (df_result_old['round_no'].astype(str) + df_result_old['dataset']).values
        time_start = time.time()
        for task in tasks:
            for data_size in data_sizes:
                path = os.path.join(data_base_path, task, data_size)
                if os.path.exists(path):
                    list = os.listdir(path)
                    for dir_path in list:
                        if dir == '__init__.py' or dir_path == 'template':
                            continue
                        if len(white_list) > 0 and dir_path not in white_list:
                            continue
                        self._run_one_job(path, dir_path, self.params.env, no_and_dataset, framework, trail, data_size,
                                          result_file_path)
        time_end = time.time()
        logger.info("end run framework:{}".format(framework))
        logger.info("total cost {}s".format(time_end - time_start))

    def _run_one_job(self, path, dir_path, mode, no_and_dataset, framework, trail, data_size, result_file_path):
        train_file_path = os.path.join(path, dir_path, 'train.csv')
        if mode == 'dev':
            train_file_path = os.path.join(path, dir_path, 'train_dev.csv')
        test_file_path = os.path.join(path, dir_path, 'test.csv')
        metadata_path = os.path.join(path, dir_path, 'metadata.yaml')

        if (os.path.exists(train_file_path) and os.path.getsize(train_file_path)) \
                or (os.path.exists(train_file_path[0:-4] + '.pkl')
                    and os.path.getsize(train_file_path[0:-4] + '.pkl')) > 0:
            logger.debug("train_file_path: " + train_file_path)
            logger.debug("test_file_path: " + test_file_path)
            logger.debug("metadata_path: " + metadata_path)
            metadata = get_metadata(metadata_path)

            try:
                df_train = pd.read_csv(train_file_path)
                df_test = pd.read_csv(test_file_path)

                for round_no in range(1, self.params.rounds_per_framework + 1):
                    time2_start = time.time()
                    if str(round_no) + metadata['name'] in no_and_dataset:
                        logger.info('==skipped== already trained {}{} {} '.format(round_no, metadata['name'],
                                                                                  framework))
                        benchmark_report.success_count = benchmark_report.success_count + 1
                        continue
                    random_state = random.randint(1,
                                                  65536) if self.params.random_state == None else self.params.random_state
                    y_pred, run_kwargs = trail(df_train, df_test,
                                               metadata['date_col_name'],
                                               metadata['series_col_name'], metadata['forecast_len'],
                                               metadata['dtformat'],
                                               metadata['task'],
                                               metadata['metric'],
                                               metadata['covariables'], self.params.max_trials, random_state)
                    time2_end = time.time()
                    time_cost = time2_end - time2_start
                    logging.debug('========== y_pred ==========')
                    logger.info(y_pred)
                    logging.debug('========== df_test ==========')
                    logger.info(df_test)
                    metrics = cal_metric(y_pred, df_test, metadata['date_col_name'], metadata['series_col_name'],
                                         metadata['covariables'],
                                         metrics_target, task_calc_score)

                    save_metrics(metadata,  metrics, time_cost, data_size,
                                 run_kwargs, result_file_path, framework, round_no, random_state)
            except Exception:
                traceback.print_exc()
                logger.error('train error on {}'.format(train_file_path))
                benchmark_report.error_count = benchmark_report.error_count + 1
                benchmark_report.error_list.append((framework, data_size, data_name))

            benchmark_report.success_count = benchmark_report.success_count + 1

    def gen_report(self):
        from analysis.report_analysis import generate_report
        generate_report(self.params.result_dir_path())


class BenchmarkRemote(BenchmarkBase):
    def __init__(self, params):
        BenchmarkBase.__init__(self, params)

    def run(self):
        logger.info(self.params)
        return None


class BenchmarkMultiThread(BenchmarkBase):
    def __init__(self, params):
        BenchmarkBase.__init__(self, params)

    def run(self):
        logger.info(self.params)
        return None
