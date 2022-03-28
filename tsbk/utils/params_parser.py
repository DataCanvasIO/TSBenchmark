import sys, getopt
import yaml
from engine.factory import Params
from utils.util import logging

logger = logging.getLogger(__name__)


def load_params(argv):
    opts, args = _parse(argv[1:])
    return _construct_parms(opts, args)


def _parse(argv):
    try:
        opts, args = getopt.getopt(argv, "hf:", ["launch_conf="])
    except getopt.GetoptError:
        print('test.py -f <launch_conf> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('benchmark.py -f <launch_conf>')
            sys.exit()
    return opts, args


def _construct_parms(opts, args):
    flag = False
    params = Params(tasks=['univariate-forecast'],
                    data_sizes=['small', 'medium', 'large'],
                    frameworks=['hyperts_stat'])
    for opt, arg in opts:
        if opt == '-h':
            print('benchmark.py -f <launch_conf>')
            sys.exit()
        elif opt in ("-f", "--launch_conf"):
            logger.info('load params from {}'.format(arg))
            f = open(arg, 'r', encoding='utf-8')
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

            for key in dir(params):
                if key in config:
                    setattr(params, key, config[key])
            params.conf_path = arg
            f.close()
            flag = True
    if not flag:
        logger.error('please input -f hyperbk.yaml')
        exit(0)

    return params
