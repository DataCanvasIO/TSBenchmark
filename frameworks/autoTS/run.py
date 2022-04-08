from autots import AutoTS


def trail(df_train, df_test, Date_Col_Name, Series_Col_name, forecast_length, format, task, metric, covariables,
          max_trials, random_state, reward_metric):
    metric_weighting = {
                           'smape_weighting': 5,
                           'mae_weighting': 2,
                           'rmse_weighting': 2,
                           'made_weighting': 0,
                           'containment_weighting': 0,
                           'runtime_weighting': 0.05,
                           'spl_weighting': 2,
                           'contour_weighting': 1,
                       },

    if reward_metric != None:
        metric_weighting = {reward_metric + '_weighting': 5}

    model = AutoTS(
        forecast_length=forecast_length,
        max_generations=max_trials,
        model_list="fast",  # "superfast", "default", "fast_parallel"
        transformer_list="fast",  # "superfast",
        random_seed=random_state,
        metric_weighting=metric_weighting
    )
    if covariables != None:
        df_train = df_train.drop(covariables, 1)

    model = model.fit(
        df_train,
        date_col=Date_Col_Name,
        value_col=Series_Col_name[0]
    )

    prediction = model.predict().forecast
    return prediction, {}
