import pandas as pd
import os


class TSDataset:

    def __init__(self, id, name, dataset_loader):
        self.id = id
        self.name = name
        self.dataset_loader = dataset_loader

    def get_data(self):
        return self.get_train(), self.get_test()

    def get_train(self):
        if not hasattr(self, '_train'):
            self._train = self.dataset_loader.load_train(self.id)
        return self._train

    def get_test(self):
        if not hasattr(self, '_test'):
            self._test = self.dataset_loader.load_test(self.id)
        return self._test


# TODO: define task list

class MockDataset(TSDataset):  # TODO remove this class
    """Test dataset"""

    def __init__(self):
        super(MockDataset, self).__init__(0)

    def get_data(self):
        from hyperts.datasets.base import load_network_traffic
        df = load_network_traffic()
        return df


def get_dataset(dataset_id):
    return MockDataset()
