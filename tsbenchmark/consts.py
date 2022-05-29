from pathlib import Path
import os

DEFAULT_CACHE_PATH = Path("~/.cache/tsbenchmark/datasets").expanduser().as_posix()
ENV_DATASETS_CACHE_PATH = "TSB_DATASETS_CACHE_PATH"
ENV_TSB_CONDA_HOME = "TSB_CONDA_HOME"

DEFAULT_WORKING_DIR = Path("~/tsbenchmark-working-dir").expanduser().as_posix()

DATASETS_SOURCE_MAP = {'AWS': 'https://tsbenchmark.s3.amazonaws.com/datas'}
DATASETS_SOURCE_DEFAULT = 'AWS'

DEFAULT_REPORT_METRICS = ['smape', 'mape', 'rmse', 'mae']

DEFAULT_DOWNLOAD_RETRY_TIMES = 3

NONE_DEV_ENV = os.getenv('developer') is None

DATA_SIZE_SMALL = 'small'
DATA_SIZE_MEDIUM = 'medium'
DATA_SIZE_LARGE = 'large'
TASK_TYPE_UNIVARIATE = 'univariate-forecast'
TASK_TYPE_MULTIVARIATE = 'multivariate-forecast'

DEFAULT_GLOBAL_RANDOM_STATE=2022

