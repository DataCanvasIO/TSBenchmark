import os
import tsbenchmark
from tsbenchmark.tsloader import TSDataSetLoader, TSTaskLoader
from tsbenchmark.tasks import TSTask

data_path = os.path.join(os.path.dirname(os.path.dirname(tsbenchmark.__file__)), 'datas')
dataloader = tsbenchmark.tsloader.TSDataSetLoader(data_path)


class Test_TSDataSetLoader():
    def test_list(self):
        assert len(dataloader.list()) == 3

        assert len(dataloader.list(type='univariate-forecast')) == 2

        assert len(dataloader.list(data_size='medium')) == 1

    def test_exists(self):
        assert dataloader.exists(694826) == True
        assert dataloader.exists(9527) == False

    def test_load(self):
        df_train = dataloader.load_train(694826)
        assert df_train.shape[0] == 124

        df_test = dataloader.load_test(694826)
        assert df_test.shape[0] == 6

        metadata = dataloader.load_meta(694826)
        assert len(metadata) == 16

        dataloader.load_train(890686)
        dataloader.load_train(309496)


taskdataloader = tsbenchmark.tsloader.TSTaskDataLoader(data_path)


class Test_TSTaskDataLoader():
    def test_list(self):
        assert len(taskdataloader.list()) == 3

        assert len(taskdataloader.list(type='univariate-forecast')) == 2

        assert len(taskdataloader.list(type=['univariate-forecast', 'multivariate-forecast'])) == 3

        assert len(taskdataloader.list(data_size=['medium', 'small'])) == 3

        assert len(taskdataloader.list(type=['univariate-forecast', 'multivariate-forecast'],
                                       data_size=['small'])) == 2

        assert len(taskdataloader.list(data_size='medium')) == 1

    def test_exists(self):
        assert taskdataloader.exists('694826') == True
        assert taskdataloader.exists('9527') == False
        assert taskdataloader.exists('192837_3') == True
        assert taskdataloader.exists('192837_6') == False

    def test_load(self):
        df_train, df_test = taskdataloader.load(694826)
        assert df_train.shape[0] == 124 and df_test.shape[0] == 6


taskloader = TSTaskLoader(data_path)


class Test_TSTaskLoader():
    def test_config_list(self):
        assert len(taskloader.list()) == 3
        assert len(taskloader.list(type='univariate-forecast')) == 2
        assert len(taskloader.list(data_size='medium')) == 1

    def test_config_exists(self):
        assert taskloader.exists(694826) == True
        assert taskloader.exists(9527) == False

    def test_config_load(self):
        task_config = taskloader.load(694826)
        assert task_config.task == 'univariate-forecast' and task_config.dataset_id == 694826
        assert task_config.taskdata.get_train().shape[0] == 124 and task_config.taskdata.get_test().shape[0] == 6

    def test_task_load(self):
        task_config = taskloader.load(694826)
        task = TSTask(task_config, random_state=9527, max_trails=5, reward_metric='rmse')
        assert task.task == 'univariate-forecast' and task.dataset_id == 694826
        assert task.get_train().shape[0] == 124 and task.get_test().shape[0] == 6
        assert task.random_state == 9527
