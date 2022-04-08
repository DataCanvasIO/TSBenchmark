import os
import numpy as np
import pandas as pd
import json
from utils.util import logging, sub_dict
import traceback
import analysis.report_painter as report_painter

logger = logging.getLogger(__name__)


def get_filelist(dir, Filelist):
    if os.path.isfile(dir):

        Filelist.append(dir)

    elif os.path.isdir(dir):

        for s in os.listdir(dir):
            newDir = os.path.join(dir, s)

            get_filelist(newDir, Filelist)

    return Filelist


def gen_comparison_report(params):
    logger.info('gen_comparison_report=======')
    for task in params.tasks:
        columns = ['dataset', 'shape', 'horizon']
        compare_reports_dirs = params.compare_reports_dirs(task)

        report_files = [os.listdir(crd) for crd in compare_reports_dirs]
        report_names = set(report_files[0] + report_files[1])
        report_names.remove('imgs')

        for framework in params.frameworks:
            compare_framework_path = params.compare_framework_dir(task, framework)
            for report_name in report_names:
                try:
                    dfs = [pd.read_csv(os.path.join(report_dir, report_name)) for report_dir in compare_reports_dirs]
                    df = pd.concat([dfs[0][columns], dfs[0][[framework]], dfs[1][[framework]]], axis=1)
                    df.columns = columns + params.reports
                    df.to_csv(os.path.join(compare_framework_path, report_name), index=False)
                    png_path = os.path.join(params.compare_imgs_dir(task, framework), report_name[:-3] + 'png')
                    report_painter.paint_table(df, title_cols=columns,
                                               title_text=framework + ' ' + report_name[7:-4].replace('_', ' '),
                                               fontsize=6,
                                               result_path=png_path)
                except:
                    traceback.print_exc()
                    logger.error('{png_path} generate error')


def generate_report(params):
    for task in params.tasks:
        datas_results_dir = params.datas_results_dir(task)
        report_dir = params.report_dir(task)
        report_imgs_dir = params.report_imgs_dir(task)

        logger.info('start generate report')
        data_results_file = get_filelist(datas_results_dir, [])
        columns = ['dataset', 'shape', 'horizon']
        results_datas, frameworks = get_result_datas(data_results_file)

        report_calc(results_datas, columns, frameworks, report_dir, report_imgs_dir)


def report_calc(results_datas, columns, frameworks, report_dir, report_imgs_dir):
    frameworks_non_navie = [f for f in frameworks if 'navie' not in f]
    # Metrics report
    report_calc_metric(results_datas, columns, frameworks, report_dir, report_imgs_dir, 'smape', 'mean')
    report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'smape', 'std')
    report_calc_metric(results_datas, columns, frameworks, report_dir, report_imgs_dir, 'mape', 'mean')
    report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'mape', 'std')
    report_calc_metric(results_datas, columns, frameworks, report_dir, report_imgs_dir, 'rmse', 'mean')
    report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'rmse', 'std')
    report_calc_metric(results_datas, columns, frameworks, report_dir, report_imgs_dir, 'mae', 'mean')
    report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'mae', 'std')

    # Time cost report TODO
    report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'duration', 'mean',
                       title_text='MEAN duration')
    report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'duration', 'std',
                       title_text='STD duration')
    report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'duration', 'max',
                       title_text='MAX duration')
    report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'duration', 'min',
                       title_text='MIN duration')

    # Others report TODO


def report_calc_metric(results_datas, columns, frameworks, report_dir, report_imgs_dir, metric, stat_type,
                       title_text=None):
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
        elif stat_type == 'max':
            row_report[framework] = np.max(row_data[metric])
        elif stat_type == 'min':
            row_report[framework] = np.min(row_data[metric])
    logger.debug(report_datas)

    df_report = pd.DataFrame(columns=columns_report)
    for row_report in report_datas.values():
        df_report = df_report.append(sub_dict(row_report, columns_report), ignore_index=True)
    logger.debug(df_report)
    report_path = '{}{}report_{}_{}.csv'.format(report_dir, os.sep, metric, stat_type)
    df_report.to_csv(report_path, index=False)
    logger.info('report generated: {}'.format(report_path))

    png_path = '{}{}report_{}_{}.png'.format(report_imgs_dir, os.sep, metric, stat_type)
    if title_text == None:
        title_text = '{} {} {} '.format(metric.upper(), stat_type, 'scores')
    report_painter.paint_table(df_report, title_cols=columns, title_text=title_text, fontsize=6, result_path=png_path)

def get_result_datas(result_file_list):
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
                                      'horizon': row['horizon'], 'duration': [row['duration']]}
            else:
                results_datas[key]['duration'].append(row['duration'])

            data_row = results_datas[key]
            metrics = json.loads(row['metrics_scores'].replace('\'', '\"').replace('nan', 'NaN'))
            for metric in list(metrics.keys()):
                if metric not in list(data_row.keys()):
                    results_datas[key][metric] = [metrics[metric]]
                else:
                    results_datas[key][metric].append(metrics[metric])
        except:
            traceback.print_exc()
            logger.error('====== error======')
    return results_datas, frameworks
