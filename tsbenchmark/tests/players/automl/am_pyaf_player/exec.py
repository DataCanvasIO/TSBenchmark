import tsbenchmark as tsb
import tsbenchmark.api
import pyaf.ForecastEngine as autof
import pandas as pd

support_keys = ['MAPE', 'RMSE', 'MAE', 'SMAPE', 'ErrorMean', 'ErrorStdDev', 'R2', 'Pearson', 'MedAE', 'LnQ']


def main():
    task = tsb.api.get_task()

    # task = tsb.api.get_local_task(data_path='/home/newbei/code/DAT/TSBenchmark/tsbenchmark/datas2',
    #                               dataset_id=512754, random_state=9527, max_trials=1, reward_metric='rmse')


    train_df = task.get_train().copy(deep=True)
    train_df[task.date_name] = pd.to_datetime(train_df[task.date_name])
    lEngine = autof.cForecastEngine()
    lEngine.mSignalDecomposition.mOptions.mParallelMode = False
    lEngine.mOptions.mParallelMode = False
    reward_metric = [key for key in support_keys if key.lower() == task.reward_metric.lower()]
    if len(reward_metric) == 1:
        lEngine.mOptions.mModelSelection_Criterion = reward_metric[0]
    lEngine.train(iInputDS=train_df, iTime=task.date_name, iSignal=task.series_name, iHorizon=task.get_test().shape[0])
    df_forecast = lEngine.forecast(iInputDS=train_df, iHorizon=task.get_test().shape[0])
    y_pred = df_forecast[[f'{s}_Forecast' for s in task.series_name]].tail(task.get_test().shape[0])
    y_pred.columns = task.series_name

    tsb.api.send_report_data(task, y_pred)


if __name__ == "__main__":
    main()
