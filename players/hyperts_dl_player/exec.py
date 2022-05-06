import tsbenchmark as tsb
import tsbenchmark.api


def main():
    task = tsb.api.get_task()
    from hyperts.experiment import make_experiment
    train_df = task.get_train().copy(deep=True)
    exp = make_experiment(train_df,
                          mode='dl',
                          timestamp=task.date_name,
                          task=task.task,
                          reward_metric=task.reward_metric,
                          timestamp_format=task.dtformat,
                          covariables=task.covariables_name,
                          max_trials=1,  # todo
                          optimize_direction='min',
                          verbose=1,
                          log_level='INFO',
                          early_stopping_rounds=30,
                          early_stopping_time_limit=0,
                          random_state=task.random_state,
                          dl_gpu_usage_strategy=1
                          )
    model = exp.run()
    X_test, y_test = model.split_X_y(task.get_test().copy())
    y_pred = model.predict(X_test)
    tsb.api.report_task(report_data=task.make_report_data(y_pred))


if __name__ == "__main__":
    main()
