#!/usr/bin/env python3
import logging
import argparse

from Piloton import Piloton
from utils import setup_logger, set_logger_level


# Bluetooth-discoverable names
BIKE_NAME = "IC Bike"
HEART_RATE_MONITOR_NAME = "CL831-0318513"


def arg_parse():
    """
    Argument parsing handler
    :return:
    """
    # Set up Argument Parser
    arg_parser = argparse.ArgumentParser()

    # Add arguments
    arg_parser.add_argument(
        "-t", "--test_display", action="store_true", dest="TEST_DISPLAY"
    )
    arg_parser.add_argument(
        "-b", "--bike_name", type=str, dest="BIKE_NAME", default=BIKE_NAME
    )
    arg_parser.add_argument(
        "-p", "--hrm_name", type=str, dest="HRM_NAME", default=HEART_RATE_MONITOR_NAME
    )

    return arg_parser.parse_args()


if __name__ == "__main__":
    # Set up root logger
    logger = setup_logger(logging_level=logging.DEBUG)
    set_logger_level("bleak", logging_level=logging.WARNING)
    set_logger_level("urllib3", logging_level=logging.WARNING)
    set_logger_level("asyncio", logging_level=logging.WARNING)

    # Parse arguments
    args = arg_parse()

    # Set up Piloton
    piloton: Piloton = Piloton(bike_name=args.BIKE_NAME, hrm_name=args.HRM_NAME)

    # Test output
    if args.TEST_DISPLAY:
        logger.info("Testing display!")
        piloton.test_display()
