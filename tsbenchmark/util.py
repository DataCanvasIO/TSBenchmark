import os
import requests


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
        if not os.path.exists(os.path.basename(file_path)):
            with open(file_path, "w") as f:
                pass

    @staticmethod
    def unzip(zipPath, unZipPath):
        import zipfile
        '''解压文件
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


class download_util:
    @staticmethod
    def download(file_path, url):
        file_util.get_or_create_file(file_path)
        r = requests.get(url)
        with open(file_path, 'wb') as f:
            f.write(r.content)
            f.close


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
        y_true = y_true.drop(columns=[covariables], axis=1)
    metrics_task = metrics.calc_score(y_true, y_pred,
                                      metrics=metrics_target, task=task_calc_score)
    return metrics_task
