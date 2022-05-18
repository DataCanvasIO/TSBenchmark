import tsbenchmark as tsb
import tsbenchmark.api
from autots import AutoTS


def main():
    task = tsb.api.get_task()
    # task = tsb.api.get_local_task(data_path='/home/newbei/code/DAT/TSBenchmark/tsbenchmark/datas2',
    #                               dataset_id=890686, random_state=9527, max_trials=1, reward_metric='rmse')

    train_df = task.get_train().copy(deep=True)

    metric_weighting = { 'smape_weighting': 5}
    if task.reward_metric is not None:
        metric_weighting = {task.reward_metric + '_weighting': 5}
    max_trials = task.max_trials

    model = AutoTS(
        forecast_length=task.horizon,
        max_generations=max_trials,
        random_seed=task.random_state,
        metric_weighting=metric_weighting
    )

    if task.covariables_name is not None:
        train_df = train_df.drop(task.covariables_name, 1)

    import pandas as pd
    train_df[task.date_name] = pd.to_datetime(train_df[task.date_name])
    df_train = train_df.set_index([task.date_name])

    model = model.fit(
        df_train
    )
    df_forecast = model.predict().forecast

    tsb.api.send_report_data(task, df_forecast)


if __name__ == "__main__":
    main()
