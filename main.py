#!/usr/bin/env python3
import logging

from Piloton import Piloton
from utils import setup_logger, set_logger_level

if __name__ == "__main__":
    # Set up root logger
    logger = setup_logger(logging_level=logging.DEBUG)
    set_logger_level("bleak", logging_level=logging.WARNING)
    set_logger_level("urllib3", logging_level=logging.WARNING)
    set_logger_level("asyncio", logging_level=logging.WARNING)

    # Set up Piloton
    piloton: Piloton = Piloton()

    # Run Piloton
    piloton.app()
