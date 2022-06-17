import tsbenchmark as tsb
import tsbenchmark.api
from fedot.api.main import Fedot
from fedot.core.repository.tasks import Task, TaskTypesEnum, TsForecastingParams
from fedot.core.data.data import InputData
from fedot.core.data.data_split import train_test_data_setup
import pandas as pd

def main():
    task = tsb.api.get_task()
    # task = tsb.api.get_local_task(data_path='/home/newbei/code/DAT/TSBenchmark/tsbenchmark/datas2',
    #                               dataset_id=512754, random_state=9527, max_trials=1, reward_metric='rmse')

    train_df = task.get_train().copy(deep=True)
    test_df = task.get_test().copy(deep=True)
    test_df[task.series_name] = -9999
    full_df = pd.concat([train_df, test_df], 0)
    full_df.to_csv('full_tmp.csv', index=False)

    fedot_task = Task(TaskTypesEnum.ts_forecasting, TsForecastingParams(forecast_length=test_df.shape[0]))
    input_data = InputData.from_csv_time_series(fedot_task, 'full_tmp.csv', target_column=task.series_name[0])
    train_data, test_data = train_test_data_setup(input_data)
    model = Fedot(problem='ts_forecasting', task_params=fedot_task.task_params, timeout=1, seed=task.random_state)
    chain = model.fit(features=train_data)
    forecast = model.predict(features=test_data)
    df_forecast = pd.DataFrame(forecast.reshape(-1, 1), columns=[task.series_name])

    tsb.api.send_report_data(task, df_forecast)


if __name__ == "__main__":
    main()
