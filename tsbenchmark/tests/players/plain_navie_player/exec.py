import tsbenchmark as tsb
import tsbenchmark.api
import pandas as pd


class Navie(object):

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
    task = tsb.api.get_task()
    snavie = Navie().fit(task.get_train(), task.series_name)
    df_forecast = snavie.predict(task.horizon)

    tsb.api.send_report_data(task, df_forecast)


if __name__ == "__main__":
    main()
