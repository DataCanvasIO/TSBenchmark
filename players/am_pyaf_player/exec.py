import tsbenchmark as tsb
import tsbenchmark.api
import pyaf.ForecastEngine as autof
import pandas as pd


def main():
    task = tsb.api.get_task()
    train_df = task.get_train().copy(deep=True)
    train_df[task.date_name] = pd.to_datetime(train_df[task.date_name])
    lEngine = autof.cForecastEngine()
    lEngine.mSignalDecomposition.mOptions.mParallelMode = False
    lEngine.mOptions.mParallelMode = False
    lEngine.mOptions.mModelSelection_Criterion = 'SMAPE'  # not support rmse
    lEngine.train(iInputDS=train_df, iTime=task.date_name, iSignal=task.series_name, iHorizon=task.get_test().shape[0])
    df_forecast = lEngine.forecast(iInputDS=train_df, iHorizon=task.get_test().shape[0])
    y_pred = df_forecast[[f'{s}_Forecast' for s in task.series_name]].tail(task.get_test().shape[0])
    y_pred.columns = task.series_name

    report_data = tsb.api.make_report_data(task, y_pred)
    tsb.api.report_task(report_data)


if __name__ == "__main__":
    main()
