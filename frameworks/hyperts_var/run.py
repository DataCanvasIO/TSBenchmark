from utils.util import convertdf
import time
from hyperts.framework.search_space.macro_search_space import StatsForecastSearchSpace


def trail(df_train, df_test, Date_Col_Name, Series_Col_name, forecast_length, format, task, metric, covariables,
          max_trials, random_state, reward_metric):
    # load data
    df_test, run_kwargs, time_cost, y_pred = trail_forecast(Date_Col_Name, Series_Col_name, covariables, df_test,
                                                            df_train, format, metric, task, max_trials, random_state,
                                                            reward_metric)
    if covariables != None and len(covariables) > 0:
        df_test = df_test.drop(covariables, 1)
    return y_pred, run_kwargs


def trail_forecast(Date_Col_Name, Series_Col_name, covariables, df_test, df_train, format, metric, task, max_trials,
                   random_state, reward_metric):
    df_train, df_test = convertdf(df_train, df_test, Date_Col_Name, Series_Col_name, covariables, format)

    time2_start = time.time()
    from hyperts.experiment import make_experiment
    from hyperts.utils import consts
    train_df = df_train.copy(deep=True)

    search_space = StatsForecastSearchSpace(
        task=task,
        timestamp=Date_Col_Name,
        enable_prophet=False,
        enable_arima=False,
        enable_var=True
    )

    exp = make_experiment(train_df,
                          timestamp=Date_Col_Name,
                          task=task,
                          reward_metric=reward_metric,
                          timestamp_format=format,
                          covariables=covariables,
                          max_trials=max_trials,
                          optimize_direction='min',
                          verbose=1,
                          log_level='INFO',
                          random_state=random_state,
                          search_space=search_space
                          )

    model = exp.run()
    y_pred = model.predict(df_test)
    time2_end = time.time()

    return df_test, exp.run_kwargs, (time2_end - time2_start), y_pred

# run(types, data_sizes, trail)
