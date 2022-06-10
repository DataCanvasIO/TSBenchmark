import tsbenchmark as tsb
import tsbenchmark.api
from hyperts.framework.search_space.macro_search_space import DLForecastSearchSpace


def main():
    task = tsb.api.get_task()
    search_space = DLForecastSearchSpace(
        task=task.task, timestamp=task.date_name,
        enable_deepar=True,
        enable_hybirdrnn=False,
        enable_lstnet=False,
    )
    from hyperts.experiment import make_experiment
    train_df = task.get_train().copy(deep=True)
    exp = make_experiment(train_df,
                          mode='dl',
                          timestamp=task.date_name,
                          task=task.task,
                          reward_metric=task.reward_metric,
                          timestamp_format=task.dtformat,
                          covariables=task.covariables_name,
                          max_trials=task.max_trials,
                          optimize_direction='min',
                          verbose=1,
                          log_level='INFO',
                          early_stopping_rounds=0,
                          early_stopping_time_limit=0,
                          random_state=task.random_state,
                          dl_gpu_usage_strategy=1,
                          search_space=search_space
                          )
    model = exp.run()
    X_test, y_test = model.split_X_y(task.get_test().copy())
    y_pred = model.predict(X_test)

    tsb.api.send_report_data(task, y_pred, best_params=exp.report_best_trial_params().to_json())


if __name__ == "__main__":
    main()
