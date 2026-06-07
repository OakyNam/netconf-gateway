"""
Loguru logger initialization using JSON config for the NETCONF API gateway.
"""

import json
import os
import logging
import logging.config
from loguru import logger

def _resolve_logging_config_path() -> str:
    configured = os.path.join(os.path.dirname(__file__), "../config/logging_config.json")
    if os.path.exists(configured):
        return configured
    return configured.replace("logging_config.json", "logging_config.example.json")


CONFIG_PATH = _resolve_logging_config_path()

class InterceptHandler(logging.Handler):
    """
    Forwards standard logging records to Loguru.
    """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

def setup_logging_from_json():
    """
    Set up logging using standard logging config and bridge Loguru to standard logging.
    """
    with open(CONFIG_PATH, 'r') as f:
        cfg = json.load(f)

    # Remove all Loguru handlers
    logger.remove()

    # Set up standard logging config (handlers, formatters, etc.)
    logging.config.dictConfig(cfg)

    # Bridge standard logging to Loguru
    logging.root.handlers = [InterceptHandler()]
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = [InterceptHandler()]
