import os
import requests
import zipfile

import tsbenchmark.consts as consts
from hypernets.utils import logging
logging.set_level('DEBUG')
logger = logging.getLogger(__name__)


class id_util:

    @staticmethod
    def generate(type, data_size, name):
        TASK_TYPE_MAP = {
            consts.TASK_TYPE_UNIVARIATE: '5',
            consts.TASK_TYPE_MULTIVARIATE: '6'
        }

        DATA_SIZE_MAP = {
            consts.DATA_SIZE_SMALL: '1',
            consts.DATA_SIZE_MEDIUM: '2',
            consts.DATA_SIZE_LARGE: '3'
        }

        id = TASK_TYPE_MAP[type]
        id += DATA_SIZE_MAP[data_size]
        id += str(id_util.hash(name, 10000))

        return id

    @staticmethod
    def hash(_str, _base):
        seed = 131
        hash = 0
        for i in _str:
            hash = hash * seed + ord(i)
        hash = hash & 0x7FFFFFFF
        return (hash % _base)


class file_util:

    @staticmethod
    def get_dir_path(dir_path):
        dir_path = os.path.expanduser(dir_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    @staticmethod
    def get_filelist(dir, filelist):
        if os.path.isfile(dir):

            filelist.append(dir)

        elif os.path.isdir(dir):

            for s in os.listdir(dir):
                newDir = os.path.join(dir, s)

                file_util.get_filelist(newDir, filelist)

        return filelist

    @staticmethod
    def get_or_create_file(file_path):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                pass

    @staticmethod
    def remove(file_path):
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                os.removedirs(file_path)

    @staticmethod
    def unzip(zipPath, unZipPath):
        import zipfile
        '''Unzip file
           zipPath : The file which will be unzip.
           unZipPath : The path which the files will be unzip to.
           '''
        if not os.path.exists(zipPath):
            raise 'function unZipFile:not exists file or dir(%s)' % zipPath;
        if unZipPath == '':
            unZipPath = os.path.splitext(zipPath)[0];
        if not unZipPath.endswith(os.sep):
            unZipPath += os.sep
        z = zipfile.ZipFile(zipPath, 'r')
        for k in z.infolist():
            savePath = unZipPath + k.filename
            saveDir = os.path.dirname(savePath)
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)
            if os.path.isdir(savePath):
                if not os.path.exists(savePath):
                    os.makedirs(savePath)
            else:
                f = open(savePath, 'wb')
                f.write(z.read(k))
                f.close()
        z.close()

    @staticmethod
    def exeZipFile(filePath, zipFilePath=''):
        '''Zip file
            filePath The file or dir which will be zip.
            ZipFilePath The zip file path. If only give the file name, it will generate in the dir of filePath.
        '''
        filePath = filePath.decode('utf-8');
        zipFilePath = zipFilePath.decode('utf-8');

        if not os.path.exists(filePath):
            raise FileNotFoundError('function exeZipFile:not exists file or dir(%s)' % filePath)

        hasPDir = not filePath.endswith(os.sep)
        if not hasPDir:
            filePath = os.path.dirname(filePath)

        if zipFilePath == '':
            zipFilePath = os.path.splitext(filePath)[0] + '.zip';
        elif zipFilePath.find(os.sep) == -1:
            zipFilePath = os.path.dirname(filePath) + os.sep + zipFilePath

        if not os.path.exists(os.path.dirname(zipFilePath)):
            os.makedirs(os.path.dirname(zipFilePath))

        zipRoot = ''
        if hasPDir:
            zipRoot = os.path.split(filePath)[1]
        # Begin zip
        z = zipfile.ZipFile(zipFilePath, 'w')
        if os.path.isfile(filePath):
            z.write(filePath, os.path.split(filePath)[1])
        else:
            # _iterateExeZipFile(filePath, zipRoot, z); todo
            pass
        z.close()

    @staticmethod
    def zip_files(files, zipFilePath=''):
        '''Zip files
            files: The path array of the files.
            ZipFilePath: The path array of the files.
        '''

        assert files is not None
        assert all([os.path.isfile(f) for f in files])

        # Begin zip
        z = zipfile.ZipFile(zipFilePath, 'w')
        for f in files:
            z.write(f, os.path.basename(os.path.dirname(f)) + '/' + os.path.basename(f))
        z.close()

    @staticmethod
    def dataset_dirs(dir_path):
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return []

        if 'metadata.yaml' in os.listdir(dir_path):
            return [dir_path]

        results = []
        for d in os.listdir(dir_path):
            sub_dir_path = os.path.join(dir_path, d)
            if os.path.isdir(sub_dir_path):
                results.extend(file_util.dataset_dirs(sub_dir_path))
        return results

    @staticmethod
    def leaf_dirs(dir_path):
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return []

        if all([os.path.isfile(os.path.join(dir_path, d)) for d in os.listdir(dir_path)]):
            return [dir_path]

        results = []
        for d in os.listdir(dir_path):
            sub_dir_path = os.path.join(dir_path, d)
            if os.path.isdir(sub_dir_path):
                results.extend(file_util.leaf_dirs(sub_dir_path))
        return results


class download_util:
    @staticmethod
    def download(file_path, url):
        logger.info(f"Begin download {file_path} from {url}")
        file_util.get_or_create_file(file_path)
        response = requests.get(url=url, stream=True)
        if response.status_code == 200:
            chunk_size = 1024 * 8
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            logger.info(f"Finish download {file_path} from {url}")
        else :
            raise FileNotFoundError(f"Download error with status_code {response.status_code} for "
                                    f"{file_path} from {url}")

    @staticmethod
    def download_and_check(file_path, url):

        if md5_util.check_md5sum_onefile(file_path):
            return True

        download_success = False
        md5sum_path = os.path.join(os.path.dirname(file_path), '.md5sum')
        url_md5sum = url[:url.rfind('/') + 1] + ".md5sum"
        check_name = url[url.rfind('/') + 1:]
        for i in range(consts.DEFAULT_DOWNLOAD_RETRY_TIMES):
            file_util.remove(file_path)
            file_util.remove(md5sum_path)
            download_util.download(file_path, url)
            download_util.download(md5sum_path, url_md5sum)
            if md5_util.check_md5sum_onefile(file_path, check_name):
                download_success = True
                break
        if not download_success:
            raise FileNotFoundError(
                r"Download failed for {url_file} in {consts.DEFAULT_DOWNLOAD_RETRY_TIMES} times.")


class dict_util:
    @staticmethod
    def sub_dict(somedict, somekeys, default=None):
        return dict([(k, somedict.get(k, default)) for k in somekeys])


class df_util:
    @staticmethod
    def filter(df, filter_key, filter_value):
        if filter_key is not None and filter_value is not None:
            if isinstance(filter_value, list):
                df = df[df[filter_key].isin(filter_value)]
            else:
                df = df[df[filter_key] == filter_value]
        return df


from hashlib import md5


class md5_util:
    @staticmethod
    def get_md5(file_path):
        with open(file_path, 'rb') as f:
            md5_value = md5(f.read()).hexdigest()
        return md5_value

    @staticmethod
    def get_md5sum(dir_check):
        file_md5sum = os.path.join(dir_check, '.md5sum')
        with open(file_md5sum, 'rb') as f:
            content = f.read()
        return content

    @staticmethod
    def check_md5sum(dir_check):
        if not os.path.exists(dir_check) or not os.path.exists(os.path.join(dir_check, '.md5sum')):
            return False

        flag = True
        content = md5_util.get_md5sum(dir_check)
        check_list = content.splitlines()
        for item in check_list:
            hash_value = item.split()[0]
            file_name = item.split()[1]
            file_path = os.path.join(dir_check, bytes.decode(file_name))
            hash_calc = md5_util.get_md5(file_path)
            if not (bytes.decode(hash_value) == hash_calc):
                flag = False
                break
        return flag

    @staticmethod
    def check_md5sum_onefile(file_check, check_name=None):
        dir_path = os.path.dirname(file_check)
        if not os.path.exists(file_check) or not os.path.exists(os.path.join(dir_path, '.md5sum')):
            return False

        check_name = check_name if check_name is not None else os.path.basename(file_check)

        flag = False
        content = md5_util.get_md5sum(dir_path)
        check_list = content.splitlines()
        for item in check_list:
            hash_value = item.split()[0]
            file_name = item.split()[1]
            if bytes.decode(file_name) == check_name:
                hash_calc = md5_util.get_md5(file_check)
                if bytes.decode(hash_value) == hash_calc:
                    flag = True
                    break
        return flag


def cal_task_metrics(y_pred, y_true, date_col_name, series_col_name, covariables, metrics_target, task_calc_score):
    from tsbenchmark import metrics
    if series_col_name != None:
        y_pred = y_pred[series_col_name]
        y_true = y_true[series_col_name]

    if date_col_name in y_pred.columns:
        y_pred = y_pred.drop(columns=[date_col_name], axis=1)
    if date_col_name in y_true.columns:
        y_true = y_true.drop(columns=[date_col_name], axis=1)
    if covariables != None:
        cols_del_y_true = [col for col in covariables if col not in y_true.columns.values]
        if cols_del_y_true is not None and len(cols_del_y_true) > 1:
            y_true = y_true.drop(columns=cols_del_y_true)

        cols_del_y_pred = [col for col in covariables if col in y_pred.columns.values]
        if cols_del_y_pred is not None and len(cols_del_y_pred) > 1:
            y_pred = y_pred.drop(columns=cols_del_y_true)

    metrics_task = metrics.calc_score(y_true, y_pred,
                                      metrics=metrics_target, task=task_calc_score)
    return metrics_task


class data_package_util:
    def package(self, data_path, target_path):

        self.desc_generate(data_path, target_path)

        import shutil
        # Generate .md5sum for dataset_desc.csv and copy them to target_path.
        dataset_desc_src = os.path.join(target_path, 'dataset_desc.csv')

        self.package_md5([dataset_desc_src], os.path.join(target_path, '.md5sum'))

        # Generate .md5sum for each dataset and copy zip and .md5 to relative path from target_path.
        dataset_dirs = file_util.dataset_dirs(data_path)

        for dataset_dir in dataset_dirs:
            dir_target = os.path.join(target_path, dataset_dir[len(data_path) + len(os.sep):])

            file_names = ['metadata.yaml', 'test.csv', 'train.csv']
            file_pathes = [os.path.join(dataset_dir, name) for name in file_names]

            self.package_md5(file_pathes, os.path.join(dir_target, '.md5sum'))
            file_pathes.append(os.path.join(dir_target, '.md5sum'))

            zip_file = os.path.join(dir_target + '.zip')
            file_util.zip_files(file_pathes, zip_file)

            # Generate new .md5sum for zip file and cover the old one.
            self.package_md5([zip_file], os.path.join(os.path.dirname(dir_target), '.md5sum'))

            os.remove(os.path.join(dir_target, '.md5sum'))
            os.removedirs(dir_target)

    def package_md5(self, files_path, target_path):
        md5_values = ''
        for i in range(len(files_path)):
            file_path = files_path[i]
            md5_values += md5_util.get_md5(file_path) + '  ' + os.path.basename(file_path) + '\n'

        file_util.get_or_create_file(target_path)
        with open(target_path, 'a') as f:
            f.write(md5_values)

    def desc_generate(self, data_path, target_path):
        import yaml
        import pandas as pd
        import hashlib
        types = ['multivariate-forecast', 'univariate-forecast']
        data_sizes = ['large', 'small', 'medium']
        df = pd.DataFrame(
            columns=['id', 'task', 'data_size', 'shape', 'name', 'label', 'frequency', 'industry',
                     'source_type','date_name','horizon', 'dtformat', 'format', 'task_count'])

        for task in types:
            for data_size in data_sizes:
                path = os.path.join(data_path, task, data_size)
                if os.path.exists(path):
                    list = os.listdir(path)
                    for dir in list:
                        if (dir == '__init__.py' or dir == 'template'):
                            continue
                        record = {'task': task, 'data_size': data_size, 'name': dir, 'format': 'csv', 'task_count': 1}
                        train_file_path = path + os.sep + dir + os.sep + 'train.csv'
                        metadata_path = path + os.sep + dir + os.sep + 'metadata.yaml'

                        if os.path.exists(metadata_path):
                            f = open(metadata_path, 'r', encoding='utf-8')
                            meta_config = yaml.load(f.read(), Loader=yaml.FullLoader)

                            record.update({'id': id_util.generate(task, data_size, meta_config['name'])})
                            record.update(
                                {'source_type': meta_config['source_type'] if 'source_type' in meta_config else None})
                            record.update({'date_name': meta_config['date_name']})
                            record.update({'horizon': meta_config['horizon']})
                            record.update({'dtformat': meta_config['dtformat']})
                            record.update({'label': meta_config['label'] if 'label' in meta_config else None})
                            record.update(
                                {'frequency': meta_config['frequency'] if 'frequency' in meta_config else None})
                            record.update({'shape': meta_config['shape'] if 'shape' in meta_config else None})
                            record.update(
                                {'industry': meta_config['industry'].lower() if 'industry' in meta_config else None})
                        df = df.append(record, ignore_index=True)

        file_util.get_or_create_file(os.path.join(target_path, 'dataset_desc.csv'))
        file_util.get_or_create_file(os.path.join(target_path, 'dataset_desc_local.csv'))
        df.to_csv(os.path.join(target_path, 'dataset_desc.csv'), index=False)
        df.to_csv(os.path.join(target_path, 'dataset_desc_local.csv'), index=False)
