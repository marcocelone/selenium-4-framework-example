import inspect
import logging
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "automation.log")


def customLogger(log_level: int = logging.DEBUG) -> logging.Logger:
    # Gets the name of the class / method from where this method is called
    logger_name = inspect.stack()[1][3]
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(LOG_FILE, mode="a")
        file_handler.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s: %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
