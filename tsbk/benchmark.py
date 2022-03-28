import sys
from engine.factory import Factory
from utils.params_parser import load_params
from utils.util import logging, bakup
import time

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    time_start = time.time()
    logger.info("benchmark start")
    logger.info("sys.argv: {}".format(str(sys.argv)))
    params = load_params(sys.argv)
    benchmark = Factory().get_benchmark('local', params)
    benchmark.run()
    benchmark.gen_report()
    bakup(params)
    logger.info("benchmark end, total cost {}s".format(time.time() - time_start))
