import os
import tsbenchmark
from tsbenchmark.tsloader import TSDataSetLoader, TSTaskLoader
from tsbenchmark.tasks import TSTask

data_path = os.path.join(os.path.dirname(tsbenchmark.__file__),'tests','datas')
dataloader = tsbenchmark.tsloader.TSDataSetLoader(data_path)


class Test_TSDataSetLoader():
    def test_list(self):
        assert len(dataloader.list()) == 14

        assert len(dataloader.list(type='univariate-forecast')) == 7

        assert len(dataloader.list(data_size='medium')) == 2

    def test_exists(self):
        assert dataloader.exists(512754) == True
        assert dataloader.exists(9527) == False

    def test_load(self):
        df_train = dataloader.load_train(512754)
        assert df_train.shape[0] == 124

        df_test = dataloader.load_test(512754)
        assert df_test.shape[0] == 6

        metadata = dataloader.load_meta(512754)
        assert len(metadata) == 14

        dataloader.load_train(512754)
        dataloader.load_train(61807)


taskdataloader = tsbenchmark.tsloader.TSTaskDataLoader(data_path)


class Test_TSTaskDataLoader():
    def test_list(self):
        assert len(taskdataloader.list()) == 14

        assert len(taskdataloader.list(type='univariate-forecast')) == 7

        assert len(taskdataloader.list(type=['univariate-forecast', 'multivariate-forecast'])) == 14

        assert len(taskdataloader.list(data_size=['medium', 'small'])) == 11

        assert len(taskdataloader.list(type=['univariate-forecast', 'multivariate-forecast'],
                                       data_size=['small'])) == 9

        assert len(taskdataloader.list(data_size='medium')) == 2

    def test_exists(self):
        assert taskdataloader.exists(512754) == True
        assert taskdataloader.exists(9527) == False


    def test_load(self):
        df_train, df_test = taskdataloader.load(512754)
        assert df_train.shape[0] == 124 and df_test.shape[0] == 6


taskloader = TSTaskLoader(data_path)


class Test_TSTaskLoader():
    def test_config_list(self):
        assert len(taskloader.list()) == 14
        assert len(taskloader.list(type='univariate-forecast')) == 7
        assert len(taskloader.list(data_size='medium')) == 2

    def test_config_exists(self):
        assert taskloader.exists(512754) == True
        assert taskloader.exists(9527) == False

    def test_config_load(self):
        task_config = taskloader.load(512754)
        assert task_config.task == 'univariate-forecast' and task_config.dataset_id == str(512754)

        task_config = taskloader.load(61807)
        assert task_config.task == 'multivariate-forecast' and task_config.dataset_id == str(61807)

    def test_task_load(self):
        task_config = taskloader.load(512754)
        task = TSTask(task_config, random_state=9527, max_trials=5, reward_metric='rmse')
        assert task.task == 'univariate-forecast' and task.dataset_id == str(512754)
        assert task.get_train().shape[0] == 124 and task.get_test().shape[0] == 6
        assert task.random_state == 9527

        task_config = taskloader.load(61807)
        task = TSTask(task_config, random_state=9527, max_trials=5, reward_metric='rmse')
        assert task.task == 'multivariate-forecast' and task.dataset_id == str(61807)
        assert task.taskdata.get_train().shape[1] == 112 and task.taskdata.get_test().shape[0] == 8
        assert task.series_name is None

        task.ready()
        assert task.series_name is not None and len(task.series_name) == 111
