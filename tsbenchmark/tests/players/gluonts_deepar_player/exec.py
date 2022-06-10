from gluonts.mx.trainer import Trainer
from gluonts.dataset import common
from gluonts.model import deepar
from gluonts.evaluation import make_evaluation_predictions

import tsbenchmark as tsb
import tsbenchmark.api
import pandas as pd


def main():
    # task = tsb.api.get_task()
    task = tsb.api.get_local_task(data_path=r'D:\workspace\DAT\benchmark\hyperts\data\tsbenchmark-dev',
                                  dataset_id=512754, random_state=9527, max_trials=1, reward_metric='smape')

    df_train = task.get_train().bfill()
    df_train.reset_index(inplace=True, drop=True)
    df_train = df_train[task.series_name]
    data = common.ListDataset([{'start': 0, 'target': df_train[col]} for col in task.series_name],
                              freq=task.freq)

    trainer = Trainer(epochs=1)
    estimator = deepar.DeepAREstimator(
        freq=task.freq, prediction_length=task.horizon, trainer=trainer)
    predictor = estimator.train(training_data=data)

    forcast_it, ts_it = make_evaluation_predictions(
        dataset=data,
        predictor=predictor,
        num_samples=task.horizon,
    )
    fore = list(forcast_it)
    if len(fore) == 1:
        y_pred = pd.DataFrame(fore[0].mean)
    else:
        y_pred = pd.DataFrame([f.mean for f in fore]).T
    y_pred.columns = task.series_name
    tsb.api.send_report_data(task, y_pred)


if __name__ == "__main__":
    main()
