import os
import numpy as np
import pandas as pd
import json
from utils.util import logging
import traceback

logger = logging.getLogger(__name__)


def get_filelist(dir, Filelist):
    if os.path.isfile(dir):

        Filelist.append(dir)

    elif os.path.isdir(dir):

        for s in os.listdir(dir):
            newDir = os.path.join(dir, s)

            get_filelist(newDir, Filelist)

    return Filelist


def generate_report(report_dir_path):
    logger.info('start generate report')
    result_file_list = get_filelist(report_dir_path, [])
    columns = ['dataset', 'shape', 'data_size', 'task', 'horizon']
    results_datas, frameworks = get_result_datas(result_file_list)
    report_calc(results_datas, columns, frameworks, report_dir_path)
    return 0


def report_calc(results_datas, columns, frameworks, report_dir_path):
    report_calc_metric(results_datas, columns, frameworks, report_dir_path, 'smape', 'mean')
    report_calc_metric(results_datas, columns, frameworks, report_dir_path, 'smape', 'std')
    report_calc_metric(results_datas, columns, frameworks, report_dir_path, 'mape', 'mean')
    report_calc_metric(results_datas, columns, frameworks, report_dir_path, 'mape', 'std')
    report_calc_metric(results_datas, columns, frameworks, report_dir_path, 'rmse', 'mean')
    report_calc_metric(results_datas, columns, frameworks, report_dir_path, 'rmse', 'std')
    report_calc_metric(results_datas, columns, frameworks, report_dir_path, 'mae', 'mean')
    report_calc_metric(results_datas, columns, frameworks, report_dir_path, 'mae', 'std')


def report_calc_metric(results_datas, columns, frameworks, report_dir_path, metric, stat_type):
    columns_report = columns + frameworks
    report_datas = {}
    for row_key in list(results_datas.keys()):
        row_data = results_datas[row_key]
        framework = row_data['framework']
        report_data_key = row_data['dataset'] + row_data['task']
        if report_data_key not in (report_datas.keys()):
            row_report = {}
            for col in columns:
                row_report[col] = row_data[col]
            report_datas[report_data_key] = row_report
        row_report = report_datas[report_data_key]
        if stat_type == 'mean':
            row_report[framework] = np.mean(row_data[metric])
        elif stat_type == 'std':
            row_report[framework] = np.std(row_data[metric])
    logger.debug(report_datas)

    df_report = pd.DataFrame(columns=columns_report)
    for row_report in report_datas.values():
        df_report = df_report.append(row_report, ignore_index=True)
    logger.debug(df_report)
    report_path = '{}{}report_{}_{}.csv'.format(report_dir_path, os.sep, metric, stat_type)
    df_report.to_csv(report_path, index=False)
    logger.info('report generated: {}'.format(report_path))


def get_result_datas(result_file_list):
    # results_datas = {'smape': {}, 'mape': {}, 'rmse': {}, 'mae': {}}
    results_datas = {}
    framworks = []
    for result_file in result_file_list:
        if 'report_' in result_file or '.csv' not in result_file:
            continue
        results_datas, framworks = result_data_from_file(result_file, results_datas, framworks)
    return results_datas, framworks


def result_data_from_file(result_file, results_datas, frameworks):
    df = pd.read_csv(result_file)
    for index, row in df.iterrows():
        key = '{}_{}_{}'.format(row['dataset'], row['framework'], row['task'])
        try:
            if key not in results_datas:
                if row['framework'] not in frameworks:
                    frameworks.append(row['framework'])
                results_datas[key] = {'dataset': row['dataset'], 'framework': row['framework'], 'shape': row['shape'],
                                      'data_size': row['data_size'], 'task': row['task'],
                                      'horizon': row['horizon']}
            data_row = results_datas[key]
            metrics = json.loads(row['metrics_scores'].replace('\'', '\"').replace('nan', 'NaN'))
            for metric in list(metrics.keys()):
                if metric not in list(data_row.keys()):
                    results_datas[key][metric] = [metrics[metric]]
                else:
                    results_datas[key][metric].append(metrics[metric])

        except:
            traceback.print_exc()
            print('====== error======')
    return results_datas, frameworks


def result_data_from_file_old(result_file, results_datas, columns):
    df = pd.read_csv(result_file)
    for index, row in df.iterrows():
        key = row['dataset'] + row['task']
        try:
            if key not in results_datas['smape']:
                if row['framework'] not in columns:
                    columns.append(row['framework'])
                new_row = {'dataset': row['dataset'], 'shape': row['shape'],
                           'data_size': row['data_size'], 'task': row['task'],
                           'horizon': row['horizon']}
                for report_type in list(results_datas.keys()):
                    results_datas[report_type][key] = new_row
            metrics = json.loads(row['metrics_scores'].replace('\'', '\"').replace('nan', 'NaN'))
            for report_type in list(results_datas.keys()):
                results_datas[report_type][key][row['framework']] = metrics[report_type]

        except:
            traceback.print_exc()
            print('====== error======')
    return results_datas


generate_report(r'D:\文档\0 DAT\3 Benchmark\benchmark-output\hyperts\hyperts_release_0.1.0')
