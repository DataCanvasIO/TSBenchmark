import tsbenchmark as tsb
import tsbenchmark.api

def main():
    # task = tsb.api.get_task()
    task = tsb.api.get_local_task(data_path='/home/newbei/code/DAT/TSBenchmark/tsbenchmark/datas2',
                                  dataset_id=890686, random_state=9527, max_trails=1, reward_metric='rmse')

    from hyperts.experiment import make_experiment
    train_df = task.get_train().copy(deep=True)
    exp = make_experiment(train_df,
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
                          random_state=task.random_state
                          )
    model = exp.run()
    X_test, y_test = model.split_X_y(task.get_test().copy())
    y_pred = model.predict(X_test)

    report_data = tsb.api.make_report_data(task, y_pred, best_params=exp.report_best_trial_params().to_json())
    tsb.api.report_task(report_data)


if __name__ == "__main__":
    main()
