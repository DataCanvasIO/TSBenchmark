import os
import tsbenchmark
from tsbenchmark.tsloader import TSDataSetLoader, TSTaskLoader

data_path = os.path.join(os.path.dirname(os.path.dirname(tsbenchmark.__file__)), 'datas')
dataloader = tsbenchmark.tsloader.TSDataSetLoader(data_path)


class Test_TSDataSetLoader():
    def test_datase(self):
        assert len(dataloader.list()) == 3

        assert len(dataloader.list(type='univariate-forecast')) == 2

        assert len(dataloader.list(data_size='medium')) == 1

    def test_exists(self):
        assert dataloader.exists(694826) == True
        assert dataloader.exists(9527) == False

    def test_load(self):
        df_train, df_test, metadata = dataloader.load(694826)
        assert df_train.shape[0] == 124 and df_test.shape[0] == 6 and len(metadata) == 15


taskloader = TSTaskLoader(data_path)


class Test_TSTaskLoader():
    def test_datase(self):
        assert len(taskloader.list()) == 3
        assert len(taskloader.list(type='univariate-forecast')) == 2
        assert len(taskloader.list(data_size='medium')) == 1

    def test_exists(self):
        assert taskloader.exists(694826) == True
        assert taskloader.exists(9527) == False

    def test_load(self):
        task = taskloader.load(694826)
        assert task.task == 'univariate-forecast' and task.dataset_id == 694826
