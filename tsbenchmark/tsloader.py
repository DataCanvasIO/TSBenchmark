from tsbenchmark.core.loader import DataSetLoader, TaskLoader
from tsbenchmark.tdatasets import TSDataset
import os
from hypernets.utils import logging
import pandas as pd
import yaml
from tsbenchmark.ttasks import TSTaskConfig

logging.set_level('DEBUG')  # TODO
logger = logging.getLogger(__name__)


class TSDataSetDesc:
    def __init__(self, data_path):
        self.data_path = data_path

        if not os.path.exists(self._desc_file()):
            logger.info('Downloading dataset_desc.csv from remote.')
            # TODO DOWNLOAD
            logger.info('Finish download dataset_desc.csv.')
        self.dataset_desc = pd.read_csv(self._desc_file())
        self.dataset_desc_local = None
        if os.path.exists(self._desc_local_file()):
            self.dataset_desc_local = pd.read_csv(self._desc_local_file())

    def exists(self, dataset_id):
        return self.dataset_desc[self.dataset_desc['id'] == dataset_id].shape[0] == 1

    def cached(self, dataset_id):
        return self.dataset_desc_local[self.dataset_desc_local['id'] == dataset_id].shape[0] == 1

    def update_local(self, dataset_id):
        df = pd.read_csv(self._desc_file())
        df[df['id'] == dataset_id].to_csv(self._desc_local_file(), index=False, mode='a')

    def _desc_file(self):
        return os.path.join(self.data_path, 'dataset_desc.csv')

    def _desc_local_file(self):
        return os.path.join(self.data_path, 'dataset_desc_local.csv')

    def train_file_path(self, dataset_id):
        return os.path.join(self.dataset_path_local(dataset_id), 'train.csv')

    def test_file_path(self, dataset_id):
        return os.path.join(self.dataset_path_local(dataset_id), 'test.csv')

    def meta_file_path(self, dataset_id):
        return os.path.join(self.dataset_path_local(dataset_id), 'metadata.yaml')

    def dataset_path_local(self, dataset_id):
        dataset = self.dataset_desc_local[self.dataset_desc_local['id'] == dataset_id]
        return os.path.join(self.data_path,
                            dataset.type.values[0],
                            dataset.data_size.values[0],
                            dataset.name.values[0]
                            )


def _get_metadata(meta_file_path):
    f = open(meta_file_path, 'r', encoding='utf-8')
    metadata = yaml.load(f.read(), Loader=yaml.FullLoader)
    metadata['series_name'] = metadata['series_name'].split(
        ",") if 'series_name' in metadata else None
    metadata['covariables_name'] = metadata['covariables_name'].split(
        ",") if 'covariables_name' in metadata else None
    f.close()
    return metadata


class TSDataSetLoader(DataSetLoader):
    def __init__(self, data_path):
        self.data_path = data_path
        self.dataset_desc = TSDataSetDesc(data_path)

    def list(self, type=None, data_size=None):
        # 1. Get dataset desc from local or remote.
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        df = self.dataset_desc.dataset_desc
        if data_size is not None:
            df = df[df['data_size'] == data_size]
        if type is not None:
            df = df[df['type'] == type]
        return df['id'].values

    def exists(self, dataset_id):
        return self.dataset_desc.exists(dataset_id)

    def load(self, dataset_id):
        return self.load_train(dataset_id), self.load_test(dataset_id)

    def load_train(self, dataset_id):
        self._download_if_not_cached(dataset_id)
        df_train = pd.read_csv(self.dataset_desc.train_file_path(dataset_id))
        return df_train

    def load_test(self, dataset_id):
        self._download_if_not_cached(dataset_id)
        df_test = pd.read_csv(self.dataset_desc.test_file_path(dataset_id))
        return df_test

    def load_meta(self, dataset_id):
        self._download_if_not_cached(dataset_id)
        metadata = _get_metadata(self.dataset_desc.meta_file_path(dataset_id))
        return metadata

    def _download_if_not_cached(self, dataset_id):
        if not self.exists(dataset_id):
            raise ValueError(f"Dataset {dataset_id} does not exists!")
        if not self.dataset_desc.cached(dataset_id):
            logger.info(f"Downloading dattaset {dataset_id} from remote.")
            # TODO
            self.local_update(dataset_id)
            logger.info(f"Finish download dattaset {dataset_id} from remote.")


class TSTaskLoader(TaskLoader):
    def __init__(self, data_path):
        self.data_path = data_path
        self.dataset_loader = TSDataSetLoader(data_path)

    def list(self, type=None, data_size=None):
        return self.dataset_loader.list(type, data_size)

    def exists(self, dataset_id):
        return self.dataset_loader.exists(dataset_id)

    def load(self, dataset_id):
        metadata = self.dataset_loader.load_meta(dataset_id)

        task = TSTaskConfig(dataset_id=dataset_id,
                            dataset=TSDataset(id=dataset_id, name=metadata['name'], dataset_loader=self.dataset_loader),
                            date_name=metadata['date_name'],
                            task=metadata['task'],
                            horizon=metadata['horizon'],
                            series_name=metadata['series_name'],
                            covariables_name=metadata['covariables_name'],
                            dtformat=metadata['dtformat'])
        return task
