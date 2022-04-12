import os
from tsbenchmark.tsdatasetloader import TSDataSetLoader

data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'datas')
loader = TSDataSetLoader(data_path)


def test_list():
    assert len(loader.list()) == 3

    assert len(loader.list(type='univariate-forecast')) == 2

    assert len(loader.list(data_size='medium')) == 1


def test_exists():
    assert loader.exists(694826) == True


def test_load():
    df_train, df_test, metadata = loader.load(694826)
    assert df_train.shape[0] == 124 and df_test.shape[0] == 6 and len(metadata) == 15
