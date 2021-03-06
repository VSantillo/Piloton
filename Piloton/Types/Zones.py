from math import inf
from typing import MutableMapping

from Piloton.Types.Zone import Zone


class Zones:
    ZONES: MutableMapping[Zone, float] = {}

    COLORS: MutableMapping[Zone, str] = {}

    def __init__(self):
        """
        Initialize Zones -- stub
        """

    def calculate_zone(self, comparison_value: float) -> Zone:
        """
        Calculate which zone parameter is in based on comparison_value

        :param float comparison_value: Value to be compared
        :return: Current Zone
        :rtype: Zone
        """
        # Find Zone by iterating over Zone(s)
        range_min: float = -inf
        range_max: float
        for zone, threshold in self.ZONES.items():
            # Set upper limit
            range_max = threshold

            # Return current zone, if within threshold
            if range_min < comparison_value <= range_max:
                return zone

        return Zone(0)
