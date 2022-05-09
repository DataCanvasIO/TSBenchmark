import pyaf.ForecastEngine as autof
import pandas as pd


def trail(df_train, df_test, Date_Col_Name, Series_Col_name, forecast_length, format, task, metric, covariables,
          max_trials, random_state, reward_metric):
    df_train[Date_Col_Name] = pd.to_datetime(df_train[Date_Col_Name])
    df_test[Date_Col_Name] = pd.to_datetime(df_test[Date_Col_Name])
    lEngine = autof.cForecastEngine()
    lEngine.mSignalDecomposition.mOptions.mParallelMode = False
    lEngine.mOptions.mParallelMode = False
    lEngine.mOptions.mModelSelection_Criterion = 'SMAPE' # not support rmse
    lEngine.train(iInputDS=df_train, iTime=Date_Col_Name, iSignal=Series_Col_name, iHorizon=df_test.shape[0])
    df_forecast = lEngine.forecast(iInputDS=df_train, iHorizon=df_test.shape[0])
    df_forecast = df_forecast[[f'{s}_Forecast' for s in Series_Col_name]].tail(df_test.shape[0])
    df_forecast.columns = Series_Col_name
    return df_forecast, {}
