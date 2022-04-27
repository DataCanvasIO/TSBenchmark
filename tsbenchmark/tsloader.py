from tsbenchmark.core.loader import DataSetLoader, TaskLoader
from tsbenchmark.datasets import TSDataset, TSTaskData
import os
from hypernets.utils import logging
import pandas as pd
import yaml
from tsbenchmark.tasks import TSTaskConfig
from tsbenchmark.util import download_util, file_util

logging.set_level('DEBUG')  # TODO
logger = logging.getLogger(__name__)

BASE_URL = 'http://raz9e5klq.hb-bkt.clouddn.com/datas'
DESC_URL = f'{BASE_URL}/dataset_desc.csv'


class TSDataSetDesc:
    def __init__(self, data_path):
        self.data_path = data_path

        if not os.path.exists(self._desc_file()):
            logger.info('Downloading dataset_desc.csv from remote.')
            download_util.download(self._desc_file(), DESC_URL)
            logger.info('Finish download dataset_desc.csv.')
        self.dataset_desc = pd.read_csv(self._desc_file())
        self.dataset_desc_local = None
        if os.path.exists(self._desc_local_file()):
            self.dataset_desc_local = pd.read_csv(self._desc_local_file())

    def exists(self, dataset_id):
        return self.dataset_desc[self.dataset_desc['id'] == dataset_id].shape[0] == 1

    def cached(self, dataset_id):
        return self.dataset_desc_local is not None and \
               self.dataset_desc_local[self.dataset_desc_local['id'] == dataset_id].shape[0] == 1

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
        return os.path.join(self.data_path, dataset.type.values[0],
                            dataset.data_size.values[0], dataset.name.values[0])

    def data_size(self, dataset_id):
        dataset = self.dataset_desc_local[self.dataset_desc_local['id'] == dataset_id]
        return dataset.data_size.values[0]

    def data_shape(self, dataset_id):
        dataset = self.dataset_desc_local[self.dataset_desc_local['id'] == dataset_id]
        return dataset.shape


def _get_metadata(meta_file_path):
    f = open(meta_file_path, 'r', encoding='utf-8')
    metadata = yaml.load(f.read(), Loader=yaml.FullLoader)
    metadata['series_name'] = metadata['series_name'].split(
        ",") if 'series_name' in metadata else None
    metadata['covariables_name'] = metadata['covariables_name'].split(
        ",") if 'covariables_name' in metadata else None
    f.close()
    return metadata


def _to_dataset(taskdata_id):
    if '_' in str(taskdata_id):
        strs = taskdata_id.split('_')
        dataset_id = int(strs[0])
        task_no = int(strs[1])
    else:
        dataset_id = int(taskdata_id)
        task_no = 1
    return dataset_id, task_no


class TSDataSetLoader(DataSetLoader):
    def __init__(self, data_path):
        self.data_path = data_path
        self.dataset_desc = TSDataSetDesc(data_path)

    def list(self, type=None, data_size=None):
        df = self.dataset_desc.dataset_desc
        if data_size is not None:
            df = df[df['data_size'] == data_size]
        if type is not None:
            df = df[df['type'] == type]
        return df['id'].values

    def exists(self, dataset_id):
        return self.dataset_desc.exists(dataset_id)

    def data_format(self, dataset_id):
        df = self.dataset_desc.dataset_desc
        return df[df['id'] == dataset_id]['format'].values[0]

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
        metadata['data_size'] = self.dataset_desc.data_size(dataset_id)
        metadata['shape'] = self.dataset_desc.data_shape(dataset_id)
        return metadata

    def _download_if_not_cached(self, dataset_id):
        if not self.exists(dataset_id):
            raise ValueError(f"TaskData {dataset_id} does not exists!")
        if not self.dataset_desc.cached(dataset_id):
            # 1. Get dataset's meta from dataset_desc.
            meta = self.dataset_desc.dataset_desc[self.dataset_desc.dataset_desc['id'] == dataset_id]
            task_type = meta['type'].values[0]
            data_size = meta['data_size'].values[0]
            name = meta['name'].values[0]

            # 2. Download tmp zip file from cloud.
            tmp_path = file_util.get_dir_path(os.path.join(self.data_path, 'tmp'))
            url = f"{BASE_URL}/{task_type}/{data_size}/{name}.zip"
            import uuid
            file_name = str(uuid.uuid1()) + '.zip'
            file_tmp = os.path.join(tmp_path, file_name)
            download_util.download(file_tmp, url)

            # 3. Unzip file under data_path
            data_path = os.path.join(self.data_path, task_type, data_size)
            file_util.unzip(file_tmp, data_path)

            # 4. Record to dataset_desc_local.
            if self.dataset_desc.dataset_desc_local is not None:
                self.dataset_desc.dataset_desc_local = pd.concat([self.dataset_desc.dataset_desc_local, meta], 0)
            else:
                self.dataset_desc.dataset_desc_local = meta.copy()
            self.dataset_desc.dataset_desc_local.to_csv(self.dataset_desc._desc_local_file(), index=False)

            # 5. Remove tmp file.
            os.remove(file_tmp)


class TSTaskDataLoader():
    def __init__(self, data_path):
        self.data_path = data_path
        self.dataset_loader = TSDataSetLoader(data_path)

    def list(self, type=None, data_size=None):
        df = self.dataset_loader.dataset_desc.dataset_desc
        if data_size is not None:
            df = df[df['data_size'] == data_size]
        if type is not None:
            df = df[df['type'] == type]

        taskdata_list = []

        for i, row in df.iterrows():
            task_count = row['task_count']
            if task_count == 1:
                taskdata_list.append(str(row['id']))
            else:
                taskdata_list = taskdata_list + [str("{}_{}".format(row['id'], i)) for i in range(task_count)]

        return taskdata_list

    def exists(self, task_data_id):
        df = self.dataset_loader.dataset_desc.dataset_desc
        dataset_id, task_no = _to_dataset(task_data_id)
        row = df[df['id'] == dataset_id]
        return row.shape[0] == 1 and int(row['task_count'].values[0]) >= task_no

    def load_meta(self, task_data_id):
        dataset_id, task_no = _to_dataset(task_data_id)
        return self.dataset_loader.load_meta(dataset_id)

    def load(self, task_data_id):
        return self.load_train(task_data_id), self.load_test(task_data_id)

    def load_train(self, task_data_id):
        dataset_id, task_no = _to_dataset(task_data_id)
        if self.dataset_loader.data_format(dataset_id) == 'csv':
            return self.dataset_loader.load_train(dataset_id)
        else:
            logger.info("To be implement.")  # todo
            raise NotImplemented

    def load_test(self, task_data_id):
        dataset_id, task_no = _to_dataset(task_data_id)
        if self.dataset_loader.data_format(dataset_id) == 'csv':
            return self.dataset_loader.load_test(dataset_id)
        else:
            logger.info("To be implement.")  # todo
            raise NotImplemented


class TSTaskLoader(TaskLoader):
    def __init__(self, data_path):
        self.data_path = data_path
        self.taskdata_loader = TSTaskDataLoader(data_path)

    def list(self, type=None, data_size=None):
        return self.taskdata_loader.list(type, data_size)

    def exists(self, taskconfig_id):
        return self.taskdata_loader.exists(taskconfig_id)

    def load(self, taskconfig_id):
        metadata = self.taskdata_loader.load_meta(taskconfig_id)
        dataset_id, task_no = _to_dataset(taskconfig_id)

        task = TSTaskConfig(taskconfig_id=taskconfig_id,
                            dataset_id=dataset_id,
                            taskdata=TSTaskData(id=taskconfig_id, dataset_id=dataset_id, name=metadata['name'],
                                                taskdata_loader=self.taskdata_loader),
                            date_name=metadata['date_name'],
                            task=metadata['task'],
                            horizon=metadata['horizon'],
                            data_size=metadata['data_size'],
                            shape=metadata['shape'],
                            series_name=metadata['series_name'],
                            covariables_name=metadata['covariables_name'],
                            dtformat=metadata['dtformat'])
        return task
