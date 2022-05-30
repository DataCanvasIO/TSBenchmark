import tsbenchmark as tsb
import tsbenchmark.api
import pandas as pd


class Navie(object):
    '''
    Naive Methods such as assuming the predicted value at time ‘t’ to be the actual value of the variable at time ‘t-1’.
    This is a simple method as a baseline for benchmark and a simple demo.
    '''

    def __init__(self):
        self.history_data = None

    def fit(self, df_train: pd.DataFrame, series_name):
        self.history_data = df_train[-1:][series_name]
        return self

    def predict(self, horizon: int):
        import numpy as np
        df_predcit = pd.DataFrame(np.repeat(self.history_data.values, horizon, axis=0))
        df_predcit.columns = self.history_data.columns
        return df_predcit


def main():
    '''
        Main steps:
        1. Get a task.
            Get the the task,it will return a TSTask. Player will get the data and metadata from the it.
            You can get more info about TSTask in tasks.py
            When you are in develop mode, you can get a test task by  tsb.api.get_local_task.
                task = tsb.api.get_local_task(data_path='~/datas', dataset_id=512754, random_state=9527, max_trials=1, reward_metric='smape')
        2. Train model.
        3. Predict for task.horizon or task.getTest().
        4. Send report with the result from step 3.

    '''

    # 1. Get a task
    task = tsb.api.get_task()

    # 2. Train model
    snavie = Navie().fit(task.get_train(), task.series_name)

    # 3. Predict
    df_forecast = snavie.predict(task.horizon)

    # 4. Send report
    tsb.api.send_report_data(task, df_forecast)


if __name__ == "__main__":
    main()
