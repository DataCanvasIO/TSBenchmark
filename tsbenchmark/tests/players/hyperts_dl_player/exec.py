import tsbenchmark as tsb
import tsbenchmark.api
import time
from hyperts.utils import metrics


def cal_metric(y_pred, y_test, date_col_name, series_col_name, covariables, metrics_target, task_calc_score):
    if series_col_name != None:
        y_pred = y_pred[series_col_name]
        y_test = y_test[series_col_name]

    if date_col_name in y_pred.columns:
        y_pred = y_pred.drop(columns=[date_col_name], axis=1)
    if date_col_name in y_test.columns:
        y_test = y_test.drop(columns=[date_col_name], axis=1)
    if covariables != None:
        y_test = y_test.drop(columns=[covariables], axis=1)
    hypertsmetric = metrics.calc_score(y_test, y_pred,
                                       metrics=metrics_target, task=task_calc_score)
    return hypertsmetric


def main():
    task = tsb.api.get_task()
    from hyperts.experiment import make_experiment
    train_df = task.get_train().copy(deep=True)
    time_start = time.time()
    exp = make_experiment(train_df,
                          mode='dl',
                          timestamp=task.date_name,
                          task=task.task,
                          reward_metric=task.reward_metric,
                          timestamp_format=task.dtformat,
                          covariables=task.covariables_name,
                          max_trials=1, #todo
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

    metrics = cal_metric(y_pred, task.get_test(), task.date_name, task.series_name,
                         task.covariables_name,
                         ['smape', 'mape', 'rmse', 'mae'], 'regression')

    duration = time.time() - time_start

    report_data = {
        'duration': duration,
        'y_predict': y_pred[task.series_name].to_json(orient='records')[1:-1].replace('},{', '} {'),
        'y_real': y_test.to_json(orient='records')[1:-1].replace('},{', '} {'),
        'metrics': metrics
    }
    tsb.api.report_task(report_data=report_data)


if __name__ == "__main__":
    main()
