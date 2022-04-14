import pandas as pd
import os


class TSDataset:

    def __init__(self, id, name, dataset_loader):
        self.id = id
        self.name = name
        self.dataset_loader = dataset_loader

    # def get_data(self):
    #     return self.get_train(), self.get_test()
    #
    # def get_train(self):
    #     if not hasattr(self, '_train'):
    #         self._train = self.dataset_loader.load_train(self.id)
    #     return self._train
    #
    # def get_test(self):
    #     if not hasattr(self, '_test'):
    #         self._test = self.dataset_loader.load_test(self.id)
    #     return self._test


class TSTaskData:

    def __init__(self, dataset_id, name, taskdata_loader, id=None):
        self.id = id
        self.dataset_id = dataset_id
        self.name = name
        self.taskdata_loader = taskdata_loader

    def get_data(self):
        return self.get_train(), self.get_test()

    def get_train(self):
        if not hasattr(self, '_train'):
            self._train = self.taskdata_loader.load_train(self.id)
        return self._train

    def get_test(self):
        if not hasattr(self, '_test'):
            self._test = self.taskdata_loader.load_test(self.id)
        return self._test

