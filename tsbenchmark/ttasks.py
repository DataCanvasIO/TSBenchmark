class TSTaskConfig:

    def __init__(self, id, task, target, time_series, dataset_id, covariables=None):
        self.id = id
        self.task = task
        self.target = target
        self.time_series = time_series
        self.dataset_id = dataset_id
        self.covariables = covariables

    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task ,
            "target": self.target,
            "time_series": self.time_series ,
            "dataset": self.dataset_id,
            "covariables": self.covariables ,
        }
