# Loading the package
from utils.util import convertdf
import time
from hyperts.framework.search_space.macro_search_space import DLForecastSearchSpace

task_trail = 'forecast'


def trail(df_train, df_test, Date_Col_Name, Series_Col_name, forecast_length, format, task, metric, covariables,
          max_trials, random_state,reward_metric):
    y_test, run_kwargs, time_cost, y_pred = _trail(Date_Col_Name, Series_Col_name, covariables,
                                                   df_test, df_train, format, metric, task,
                                                   max_trials, random_state,reward_metric)

    return y_pred, run_kwargs


def _trail(Date_Col_Name, Series_Col_name, covariables, df_test, df_train, format, metric, task, max_trials,
           random_state,reward_metric):
    df_train, df_test = convertdf(df_train, df_test, Date_Col_Name, Series_Col_name, covariables, format)
    time2_start = time.time()
    from hyperts.experiment import make_experiment

    train_df = df_train.copy(deep=True)

    search_space = DLForecastSearchSpace(
        task=task, timestamp=Date_Col_Name,
        enable_deepar=True,
        enable_hybirdrnn=False,
        enable_lstnet=False,
    )

    exp = make_experiment(train_df,
                          mode='dl',
                          timestamp=Date_Col_Name,
                          task=task,
                          reward_metric=reward_metric,
                          timestamp_format=format,
                          covariables=covariables,
                          max_trials=max_trials,
                          optimize_direction='min',
                          verbose=1,
                          log_level='INFO',
                          early_stopping_rounds=30,
                          early_stopping_time_limit=0,
                          random_state=random_state,
                          dl_gpu_usage_strategy=1,
                          search_space=search_space
                          )

    model = exp.run()
    X_test, y_test = model.split_X_y(df_test.copy())
    y_pred = model.predict(X_test)
    time2_end = time.time()
    params = {}
    params['run_kwargs']=exp.run_kwargs
    params['report_best_trial_params'] = exp.report_best_trial_params()

    return df_test, params, (time2_end - time2_start), y_pred
