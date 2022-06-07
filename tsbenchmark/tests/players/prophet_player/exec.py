from prophet import Prophet

import tsbenchmark as tsb
import tsbenchmark.api


def main():
    # task = tsb.api.get_local_task(data_path="/tmp/hdatasets", dataset_id=512754, random_state=9527, max_trials=1, reward_metric='rmse')
    task = tsb.api.get_task()
    df_train = task.get_train().copy(deep=True).rename(columns={task.date_name: 'ds', task.series_name[0]: 'y'}, inplace=False)
    df_test = task.get_test().copy(deep=True).rename(columns={task.date_name: 'ds', task.series_name[0]: 'y'}, inplace=False)
    model = Prophet()
    model.fit(df_train)

    df_prediction = model.predict(df_test)  # 评估模型

    tsb.api.send_report_data(task=task, y_pred=df_prediction['yhat'])  # 上报评估数据


if __name__ == "__main__":
    main()
