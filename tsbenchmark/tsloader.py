from tsbenchmark.core.loader import DataSetLoader, TaskLoader
from tsbenchmark.datasets import TSDataset, TSTaskData
import os
from hypernets.utils import logging
import pandas as pd
import yaml
from tsbenchmark.tasks import TSTaskConfig
from tsbenchmark.util import download_util, file_util, df_util, md5_util
from tsbenchmark import consts

logging.set_level('DEBUG')  # TODO
logger = logging.getLogger(__name__)


# BASE_URL = 'https://tsbenchmark.s3.amazonaws.com/datas'  # TODO
# DESC_URL = f'{BASE_URL}/dataset_desc.csv'


class TSDataSetDesc:
    def __init__(self, data_path, data_source):
        self.data_path = data_path

        if not os.path.exists(self._desc_file()):
            logger.info('Downloading dataset_desc.csv from remote.')
            download_util.download_and_check(self._desc_file(), f'{data_source}/dataset_desc.csv')
            logger.info('Finish download dataset_desc.csv.')
        self.dataset_desc = pd.read_csv(self._desc_file())
        self.dataset_desc['id'] = self.dataset_desc['id'].astype(str)
        self.dataset_desc_local = None
        if os.path.exists(self._desc_local_file()):
            self.dataset_desc_local = pd.read_csv(self._desc_local_file())
            self.dataset_desc_local['id'] = self.dataset_desc_local['id'].astype(str)

    def exists(self, dataset_id):
        return self.dataset_desc[self.dataset_desc['id'] == str(dataset_id)].shape[0] == 1

    def cached(self, dataset_id):
        return self.dataset_desc_local is not None and \
               self.dataset_desc_local[self.dataset_desc_local['id'] == str(dataset_id)].shape[0] == 1

    def update_local(self, dataset_id):
        df = pd.read_csv(self._desc_file())
        df[df['id'] == str(dataset_id)].to_csv(self._desc_local_file(), index=False, mode='a')

    def _desc_file(self):
        return os.path.join(self.data_path, 'dataset_desc.csv')

    def _desc_md5sum(self):
        return os.path.join(self.data_path, '.md5sum')

    def _desc_local_file(self):
        return os.path.join(self.data_path, 'dataset_desc_local.csv')

    def train_file_path(self, dataset_id):
        return os.path.join(self.dataset_path_local(dataset_id), 'train.csv')

    def test_file_path(self, dataset_id):
        return os.path.join(self.dataset_path_local(dataset_id), 'test.csv')

    def meta_file_path(self, dataset_id):
        return os.path.join(self.dataset_path_local(dataset_id), 'metadata.yaml')

    def dataset_path_local(self, dataset_id):
        dataset = self.dataset_desc_local[self.dataset_desc_local['id'] == str(dataset_id)]
        return os.path.join(self.data_path, dataset.task.values[0],
                            dataset.data_size.values[0], dataset.name.values[0])

    def data_size(self, dataset_id):
        dataset = self.dataset_desc_local[self.dataset_desc_local['id'] == str(dataset_id)]
        return dataset.data_size.values[0]

    def data_shape(self, dataset_id):
        dataset = self.dataset_desc_local[self.dataset_desc_local['id'] == str(dataset_id)]
        return dataset.shape


def _get_metadata(meta_file_path):
    f = open(meta_file_path, 'r', encoding='utf-8')
    metadata = yaml.load(f.read(), Loader=yaml.FullLoader)
    f.close()
    return metadata


def _to_dataset(taskdata_id):
    if '_' in str(taskdata_id):
        strs = taskdata_id.split('_')
        dataset_id = strs[0]
        task_no = int(strs[1])
    else:
        dataset_id = str(taskdata_id)
        task_no = 1
    return dataset_id, task_no


class TSDataSetLoader(DataSetLoader):
    def __init__(self, data_path, data_source=None):
        self.data_path = data_path
        self.data_source = consts.DATASETS_SOURCE_MAP[
            consts.DATASETS_SOURCE_DEFAULT] if data_source is None else data_source
        self.dataset_desc = TSDataSetDesc(data_path, self.data_source)

    def list(self, type=None, data_size=None):
        df = self.dataset_desc.dataset_desc
        df = df_util.filter(df, 'data_size', data_size)
        df = df_util.filter(df, 'task', type)
        df = df[df['format'] != 'tsf']  # todo support in the future.
        return df['id'].values

    def exists(self, dataset_id):
        return self.dataset_desc.exists(dataset_id)

    def data_format(self, dataset_id):
        df = self.dataset_desc.dataset_desc
        return df[df['id'] == str(dataset_id)]['format'].values[0]

    def load_train(self, dataset_id):
        self._download_if_not_cached(dataset_id)
        df_train = pd.read_csv(self.dataset_desc.train_file_path(dataset_id))
        return df_train

    def load_test(self, dataset_id):
        self._download_if_not_cached(dataset_id)
        df_test = pd.read_csv(self.dataset_desc.test_file_path(dataset_id))
        return df_test

    def load_meta(self, dataset_id):
        metadata = self.dataset_desc.dataset_desc[self.dataset_desc.dataset_desc.id == str(dataset_id)].iloc[0].to_dict()
        return metadata

    def ready(self, dataset_id):
        ''' Download data and get the metadata from the metadata.yaml
        Parameters
        ----------
        dataset_id

        Returns dict
        -------

        '''
        self._download_if_not_cached(dataset_id)
        metadata = _get_metadata(self.dataset_desc.meta_file_path(dataset_id))
        metadata['data_size'] = self.dataset_desc.data_size(dataset_id)
        metadata['shape'] = self.dataset_desc.data_shape(dataset_id)

        metadata['series_name'] = metadata['series_name'].split(
            ",") if 'series_name' in metadata else None
        metadata['covariables_name'] = metadata['covariables_name'].split(
            ",") if 'covariables_name' in metadata else None

        if metadata['series_name'] is not None and metadata['covariables_name'] is not None:
            return metadata
        columns = list(self.load_test(dataset_id).columns.values)
        columns.remove(metadata['date_name'])

        if metadata['series_name'] is None and metadata['covariables_name'] is None:
            metadata['series_name'] = columns
        elif metadata['series_name'] is None:
            for col in metadata['covariables_name']:
                columns.remove(col)
            metadata['series_name'] = columns
        elif metadata['covariables_name'] is None:
            if len(columns) != len(metadata['series_name']):
                for col in metadata['series_name']:
                    columns.remove(col)
                metadata['covariables_name'] = columns

        return metadata

    def _download_if_not_cached(self, dataset_id):
        if not self.exists(dataset_id):
            raise ValueError(f"TaskData {dataset_id} does not exists!")
        if not self.dataset_desc.cached(dataset_id):
            # 1. Get dataset's meta from dataset_desc.
            meta = self.dataset_desc.dataset_desc[self.dataset_desc.dataset_desc['id'] == str(dataset_id)]
            task_type = meta['task'].values[0]
            data_size = meta['data_size'].values[0]
            name = meta['name'].values[0]

            # 2. Download tmp zip file from cloud.
            tmp_path = file_util.get_dir_path(os.path.join(self.data_path, 'tmp'))
            url = f"{self.data_source}/{task_type}/{data_size}/{name}.zip"
            import uuid
            file_name = str(uuid.uuid1()) + '.zip'
            file_tmp = os.path.join(tmp_path, file_name)
            download_util.download_and_check(file_tmp, url)

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
    def __init__(self, data_path, data_source=None):
        self.data_path = data_path
        self.dataset_loader = TSDataSetLoader(data_path, data_source)

    def list(self, type=None, data_size=None):
        df = self.dataset_loader.dataset_desc.dataset_desc
        df = df_util.filter(df, 'data_size', data_size)
        df = df_util.filter(df, 'task', type)
        df = df[df['format'] != 'tsf']  # todo support in the future.

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
        row = df[df['id'] == str(dataset_id)]
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
    def __init__(self, data_path, data_source=None):
        self.data_path = data_path
        self.taskdata_loader = TSTaskDataLoader(data_path, data_source)

    def list(self, type=None, data_size=None):
        return self.taskdata_loader.list(type, data_size)

    def exists(self, taskconfig_id):
        return self.taskdata_loader.exists(taskconfig_id)

    def load(self, taskconfig_id):
        metadata = self.taskdata_loader.load_meta(taskconfig_id)
        dataset_id, task_no = _to_dataset(taskconfig_id)

        task_config = TSTaskConfig(taskconfig_id=taskconfig_id,
                                   dataset_id=dataset_id,
                                   taskdata=TSTaskData(id=taskconfig_id, dataset_id=dataset_id, name=metadata['name'],
                                                       taskdata_loader=self.taskdata_loader),
                                   date_name=metadata['date_name'],
                                   task=metadata['task'],
                                   horizon=metadata['horizon'],
                                   data_size=metadata['data_size'],
                                   shape=metadata['shape'],
                                   series_name=None,
                                   covariables_name=None,
                                   dtformat=metadata['dtformat'])
        return task_config
