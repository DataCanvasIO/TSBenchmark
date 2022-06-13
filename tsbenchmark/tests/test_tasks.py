from tsbenchmark.tasks import get_task_config, list_task_configs
import os

HERE = os.path.dirname(__file__)


def test_get_task_config():
    tc = get_task_config(512754)
    assert tc.id == 512754


def test_list_task_configs_all():
    task_configs = list_task_configs(cache_path=os.path.join(HERE, "datas"),
                                     task_types=None,
                                     dataset_sizes=None,
                                     task_ids=None, dataset_ids=None)
    assert len(task_configs) == 19


def test_list_task_configs_by_types():
    task_configs = list_task_configs(cache_path=os.path.join(HERE, "datas"),
                                     task_types=['univariate-forecast'],
                                     dataset_sizes=None,
                                     task_ids=None, dataset_ids=None)
    for task_config in task_configs:
        assert task_config.task == 'univariate-forecast'
    assert len(task_configs) == 12


def test_list_task_configs_by_dataset_sizes():
    task_configs = list_task_configs(cache_path=os.path.join(HERE, "datas"),
                                     task_types=None,
                                     dataset_sizes=['small'],
                                     task_ids=None, dataset_ids=None)
    for task_config in task_configs:
        assert task_config.data_size == 'small'
    assert len(task_configs) == 14


def test_list_task_configs_by_task_ids():
    task_configs = list_task_configs(cache_path=os.path.join(HERE, "datas"),
                                     task_types=None,
                                     dataset_sizes=None,
                                     task_ids=['631753'], dataset_ids=None)
    assert len(task_configs) == 1
    assert task_configs[0].id == '631753'


def test_list_task_configs_by_dataset_ids():
    task_configs = list_task_configs(cache_path=os.path.join(HERE, "datas"),
                                     task_types=None,
                                     dataset_sizes=None,
                                     task_ids=None, dataset_ids=['631753'] )
    assert len(task_configs) == 1
    assert task_configs[0].dataset_id == '631753'


def test_list_task_configs_by_types_and_dataset_sizes():
    task_configs = list_task_configs(cache_path=os.path.join(HERE, "datas"),
                                     task_types=['univariate-forecast'],
                                     dataset_sizes=['small'],
                                     task_ids=None, dataset_ids=None)
    for task_config in task_configs:
        assert task_config.task == 'univariate-forecast'
        assert task_config.data_size == 'small'
    assert len(task_configs) == 10
