# -*- encoding: utf-8 -*-
import argparse
from pathlib import Path

from hypernets.utils import logging
from hypernets.utils import logging as hyn_logging
from tsbenchmark.cfg import load_benchmark
from tsbenchmark.reporter import load_compare_reporter

logger = logging.getLogger(__name__)

PWD_path = Path(__file__)
import os

src_dir = os.path.dirname(__file__)

def main():
    """
    Examples:
        cd tsbenchmark/tests
        tsb run --config ./benchmark_example_local.yaml
        tsb --log-level=DEBUG run --config ./benchmark_example_local.yaml
        tsb compare ~/tsbenchmark-data/report/bechmark1 ~/tsbenchmark-data/report/bechmark2
    """
    print("PWD_path")
    print(PWD_path.as_posix())
    print("src_dir")
    print(src_dir)


    def setup_global_args(global_parser):
        # console output
        logging_group = global_parser.add_argument_group('Console outputs')

        logging_group.add_argument('--log-level', type=str, default='INFO',
                                   help='logging level, default is %(default)s')
        logging_group.add_argument('-error', dest='log_level', action='store_const', const='ERROR',
                                   help='alias of "--log-level=ERROR"')
        logging_group.add_argument('-warn', dest='log_level', action='store_const', const='WARN',
                                   help='alias of "--log-level=WARN"')
        logging_group.add_argument('-info', dest='log_level', action='store_const', const='INFO',
                                   help='alias of "--log-level=INFO"')
        logging_group.add_argument('-debug', dest='log_level', action='store_const', const='DEBUG',
                                   help='alias of "--log-level=DEBUG"')

    def setup_run_parser(operation_parser):
        exec_parser = operation_parser.add_parser("run", help="run benchmark")
        exec_parser.add_argument("-c", "--config", help="benchmark yaml config file", default=None, required=True)

    def setup_compare_parser(operation_parser):
        exec_parser = operation_parser.add_parser("compare", help="compare benchmark reports")
        exec_parser.add_argument("-c", "--config", help="compare yaml config file", default=None, required=True)

    parser = argparse.ArgumentParser(prog="tsb",
                                     description='tsb command is used to manage benchmarks', add_help=True)
    setup_global_args(parser)

    subparsers = parser.add_subparsers(dest="operation")

    setup_run_parser(subparsers)
    setup_compare_parser(subparsers)

    args_namespace = parser.parse_args()

    kwargs = args_namespace.__dict__.copy()

    log_level = kwargs.pop('log_level')
    if log_level is None:
        log_level = hyn_logging.INFO
    hyn_logging.set_level(log_level)

    operation = kwargs.pop('operation')

    if operation == 'run':
        benchmark = load_benchmark(kwargs.get('config'))
        benchmark.run()
    elif operation == 'compare':
        reporter = load_compare_reporter(kwargs.get('config'))
        reporter.run_compare()

    else:
        parser.print_help()
        # raise ValueError(f"unknown job operation: {operation} ")


if __name__ == '__main__':
    main()
