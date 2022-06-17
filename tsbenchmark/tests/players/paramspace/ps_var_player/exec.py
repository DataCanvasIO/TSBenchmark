import tsbenchmark as tsb
import tsbenchmark.api
import json
import pandas as pd
import traceback

from statsmodels.tsa.vector_ar.var_model import VAR

params_space = [
    {"maxlags": None, "ic": "aic", "trend": 'c'},
    {"maxlags": 12, "ic": "bic", "trend": 'ct'},
    {"maxlags": 6, "ic": None, "trend": 'ctt'},
    {"maxlags": 18, "ic": "fpe", "trend": 'nc'},
    {"maxlags": 4, "ic": "hqic", "trend": 'n'},
    {"maxlags": 12, "ic": "bic", "trend": 'n'},
    {"maxlags": 8, "ic": "fpe", "trend": 'n'},
    {"maxlags": 25, "ic": "aic", "trend": 'nc'},
    {"maxlags": 24, "ic": None, "trend": 'n'},
    {"maxlags": 12, "ic": "fpe", "trend": 'ctt'},
    {"maxlags": 12, "ic": "aic", "trend": 'ct'},
    {"maxlags": 12, "ic": "bic", "trend": 'n'},
    {"maxlags": 10, "ic": None, "trend": 'ct'},
    {"maxlags": 11, "ic": "hqic", "trend": 'c'},
    {"maxlags": 10, "ic": "bic", "trend": 'c'},
    {"maxlags": 11, "ic": "fpe", "trend": 'n'},
    {"maxlags": 10, "ic": None, "trend": 'nc'},
    {"maxlags": 8, "ic": "hqic", "trend": 'ct'},
    {"maxlags": 12, "ic": "fpe", "trend": 'n'},
    {"maxlags": 8, "ic": "aic", "trend": 'c'},
]


def main():
    # task = tsb.api.get_task()
    task = tsb.api.get_local_task(data_path=r'D:\workspace\DAT\benchmark\hyperts\data\tsbenchmark-dev',
                                  dataset_id=61807, random_state=9527, max_trials=1, reward_metric='smape')
    df_train = task.get_train().copy(deep=True)

    df_train = df_train[task.series_name]
    for params in params_space:
        try:
            model = VAR(df_train)
            model_fit = model.fit(maxlags=params['maxlags'], ic=params['ic'], trend=params['trend'])
            # make prediction
            yhat = model_fit.forecast(model_fit.y, steps=task.horizon)
            pred = pd.DataFrame(yhat, columns=task.series_name)

            tsb.api.send_report_data(task=task, y_pred=pred, sub_result=True, key_params=json.dumps(params))
        except:
            traceback.print_exc()


if __name__ == "__main__":
    main()
