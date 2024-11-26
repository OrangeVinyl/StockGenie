import sys
import logging

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger
