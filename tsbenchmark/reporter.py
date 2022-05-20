import os
from tsbenchmark.util import file_util, dict_util
from hypernets.hyperctl.utils import load_yaml
import pandas as pd
from hypernets.utils import logging
import traceback
import numpy as np
import json
import matplotlib.pyplot as plt

logging.set_level('DEBUG')  # TODO
logger = logging.getLogger(__name__)


class PathMaintainer:
    '''

    /report_path
    /report_path/benchmark_name
    /report_path/benchmark_name/task
    /report_path/benchmark_name/task/datas
    /report_path/benchmark_name/task/datas/player.csv
    /report_path/benchmark_name/task/datas/player_tmp.csv
    /report_path/benchmark_name/task/report
    /report_path/benchmark_name/task/report/report_name.csv
    /report_path/benchmark_name/task/report/imgs
    /report_path/benchmark_name/task/report/imgs/report_name.png
    '''

    def __init__(self, report_path, benchmark_name):
        self.report_path = report_path
        self.benchmark_name = benchmark_name

    def benchmark_dir(self):
        report_path = file_util.get_dir_path(self.report_path)
        return file_util.get_dir_path(os.path.join(report_path, self.benchmark_name))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/
    def task_dir(self, task_type):
        return file_util.get_dir_path(os.path.join(self.benchmark_dir(), task_type))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/datas
    def datas_dir(self, task_type):
        return file_util.get_dir_path(os.path.join(self.task_dir(task_type), 'datas'))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/report
    def report_dir(self, task_type):
        return file_util.get_dir_path(os.path.join(self.task_dir(task_type), 'report'))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/report/imgs
    def report_imgs_dir(self, task_type):
        return file_util.get_dir_path(os.path.join(self.report_dir(task_type), 'imgs'))

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/datas/hyperts_dl.csv
    def data_file(self, bmtask):
        return os.path.join(self.datas_dir(bmtask.ts_task.task), bmtask.player.name + '.csv')

    # e.g. /mnt/result/hyperts_v0.1.0/univariate-forecast/datas/hyperts_dl_tmp.csv
    def data_file_tmp(self, bmtask):
        return os.path.join(self.datas_dir(bmtask.ts_task.task), bmtask.player.name + '_tmp.csv')

    # def compare_reports_dirs(self, task): todo
    #     return [os.path.join(self.report_path, report_name, task, 'report') for report_name in self.reports]
    #
    # def compare_framework_dir(self, task, framework):
    #     return file_util.get_dir_path(os.path.join(self.task_dir(task), framework))
    #
    # def compare_imgs_dir(self, task, framework):
    #     return file_util.get_dir_path(os.path.join(self.compare_framework_dir(task, framework), 'imgs'))


class Painter:
    def get_steps_colors(self, values):
        _range = np.max(values) - np.min(values)
        if _range == 0:
            _range = 1
        else:
            values = 1 / values
        _values = (values - np.min(values)) / _range
        colors_data = plt.cm.Wistia(_values)
        return colors_data

    def paint_table(self, df, title_cols, title_text, result_path, fontsize=-1, fig_background_color='white',
                    fig_border='white'):
        df = df.copy()
        df = df.applymap(lambda x: x[:15] + '...' if isinstance(x, str) and len(x) > 15 else x)

        # Get headers
        footer_text = ''
        cols_header = df.columns
        cols_header_data = df.columns[1:]
        if title_cols != None:
            cols_header_data = df.columns[len(title_cols):]

        df_data = df[cols_header_data]

        # Get data
        cell_text = []
        for i, row in df.iterrows():
            data_row = list(row.values[0:len(title_cols)]) + [f'{x:1.3f}' for x in row.values[len(title_cols):]]
            cell_text.append(data_row)

        # Get colors
        colors_cells = []
        for i, row in df_data.iterrows():
            colors_data = self.get_steps_colors(row.values)
            colors_row = np.append(plt.cm.binary(np.full(len(title_cols), 1)), colors_data, axis=0)
            colors_cells.append(colors_row)

        colors_header = plt.cm.binary(np.full(len(cols_header), 1))

        # Figure
        plt.figure(linewidth=2,
                   edgecolor=fig_border,
                   facecolor=fig_background_color,
                   tight_layout={'pad': 1},
                   # figsize=(5,3)
                   )

        # plt.rcParams.update({"font.size": 20})
        the_table = plt.table(cellText=cell_text,
                              cellColours=colors_cells,
                              rowLoc='right',
                              colColours=colors_header,
                              colLabels=cols_header,
                              loc='center')

        # Set font size if user set it
        if fontsize > 0:
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(fontsize)

        the_table.scale(1, 1.5)
        # Hide axes
        ax = plt.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        # Hide axes border
        plt.box(on=None)
        # Add title
        cell_height = the_table[0, 0].get_height()
        center = 0.5
        distance_cell_title = 0.02
        y = center + cell_height * (df.shape[0] + 1) / 2 + distance_cell_title
        plt.suptitle(title_text, y=y)
        # Add footer
        plt.figtext(0.95, 0.05, footer_text, horizontalalignment='right', size=6, weight='light')
        # Force the figure to update, so backends center objects correctly within the figure.
        # Without plt.draw() here, the title will center on the axes and not the figure.
        plt.draw()

        # Create image. plt.savefig ignores figure edge and face colors, so map them.
        fig = plt.gcf()
        plt.savefig(result_path,
                    # bbox='tight',
                    edgecolor=fig.get_edgecolor(),
                    facecolor=fig.get_facecolor(),
                    dpi=400
                    )


class Analysis:
    def __init__(self, benchmark_config):
        self.painter = Painter()
        self.benchmark_config = benchmark_config
        self.path_maintainer = PathMaintainer(benchmark_config['report.path'], benchmark_config['name'])

    def gen_comparison_report(self, params):
        for task in params.ts_tasks_config:
            columns = ['dataset', 'shape', 'horizon']
            compare_reports_dirs = params.compare_reports_dirs(task)

            report_files = [os.listdir(crd) for crd in compare_reports_dirs]
            report_names = set(report_files[0] + report_files[1])
            report_names.remove('imgs')

            for framework in params.frameworks:
                compare_framework_path = params.compare_framework_dir(task, framework)
                for report_name in report_names:
                    try:
                        dfs = [pd.read_csv(os.path.join(report_dir, report_name)) for report_dir in
                               compare_reports_dirs]
                        df = pd.concat([dfs[0][columns], dfs[0][[framework]], dfs[1][[framework]]], axis=1)
                        df.columns = columns + params.reports
                        df.to_csv(os.path.join(compare_framework_path, report_name), index=False)
                        png_path = os.path.join(params.compare_imgs_dir(task, framework), report_name[:-3] + 'png')
                        self.painter.paint_table(df, title_cols=columns,
                                                 title_text=framework + ' ' + report_name[7:-4].replace('_', ' '),
                                                 fontsize=6,
                                                 result_path=png_path)
                    except:
                        traceback.print_exc()
                        logger.error('{png_path} generate error')

    def generate_report(self):
        for task_type in self.benchmark_config['task_filter.tasks']:
            task_dir = self.path_maintainer.task_dir(task_type)
            report_dir = self.path_maintainer.report_dir(task_type)
            report_imgs_dir = self.path_maintainer.report_imgs_dir(task_type)

            logger.info('start generate report')
            data_results_file = file_util.get_filelist(task_dir, [])

            results_datas, players = self.get_result_datas(data_results_file)

            self.report_calc(results_datas, players, report_dir, report_imgs_dir)

    def report_calc(self, results_datas, players, report_dir, report_imgs_dir):
        columns = ['dataset', 'shape', 'horizon']
        frameworks_non_navie = [p for p in players if 'navie' not in p]
        # Metrics report
        self.report_calc_metric(results_datas, columns, players, report_dir, report_imgs_dir, 'smape', 'mean')
        self.report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'smape',
                                'std')
        self.report_calc_metric(results_datas, columns, players, report_dir, report_imgs_dir, 'mape', 'mean')
        self.report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'mape',
                                'std')
        self.report_calc_metric(results_datas, columns, players, report_dir, report_imgs_dir, 'rmse', 'mean')
        self.report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'rmse',
                                'std')
        self.report_calc_metric(results_datas, columns, players, report_dir, report_imgs_dir, 'mae', 'mean')
        self.report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'mae', 'std')

        self.report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'duration',
                                'mean',
                                title_text='MEAN duration')
        self.report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'duration',
                                'std',
                                title_text='STD duration')
        self.report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'duration',
                                'max',
                                title_text='MAX duration')
        self.report_calc_metric(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir, 'duration',
                                'min',
                                title_text='MIN duration')

    def report_calc_metric(self, results_datas, columns, players, report_dir, report_imgs_dir, metric, stat_type,
                           title_text=None):
        columns_report = columns + players
        report_datas = {}
        for row_key in list(results_datas.keys()):
            row_data = results_datas[row_key]
            player = row_data['player']
            report_data_key = row_data['dataset'] + row_data['task']
            if report_data_key not in (report_datas.keys()):
                row_report = {}
                for col in columns:
                    row_report[col] = row_data[col]
                report_datas[report_data_key] = row_report
            row_report = report_datas[report_data_key]
            if stat_type == 'mean':
                row_report[player] = np.mean(row_data[metric])
            elif stat_type == 'std':
                row_report[player] = np.std(row_data[metric])
            elif stat_type == 'max':
                row_report[player] = np.max(row_data[metric])
            elif stat_type == 'min':
                row_report[player] = np.min(row_data[metric])
        logger.debug(report_datas)

        df_report = pd.DataFrame(columns=columns_report)
        for row_report in report_datas.values():
            df_report = df_report.append(dict_util.sub_dict(row_report, columns_report), ignore_index=True)
        logger.debug(df_report)
        report_path = '{}{}report_{}_{}.csv'.format(report_dir, os.sep, metric, stat_type)
        df_report.to_csv(report_path, index=False)
        logger.info('report generated: {}'.format(report_path))
        return df_report

        # png_path = '{}{}report_{}_{}.png'.format(report_imgs_dir, os.sep, metric, stat_type)
        # if title_text == None:
        #     title_text = '{} {} {} '.format(metric.upper(), stat_type, 'scores')
        # self.painter.paint_table(df_report, title_cols=columns, title_text=title_text, fontsize=6,
        #                          result_path=png_path)

    def get_result_datas(self, result_file_list):
        results_datas = {}
        players = []
        for result_file in result_file_list:
            if 'report_' in os.path.basename(result_file) or '.csv' not in os.path.basename(result_file):
                continue
            results_datas, players = self.result_data_from_file(result_file, results_datas, players)
        return results_datas, players

    def result_data_from_file(self, result_file, results_datas, players):
        df = pd.read_csv(result_file)
        for index, row in df.iterrows():
            key = '{}_{}_{}'.format(row['dataset'], row['player'], row['task'])
            try:
                if key not in results_datas:
                    if row['player'] not in players:
                        players.append(row['player'])
                    results_datas[key] = {'dataset': row['dataset'], 'player': row['player'],
                                          'shape': row['shape'],
                                          'data_size': row['data_size'], 'task': row['task'],
                                          'horizon': row['horizon'], 'duration': [row['duration']]}
                else:
                    results_datas[key]['duration'].append(row['duration'])

                data_row = results_datas[key]
                metrics = json.loads(row['metrics'].replace('\'', '\"').replace('nan', 'NaN'))
                for metric in list(metrics.keys()):
                    if metric not in list(data_row.keys()):
                        results_datas[key][metric] = [metrics[metric]]
                    else:
                        results_datas[key][metric].append(metrics[metric])
            except:
                traceback.print_exc()
                logger.error('====== error======')
        return results_datas, players


class Reporter():
    def __init__(self, benchmark_config):
        self.benchmark_config = benchmark_config
        self.path_maintainer = PathMaintainer(benchmark_config['report.path'], benchmark_config['name'])
        self.analysis = Analysis(self.benchmark_config)
        self.painter = Painter()

    def save_results(self, message, bm_task):
        # todo missing_rate periods cv cv_folds run_times init_params ensemble best_model_params run_kwargs industry frequency
        cols_data_tmp = ['task_id', 'round_no', 'player', 'dataset', 'shape', 'data_size', 'task', 'horizon',
                         'reward_metric', 'metrics', 'duration', 'random_state', 'y_predict', 'y_real', 'key_params',
                         'best_params']
        data_df = pd.DataFrame(columns=cols_data_tmp)
        data_file = self.path_maintainer.data_file(bm_task)

        round_no = 1
        if 'random_states' in self.benchmark_config and bm_task.ts_task.random_state is not None:
            round_no = self.benchmark_config['random_states'].index(bm_task.ts_task.random_state) + 1

        data = {'task_id': bm_task.ts_task.id,
                'round_no': round_no,
                'player': bm_task.player.name,
                'dataset': bm_task.ts_task.taskdata.name,
                'shape': bm_task.ts_task.shape,
                'data_size': bm_task.ts_task.data_size,
                'task': bm_task.ts_task.task,
                'horizon': bm_task.ts_task.horizon,
                'reward_metric': bm_task.ts_task.reward_metric,
                'metrics': message['metrics'],
                'duration': message['duration'],
                'random_state': bm_task.ts_task.random_state,
                'y_predict': message['y_predict'],
                'y_real': message['y_real'],
                'key_params': message['key_params'],
                'best_params': message['best_params']
                }

        data_df = data_df.append(data, ignore_index=True)
        if os.path.exists(data_file):
            data_df[cols_data_tmp].to_csv(data_file, mode='a', index=False, header=False)
            logger.info(f"Save result to : {data_file}")
        else:
            data_df[cols_data_tmp].to_csv(data_file, mode='a', index=False)
            logger.info(f"Append result to : {data_file}")

    def generate_report(self):
        logger.info('start generate report')
        for task_type in self.benchmark_config['task_filter.tasks']:
            task_dir = self.path_maintainer.task_dir(task_type)
            report_dir = self.path_maintainer.report_dir(task_type)
            report_imgs_dir = self.path_maintainer.report_imgs_dir(task_type)
            data_results_file = file_util.get_filelist(task_dir, [])
            results_datas, players = self.analysis.get_result_datas(data_results_file)
            self.generate_type_reports(results_datas, players, report_dir, report_imgs_dir)

    def generate_type_reports(self, results_datas, players, report_dir, report_imgs_dir):
        columns = ['dataset', 'shape', 'horizon']
        frameworks_non_navie = [p for p in players if 'navie' not in p]

        # metrics reports
        for metric in ['smape', 'mape', 'rmse', 'mae']:
            self.calc_and_paint(results_datas, columns, players, report_dir, report_imgs_dir, metric, 'mean')
            self.calc_and_paint(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir,
                                metric,
                                'std')

        # duration reports
        for stat_type in ['mean', 'std', 'max', 'min']:
            self.calc_and_paint(results_datas, columns, frameworks_non_navie, report_dir, report_imgs_dir,
                                'duration',
                                stat_type,
                                title_text=stat_type.upper() + ' duration')

    def calc_and_paint(self, results_datas, columns, players, report_dir, report_imgs_dir, metric, stat_type,
                       title_text=None):
        if len(players) == 0:
            return
        df_report = self.analysis.report_calc_metric(results_datas, columns, players, report_dir, report_imgs_dir,
                                                     metric, stat_type)
        if title_text == None:
            title_text = '{} {} {} '.format(metric.upper(), stat_type, 'scores')
        png_path = '{}{}report_{}_{}.png'.format(report_imgs_dir, os.sep, metric, stat_type)
        self.painter.paint_table(df_report, title_cols=columns, title_text=title_text, fontsize=6,
                                 result_path=png_path)
        logger.info('report figure generated: {}'.format(png_path))


class CompareReporter():
    def __init__(self, config_dict):
        self.config_dict = config_dict
        self.painter = Painter()
        self.reports = [os.path.basename(p) for p in config_dict['report_paths']]

    def run_compare(self):
        logger.info(f'Begin generate compare report {self.config_dict["name"]}')
        columns = ['dataset', 'shape', 'horizon']
        for task in self.config_dict['tasks']:
            compare_reports_dirs = self.compare_reports_dirs(task)

            report_files = [os.listdir(crd) for crd in compare_reports_dirs]
            report_names = set(report_files[0] + report_files[1])
            report_names.remove('imgs')

            for player in self.config_dict['players']:
                compare_player_dir = self.compare_player_dir(task, player)
                for report_name in report_names:
                    try:
                        dfs = [pd.read_csv(os.path.join(report_dir, report_name)) for report_dir in
                               compare_reports_dirs]
                        df = pd.concat([dfs[0][columns], dfs[0][[player]], dfs[1][[player]]], axis=1)
                        df.columns = columns + self.reports
                        df.to_csv(os.path.join(compare_player_dir, report_name), index=False)
                        png_path = os.path.join(self.compare_imgs_dir(task, player), report_name[:-3] + 'png')
                        self.painter.paint_table(df, title_cols=columns,
                                                 title_text=player + ' ' + report_name[7:-4].replace('_', ' '),
                                                 fontsize=6,
                                                 result_path=png_path)
                    except:
                        traceback.print_exc()
                        logger.error('{png_path} generate error')
        logger.info(f'Finish generate compare report in {self.config_dict["report"]["path"]}')
        
    def compare_reports_dirs(self, task):
        return [os.path.join(report_path, task, 'report') for report_path in self.config_dict['report_paths']]

    def compare_player_dir(self, task, player):
        return file_util.get_dir_path(
            os.path.join(self.config_dict['report']['path'], self.config_dict['name'], task, player))

    def compare_imgs_dir(self, task, player):
        return file_util.get_dir_path(os.path.join(self.compare_player_dir(task, player), 'imgs'))


def load_compare_reporter(config_file: str):
    config_dict = load_yaml(config_file)
    return CompareReporter(config_dict)
