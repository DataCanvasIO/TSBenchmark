import os.path
import pandas as pd

import sys

sys.path.append("..")
import os
import util


def spit_dev_data():
    data_base_path, report_base_path, max_trials, mode, vers = util.initparams('../config.yaml')
    print(data_base_path, report_base_path, max_trials, mode, vers)

    types = ['multivariate-forecast', 'univariate-forecast']
    data_sizes = ['large', 'medium', 'small']

    for type in types:
        print("3 type:" + type)
        for data_size in data_sizes:
            print("4 data_size:" + data_size)
            path = data_base_path + os.sep + type + os.sep + data_size
            if os.path.exists(path):
                list = os.listdir(path)
                for dir in list:

                    train_file_path = path + os.sep + dir + os.sep + 'train.csv'
                    dev_file_path = path + os.sep + dir + os.sep + 'train_dev.csv'
                    if os.path.exists(dev_file_path):
                        continue
                    print('saveing: ', dev_file_path)
                    if os.path.exists(train_file_path):
                        df_train = pd.read_csv(train_file_path)
                        if df_train.shape[0] > 1000:
                            df_dev = df_train[-1000:]
                        else:
                            df_dev = df_train
                        df_dev.to_csv(dev_file_path, index=False)

    return 0


spit_dev_data()
