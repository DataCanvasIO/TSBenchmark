from darts import TimeSeries
from darts.models import RNNModel

import tsbenchmark as tsb
import tsbenchmark.api
import pandas as pd


def main():
    # task = tsb.api.get_task()
    task = tsb.api.get_local_task(data_path=r'D:\workspace\DAT\benchmark\hyperts\data\tsbenchmark-dev',
                                  dataset_id=512754, random_state=9527, max_trials=1, reward_metric='smape')

    df_train = task.get_train().bfill()
    df_train.reset_index(inplace=True, drop=True)
    df_train = df_train[task.series_name]
    df_train = pd.concat([task.get_train()[[task.date_name]], df_train], 1)
    series = TimeSeries.from_dataframe(df_train, task.date_name, task.series_name, freq=task.freq)
    model = RNNModel(input_chunk_length=task.horizon,
                     output_chunk_length=task.horizon, random_state=task.random_state, model="LSTM")
    model.fit(series)
    y_pred = model.predict(task.horizon)
    y_pred = pd.DataFrame(y_pred.values())
    y_pred.columns = task.series_name
    tsb.api.send_report_data(task, y_pred)


if __name__ == "__main__":
    main()
