import os

import tsbenchmark as tsb
import tsbenchmark.api
from tsbenchmark import consts


def main():
  task = tsb.api.get_task()
  print(task)

  assert os.path.basename(os.getenv(consts.ENV_DATASETS_CACHE_PATH)).startswith("benchmark-cache-dir")
  assert os.path.basename(task.taskdata.taskdata_loader.data_path).startswith("benchmark-cache-dir")


if __name__ == "__main__":
    main()
