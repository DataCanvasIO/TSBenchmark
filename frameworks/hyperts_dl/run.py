# Loading the package
from utils.util import convertdf
import time

types = ['multivariate-forecast']
data_sizes = ['small', 'medium', 'large']
metrics_target = ['smape', 'mape', 'rmse', 'mae']
task_calc_score = 'regression'
task_trail = 'forecast'


def trail(df_train, df_test, Date_Col_Name, Series_Col_name, forecast_length, format, task, metric, covariables,
          max_trials,random_state):
    y_test, run_kwargs, time_cost, y_pred = _trail(Date_Col_Name, Series_Col_name, covariables,
                                                   df_test, df_train, format, metric, task_trail,
                                                   max_trials,random_state)
    if covariables != None and len(covariables) > 0:
        df_test = df_test.drop(covariables, 1)
    # Metrics
    # return metrics.calc_score(y_test.drop(columns=[Date_Col_Name], axis=1),
    #                           y_pred.drop(columns=[Date_Col_Name], axis=1),
    #                           metrics=metrics_target, task=task_calc_score), time_cost, run_kwargs
    return y_pred, run_kwargs


def _trail(Date_Col_Name, Series_Col_name, covariables, df_test, df_train, format, metric, task, max_trials, random_state):
    df_train, df_test = convertdf(df_train, df_test, Date_Col_Name, Series_Col_name, covariables, format)
    time2_start = time.time()
    from hyperts.experiment import make_experiment
    from hyperts.utils import consts

    train_df = df_train.copy(deep=True)

    exp = make_experiment(train_df,
                          mode='dl',
                          timestamp=Date_Col_Name,
                          task=task,
                          reward_metric=metric,
                          timestamp_format=format,
                          covariables=covariables,
                          max_trials=max_trials,
                          optimize_direction='min',
                          verbose=1,
                          log_level='INFO',
                          early_stopping_rounds=30,
                          early_stopping_time_limit=0,
                          random_state=random_state,
                          dl_gpu_usage_strategy=1
                          )

    model = exp.run()
    X_test, y_test = model.split_X_y(df_test.copy())
    y_pred = model.predict(X_test)
    time2_end = time.time()

    return df_test, exp.run_kwargs, (time2_end - time2_start), y_pred