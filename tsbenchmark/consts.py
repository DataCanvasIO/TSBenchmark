from pathlib import Path

DEFAULT_CACHE_PATH = Path("~/.cache/tsbenchmark/datasets").expanduser().as_posix()
ENV_DATASETS_CACHE_PATH = "TSB_DATASETS_CACHE_PATH"

DEFAULT_WORKING_DIR = Path("~/tsbenchmark-working-dir").expanduser().as_posix()

DATASETS_SOURCE_MAP = {'AWS': 'https://tsbenchmark.s3.amazonaws.com/datas'}
DATASETS_SOURCE_DEFAULT = 'AWS'

DEFAULT_REPORT_METRICS = ['smape', 'mape', 'rmse', 'mae']

DEFAULT_DOWNLOAD_RETRY_TIMES = 3
