from tsbenchmark import metrics
from hypernets.utils import const


def test_calc_score():
    y = [4, 5, 6]
    y_pred = [1, 2, 3]
    results = metrics.calc_score(y, y_pred, metrics=['smape', 'rmse', 'mape', 'mae'], task=const.TASK_REGRESSION)
    assert 'smape' in results and results['smape'] is not None
    assert 'rmse' in results and results['rmse'] is not None
    assert 'mape' in results and results['mape'] is not None
    assert 'mae' in results and results['mae'] is not None
