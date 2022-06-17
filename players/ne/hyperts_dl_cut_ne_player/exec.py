import tsbenchmark as tsb
import tsbenchmark.api
import tsbenchmark.util as util

def main():
    task = tsb.api.get_task()

    from hyperts.experiment import make_experiment
    train_df = task.get_train().copy(deep=True)

    point = util.cut_point_util().get_best_data_point(train_df[task.series_name], task.horizon)
    train_df = train_df[point:]
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
                          ensemble_size=None
                          )
    model = exp.run()
    X_test, y_test = model.split_X_y(task.get_test().copy())
    y_pred = model.predict(X_test)

    tsb.api.send_report_data(task, y_pred, best_params=exp.report_best_trial_params().to_json())


if __name__ == "__main__":
    main()
