from enum import Enum


class LoopStatus(Enum):
    """
    Keep track of asyncio loop status.
    """

    INACTIVE = 0
    ACTIVE = 1
