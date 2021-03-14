import logging


class LoggingMixin:
    def __init__(self):
        """
        Set up logger
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        super().__init__()
