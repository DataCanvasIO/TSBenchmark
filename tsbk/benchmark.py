import sys
from engine.factory import Factory
from utils.params_parser import load_and_backup_params
from utils.util import logging
import time

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    time_start = time.time()
    logger.info("benchmark start")
    logger.info("sys.argv: {}".format(str(sys.argv)))
    params = load_and_backup_params(sys.argv)
    benchmark = Factory().get_benchmark('local', params)

    type = benchmark.params.type
    if type == 'benchmark':
        benchmark.run()
        benchmark.gen_report()
    elif type == 'comparison':
        benchmark.gen_comparison_report()

    logger.info("benchmark end, total cost {}s".format(time.time() - time_start))
