import tsbenchmark as tsb
import tsbenchmark.api
from autots import AutoTS

default_metric_weighting = {
    'smape_weighting': 5,
    'mae_weighting': 2,
    'rmse_weighting': 2,
    'made_weighting': 0.5,
    'mage_weighting': 0,
    'mle_weighting': 0,
    'imle_weighting': 0,
    'spl_weighting': 3,
    'containment_weighting': 0,
    'contour_weighting': 1,
    'runtime_weighting': 0.05,
}

def main():
    task = tsb.api.get_task()
    train_df = task.get_train().copy(deep=True)
    metric_key = (task.reward_metric + '_weighting').lower()
    metric_weighting = {metric_key: 5} if metric_key in default_metric_weighting else default_metric_weighting

    model = AutoTS(
        forecast_length=task.horizon,
        max_generations=task.max_trials,
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
