from pathlib import Path

DEFAULT_CACHE_PATH = Path("~/.cache/tsbenchmark/datasets").expanduser().as_posix()

DATASETS_SOURCE_MAP = {'AWS': 'https://tsbenchmark.s3.amazonaws.com/datas'}
DATASETS_SOURCE_DEFAULT = 'AWS'
