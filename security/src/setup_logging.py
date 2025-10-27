import json
import logging
import logging.config
import pathlib

from .config import settings


def setup_logging():
    config_file = pathlib.Path('src/logging_config.json')
    with open(config_file, encoding='utf-8') as f_in:
        config = json.load(f_in)
    config['loggers']['root']['level'] = settings.LOGGING_LEVEL
    logging.config.dictConfig(config)
