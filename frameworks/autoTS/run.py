from autots import AutoTS


def trail(df_train, df_test, Date_Col_Name, Series_Col_name, forecast_length, format, task, metric, covariables,
          max_trials, random_state):
    model = AutoTS(
        forecast_length=forecast_length,
        max_generations=max_trials,
        model_list="fast",  # "superfast", "default", "fast_parallel"
        transformer_list="fast",  # "superfast",
        random_seed=random_state
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
