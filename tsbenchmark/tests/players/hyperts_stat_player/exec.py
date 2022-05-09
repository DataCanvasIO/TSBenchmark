import tsbenchmark as tsb
import tsbenchmark.api
import json


def main():
    task = tsb.api.get_task()
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

    tsb.api.report_task(
        report_data=task.make_report_data(y_pred, key_params=json.dumps(exp.run_kwargs),
                                          best_params=exp.report_best_trial_params().to_json()))


if __name__ == "__main__":
    main()
