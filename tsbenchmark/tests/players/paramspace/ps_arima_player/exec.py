import tsbenchmark as tsb
import tsbenchmark.api
import json
import pandas as pd

import statsmodels.api as sm

params_space = [{"order": (12, 2, 6), "trend": "c", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": True},
                {"order": (12, 1, 6), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": True},
                {"order": (12, 0, 6), "trend": "c", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": True},
                {"order": (6, 2, 3), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": True,
                 "concentrate_scale": True},
                {"order": (6, 1, 3), "trend": "c", "simple_differencing": True, "use_exact_diffuse": False,
                 "concentrate_scale": True},
                {"order": (6, 0, 3), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": True},
                {"order": (1, 1, 1), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": True},
                {"order": (1, 0, 1), "trend": "c", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": True},
                {"order": (12, 2, 0), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": True},
                {"order": (12, 1, 0), "trend": "c", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": True},

                {"order": (12, 2, 6), "trend": "c", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                {"order": (12, 1, 6), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                {"order": (10, 1, 6), "trend": "c", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                {"order": (4, 2, 3), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": True,
                 "concentrate_scale": False},
                {"order": (6, 1, 3), "trend": "c", "simple_differencing": True, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                {"order": (5, 0, 3), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                {"order": (1, 1, 1), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                {"order": (1, 0, 1), "trend": "c", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                {"order": (8, 2, 0), "trend": "ct", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                {"order": (12, 1, 0), "trend": "c", "simple_differencing": False, "use_exact_diffuse": False,
                 "concentrate_scale": False},
                ]


def main():
    # task = tsb.api.get_task()
    task = tsb.api.get_local_task(data_path=r'D:\workspace\DAT\benchmark\hyperts\data\tsbenchmark-dev',
                                  dataset_id=514906, random_state=9527, max_trials=1, reward_metric='smape')
    for params in params_space:
        mod = sm.tsa.statespace.SARIMAX(task.get_train()[task.series_name],
                                        order=params["order"],
                                        enforce_stationarity=False,
                                        enforce_invertibility=False)
        results = mod.fit()
        pred = results.get_forecast(task.horizon)
        pred = pd.DataFrame(pred.predicted_mean, columns=task.series_name)
        tsb.api.send_report_data(task, pred, key_params=json.dumps(params), sub_result=True)


if __name__ == "__main__":
    main()
