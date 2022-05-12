from tsbenchmark.tasks import get_task_config


def test_get_task_config():
    tc = get_task_config(694826)
    assert tc.id == 694826
