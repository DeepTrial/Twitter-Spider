#! /usr/bin/env python3

import logging
import logging.handlers

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler2 = logging.StreamHandler()
    handler2.setLevel(logging.WARNING)

    handler1 = logging.FileHandler(filename="runtime.log")
    handler1.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] - (%(filename)s) - %(levelname)s: %(message)s")
    handler1.setFormatter(formatter)
    handler2.setFormatter(formatter)

    logger.addHandler(handler1)
    logger.addHandler(handler2)
    return logger