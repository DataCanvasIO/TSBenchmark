import tsbenchmark as tsb
import tsbenchmark.api
import json

from prophet import Prophet

params_space = [
    {"n_changepoints": 25, "changepoint_range": 0.8, "seasonality_mode": 'additive'},
    {"n_changepoints": 10, "changepoint_range": 0.95, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 5, "changepoint_range": 0.8, "seasonality_mode": 'additive'},
    {"n_changepoints": 8, "changepoint_range": 0.5, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 16, "changepoint_range": 0.6, "seasonality_mode": 'additive'},
    {"n_changepoints": 4, "changepoint_range": 0.8, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 2, "changepoint_range": 0.9, "seasonality_mode": 'additive'},
    {"n_changepoints": 3, "changepoint_range": 0.4, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 5, "changepoint_range": 0.8, "seasonality_mode": 'additive'},
    {"n_changepoints": 25, "changepoint_range": 0.7, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 10, "changepoint_range": 0.5, "seasonality_mode": 'additive'},
    {"n_changepoints": 5, "changepoint_range": 0.5, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 8, "changepoint_range": 0.8, "seasonality_mode": 'additive'},
    {"n_changepoints": 15, "changepoint_range": 0.6, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 4, "changepoint_range": 0.3, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 2, "changepoint_range": 0.4, "seasonality_mode": 'additive'},
    {"n_changepoints": 3, "changepoint_range": 0.3, "seasonality_mode": 'multiplicative'},
    {"n_changepoints": 5, "changepoint_range": 0.3, "seasonality_mode": 'additive'},
    {"n_changepoints": 25, "changepoint_range": 0.5, "seasonality_mode": 'multiplicative'},
]


def main():
    # task = tsb.api.get_task()
    task = tsb.api.get_local_task(data_path=r'D:\workspace\DAT\benchmark\hyperts\data\tsbenchmark-dev',
                                  dataset_id=514906, random_state=9527, max_trials=1, reward_metric='smape')
    df_train = task.get_train().copy(deep=True)
    df_train.rename(columns={task.date_name: 'ds', task.series_name[0]: 'y'}, inplace=True)

    df_test = task.get_test().copy(deep=True)
    df_test.rename(columns={task.date_name: 'ds', task.series_name[0]: 'y'}, inplace=True)

    for params in params_space:
        model = Prophet(n_changepoints=params['n_changepoints'],
                        changepoint_range=params['changepoint_range'], seasonality_mode=params['seasonality_mode'])
        model.fit(df_train)

        df_prediction = model.predict(df_test)

        df_result = df_prediction[['yhat']].copy(deep=True)
        df_result.rename(columns={'yhat': task.series_name[0]}, inplace=True)

        tsb.api.send_report_data(task=task, y_pred=df_result, sub_result=True, key_params=json.dumps(params))


if __name__ == "__main__":
    main()
