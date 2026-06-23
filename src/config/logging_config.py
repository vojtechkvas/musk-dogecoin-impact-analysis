import logging.config
import sys
from datetime import datetime
import os

os.makedirs("logs", exist_ok=True)

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {"format": "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(name)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": f"logs/app_{current_time}.log",
            "maxBytes": 10_485_760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        # The root logger handles everything unless overridden
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
