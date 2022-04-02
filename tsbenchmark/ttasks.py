class TSTaskConfig:

    def __init__(self, id, task, target, time_series, dataset, covariables=None):
        self.id = id
        self.task = task
        self.target = target
        self.time_series = time_series
        self.dataset = dataset
        self.covariables = covariables
