import tsbenchmark as tsb
import tsbenchmark.api
import time
from hyperts.utils import metrics
import pyaf.ForecastEngine as autof
import pandas as pd


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


def main():
    task = tsb.api.get_task()
    train_df = task.get_train().copy(deep=True)
    time_start = time.time()
    train_df[task.date_name] = pd.to_datetime(train_df[task.date_name])
    lEngine = autof.cForecastEngine()
    lEngine.mSignalDecomposition.mOptions.mParallelMode = False
    lEngine.mOptions.mParallelMode = False
    lEngine.mOptions.mModelSelection_Criterion = 'SMAPE'  # not support rmse
    lEngine.train(iInputDS=train_df, iTime=task.date_name, iSignal=task.series_name, iHorizon=task.get_test().shape[0])
    df_forecast = lEngine.forecast(iInputDS=train_df, iHorizon=task.get_test().shape[0])
    y_pred = df_forecast[[f'{s}_Forecast' for s in task.series_name]].tail(task.get_test().shape[0])
    y_pred.columns = task.series_name
    y_true = task.get_test()[task.series_name]
    metrics = cal_metric(y_pred, y_true, task.date_name, task.series_name,
                         task.covariables_name,
                         ['smape', 'mape', 'rmse', 'mae'], 'regression')

    duration = time.time() - time_start

    report_data = {
        'duration': duration,
        'y_predict': y_pred[task.series_name].to_json(orient='records')[1:-1].replace('},{', '} {'),
        'y_real': y_true.to_json(orient='records')[1:-1].replace('},{', '} {'),
        'metrics': metrics
    }
    tsb.api.report_task(report_data=report_data)


if __name__ == "__main__":
    main()
