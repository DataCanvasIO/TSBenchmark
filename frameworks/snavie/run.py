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


def trail(df_train, df_test, Date_Col_Name, Series_Col_name, forecast_length, format, task, metric, covariables,
          max_trials, random_state, reward_metric):
    Series_Col_name = [Series_Col_name] if isinstance(Series_Col_name, str) else Series_Col_name
    periods = []

    for col in Series_Col_name:
        period = fft_infer_period(df_train[col])
        periods.append(period)

    df_full = pd.concat([df_train[-np.max(periods):], df_test], 0)
    df_predict = pd.DataFrame()
    for i in range(len(Series_Col_name)):
        predict = df_full[col].shift(periods[i]).values[-df_test.shape[0]:]
        df_predict = pd.concat([df_predict, pd.Series(predict)], 1)
    df_predict.columns = [Series_Col_name] if isinstance(Series_Col_name, str) else Series_Col_name

    return df_predict, {}
