from logging.config import dictConfig
from config import logging


def init_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": logging["format"],
                    "datefmt": logging["date_format"],
                }
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"handlers": ["default"], "level": logging["level"]},
        }
    )
