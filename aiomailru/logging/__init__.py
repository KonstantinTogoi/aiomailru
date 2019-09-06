import logging.config
import yaml
from os.path import dirname, join


with open(join(dirname(__file__), 'config.yaml')) as f:
    config = yaml.safe_load(f)


logging.config.dictConfig(config['logging'])
