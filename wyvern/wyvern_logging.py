# -*- coding: utf-8 -*-
import logging
import logging.config
import os

import yaml

logger = logging.getLogger(__name__)


def setup_logging():
    # this log_config.yml file path is changed compared to the original library code
    path = os.path.abspath("log_config.yml")

    if os.path.exists(path):
        with open(path, "rt") as f:
            try:
                config = yaml.safe_load(f.read())

                # logfile_path = config["handlers"]["file"]["filename"]
                # os.makedirs(logfile_path, exist_ok=True)
                logging.config.dictConfig(config)
            except Exception as e:
                logger.error("Error in Logging Configuration. Using default configs")
                raise e
                # logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
        logger.warning("Failed to load configuration file. Using default configs")
