from enum import Enum


class Zone(Enum):
    """
    Base representation of a Piloton Zone
    """

    def __str__(self) -> str:
        return " ".join(self.name.split("_")).title()  # NO_ZONE -> "No Zone"
