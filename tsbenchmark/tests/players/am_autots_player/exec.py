import tsbenchmark as tsb
import tsbenchmark.api
from autots import AutoTS
import pandas as pd


def main():
    # task = tsb.api.get_task()

    from tsbenchmark.tsloader import TSTaskLoader
    from tsbenchmark.tasks import TSTask
    data_path = '/home/newbei/code/DAT/TSBenchmark/tsbenchmark/datas1'
    taskloader = TSTaskLoader(data_path)
    task_config = taskloader.load(890686)
    task = TSTask(task_config, random_state=9527, max_trails=1, reward_metric='rmse')

    train_df = task.get_train().copy(deep=True)
    metric_weighting = {task.reward_metric + '_weighting': 5}

    model = AutoTS(
        forecast_length=task.horizon,
        max_generations=task.max_trails,
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

    tsb.api.report_task(
        report_data=task.make_report_data(df_forecast))


if __name__ == "__main__":
    main()
