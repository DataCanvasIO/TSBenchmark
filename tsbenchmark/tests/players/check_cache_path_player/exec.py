import os

import tsbenchmark as tsb
import tsbenchmark.api
from tsbenchmark import consts


def main():
  task = tsb.api.get_task()
  print(task)
  assert os.getenv(consts.ENV_DATASETS_CACHE_PATH) == "/tmp/datasets-cache"
  assert task.taskdata.taskdata_loader.data_path == "/tmp/datasets-cache"


if __name__ == "__main__":
    main()
