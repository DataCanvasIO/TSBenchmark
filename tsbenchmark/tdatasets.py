class TSDataset:

    def __init__(self, id):
        self.id = id

    def get_data(self):
        raise NotImplemented


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
