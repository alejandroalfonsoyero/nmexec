import logging
import os


def get_logger(name: str) -> logging.Logger:
    level = os.environ.get("LOG_LEVEL", "info").lower()
    if level == "critical":
        level = logging.CRITICAL
    elif level == "error":
        level = logging.ERROR
    elif level == "warn":
        level = logging.WARN
    elif level == "debug":
        level = logging.DEBUG
    elif level == "notset":
        level = logging.NOTSET
    else:
        level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
