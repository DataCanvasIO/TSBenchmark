from hyperts.utils import metrics
import shutil
import yaml

import pandas as pd

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_metrics(metadata, metrics, time_cost, data_size,
                 run_kwargs, result_file_path, framework, round_no, random_state):
    # metadata['missing_rate'] TODO
    # metadata['periods'] TODO
    # 'cv' TODO
    # 'cv_folds' TODO
    # 'run_times' TODO
    # 'init_params' TODO
    # 'init_params' TODO
    # 'ensemble' TODO
    # 'best_model_params' TODO

    try:
        metrics_df = pd.read_csv(result_file_path)
    except:
        print(result_file_path + ' is null')
        metrics_df = pd.DataFrame(
            columns=['round_no', 'framework', 'dataset', 'shape', 'data_size', 'industry', 'frequency', 'task',
                     'horizon', 'metric',
                     'metric_score',
                     'metrics_scores',
                     'HyperTS_duration[s]',
                     'run_kwargs', 'random_state'])

    data = {'round_no': round_no, 'framework': framework, 'dataset': metadata['name'], 'shape': metadata['shape'],
            'data_size': data_size,
            'industry': metadata['industry'],
            'frequency': metadata['frequency'],
            'task': metadata['task'],
            'horizon': metadata['forecast_len'],
            'metric': metadata['metric'],
            'metric_score': round(metrics[metadata['metric']], 6),
            'metrics_scores': metrics,
            'HyperTS_duration[s]': round(time_cost, 1),
            'run_kwargs': run_kwargs,
            'random_state': random_state}
    print("metric: ", metadata['metric'], " merics: ", metrics)
    metrics_df = metrics_df.append(data, ignore_index=True)
    metrics_df.to_csv(result_file_path, index=False)
    print("save result to : ", result_file_path)


def get_metadata(metadata_path):
    f = open(metadata_path, 'r', encoding='utf-8')
    metadata = yaml.load(f.read(), Loader=yaml.FullLoader)

    # metadata['missing_rate'] TODO
    # metadata['periods'] TODO

    metadata['frequency'] = get_param(metadata, 'frequency')
    metadata['industry'] = get_param(metadata, 'industry')
    metadata['forecast_len'] = get_param(metadata, 'forecast_len')
    metadata['dtformat'] = get_param(metadata, 'dtformat')
    metadata['date_col_name'] = get_param(metadata, 'date_col_name')
    metadata['series_col_name'] = metadata['series_col_name'].split(
        ",") if 'series_col_name' in metadata else None
    metadata['covariables'] = metadata['covariables_col_name'].split(
        ",") if 'covariables_col_name' in metadata else None
    f.close()
    return metadata


def get_param(config, key):
    return config[key] if key in config else None


# def initparams(path=None):
#     try:
#         params = hyperctl.get_job_params()
#         data_base_path = params['data_path']
#         report_base_path = params['report_path']
#         mode = params['env']
#         max_trials = params['max_trials']
#     except:
#         # traceback.print_exc()
#         vers = hyperts.__version__
#         if path is None:
#             path = "../conf/hypertsbk.yaml"
#         f = open(path, 'r', encoding='utf-8')
#         config = yaml.load(f.read(), Loader=yaml.FullLoader)
#         data_base_path = config['data_path']
#         report_base_path = config['report_path']
#         mode = config['env']
#         max_trials = config['max_trials']
#         f.close()
#
#     return data_base_path, report_base_path, max_trials, mode, vers


def cal_metric(y_pred, y_test, date_col_name, series_col_name, covariables, metrics_target, task_calc_score):
    if series_col_name != None:
        y_pred = y_pred[series_col_name]
        y_test = y_test[series_col_name]

    if date_col_name in y_pred.columns:
        y_pred = y_pred.drop(columns=[date_col_name], axis=1)
    if date_col_name in y_test.columns:
        y_test = y_test.drop(columns=[date_col_name], axis=1)
    if covariables != None:
        y_test = y_test.drop(columns=[covariables], axis=1)
    hypertsmetric = metrics.calc_score(y_test, y_pred,
                                       metrics=metrics_target, task=task_calc_score)
    return hypertsmetric


def convertdf(df_train, df_test, Date_Col_Name, Series_Col_name, covariables, format):
    if Series_Col_name != None and covariables != None:
        Series_Col_name = Series_Col_name + covariables
    df_train[Date_Col_Name] = pd.to_datetime(df_train[Date_Col_Name], format=format)
    df_test[Date_Col_Name] = pd.to_datetime(df_test[Date_Col_Name], format=format)
    if Series_Col_name != None:
        df_train[Series_Col_name] = df_train[Series_Col_name].astype(float)
        df_test[Series_Col_name] = df_test[Series_Col_name].astype(float)

        Series_Col_name.append(Date_Col_Name)
        # split data
        df_train = df_train[Series_Col_name]
        df_test = df_test[Series_Col_name]

    else:
        for col in df_train.columns:
            if col == Date_Col_Name:
                continue
            df_train[col] = df_train[col].astype(float)
            df_test[col] = df_test[col].astype(float)
    return df_train, df_test


def to_series(x):
    try:
        value = pd.Series([float(item) for item in x.split('|')])
    except:
        print('error')
        value = pd.Series([float(item) for item in x.split('|')])
    return value


def convert_3d(df_train, df_test):
    df_train = df_train.copy()
    df_test = df_test.copy()
    Y_train = pd.DataFrame(df_train['y'])
    df_train = df_train.drop(['y'], axis=1)

    for col in df_train.columns:
        df_train[col] = df_train[col].map(to_series)
    df_train['y'] = Y_train

    Y_test = pd.DataFrame(df_test['y'])
    df_test = df_test.drop(['y'], axis=1)
    for col in df_test.columns:
        df_test[col] = df_test[col].map(to_series)
    df_test['y'] = Y_test

    return df_train, df_test


def bakup(params):
    shutil.copy(params.conf_path, params.result_dir_path())
