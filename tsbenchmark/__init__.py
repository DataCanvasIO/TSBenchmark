import os
from hypernets.utils import logging as hyn_logging

__version__ = "0.1.0"


_log_level = os.getenv('TSB_LOG_LEVEL', 'INFO')
hyn_logging.set_level(_log_level)
