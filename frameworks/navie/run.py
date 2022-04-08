import pandas as pd


def trail(df_train, df_test, Date_Col_Name, Series_Col_name, forecast_length, format, task, metric, covariables,
          max_trials, random_state,reward_metric):
    y_pred_first = df_train[-1:].drop([Date_Col_Name], axis=1)
    y_pred_last = df_test.drop([Date_Col_Name], axis=1).shift(1)[1:]
    y_pred = pd.concat([y_pred_first, y_pred_last], axis=0)

    return y_pred, {}
