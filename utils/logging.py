import logging


def setup_logger(logging_level: int = logging.INFO) -> logging.Logger:
    """
    Set up a root logger

    :param int logging_level: Level to set root logger at
    :return: Root logger
    :rtype: logging.Logger
    """
    # Get and set root Logger and logging level
    logger = logging.getLogger()
    logger.setLevel(logging_level)

    # Format of Logger message prefix
    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    # Set up stream handler
    handler = logging.StreamHandler()
    handler.setLevel(logging_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def set_logger_level(logger_name: str, logging_level: int) -> None:
    """
    Set logging level for given Logger

    :param str logger_name: Logger to set
    :param int logging_level: Level to set logger at
    """
    # Get logger_name from logging and set to level indicated
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
