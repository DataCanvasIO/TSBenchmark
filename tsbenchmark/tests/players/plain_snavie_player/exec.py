import tsbenchmark as tsb
import tsbenchmark.api
import pandas as pd
import numpy as np


def fft_infer_period(data: pd.DataFrame):
    data = data.values.reshape(-1, )
    ft = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(len(data), 1)
    mags = abs(ft)
    inflection = np.diff(np.sign(np.diff(mags)))
    peaks = (inflection < 0).nonzero()[0] + 1
    peak = peaks[mags[peaks].argmax()]
    signal_freq = freqs[peak]
    period = int(1 / signal_freq)
    return period


class Snavie(object):

    def __init__(self):
        self.periods = []
        self.series_name = []
        self.history_data = []

    def fit(self, df_train: pd.DataFrame, series_name):
        self.series_name = series_name
        for col in series_name:
            period = fft_infer_period(df_train[col])
            self.periods.append(period)
            self.history_data.append(df_train[col][-period:])

        return self

    def predict(self, horizon: int):
        results = []
        for i in range(len(self.series_name)):
            result = []
            horizon_tmp = horizon
            while horizon_tmp - self.periods[i] > 0:
                result.extend(self.history_data[i])
                horizon_tmp = horizon_tmp - self.periods[i]

            if horizon_tmp > 0:
                result.extend(self.history_data[i][:horizon_tmp])

            results.append(result)
        df_forecast = pd.DataFrame(results).T
        df_forecast.columns = self.series_name
        return df_forecast


def main():
    task = tsb.api.get_task()
    snavie = Snavie().fit(task.get_train(), task.series_name)
    df_forecast = snavie.predict(task.horizon)

    tsb.api.send_report_data(task, df_forecast)


if __name__ == "__main__":
    main()
