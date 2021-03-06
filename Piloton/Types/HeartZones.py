from math import inf

from Piloton.Types.HeartZone import HeartZone
from Piloton.Types.Zone import Zone
from Piloton.Types.Zones import Zones


class HeartZones(Zones):
    ZONES = {
        HeartZone.NO_ZONE: -inf,
        HeartZone.WARM_UP: 0.65,
        HeartZone.ENDURANCE: 0.75,
        HeartZone.POWER: 0.85,
        HeartZone.THRESHOLD: 0.95,
        HeartZone.MAX_CAPACITY: inf,
    }

    COLORS = {
        HeartZone.NO_ZONE: "#85AAD5",
        HeartZone.WARM_UP: "#FEDD55",
        HeartZone.ENDURANCE: "#F7A64F",
        HeartZone.POWER: "#FB8341",
        HeartZone.THRESHOLD: "#F65555",
        HeartZone.MAX_CAPACITY: "#EE4D5C",
    }

    def __init__(self, age: int):
        """
        Initialize Heart Zones

        :param int age: Age of user
        """
        self.age: int = age
        self.maximum_heart_rate: float = 207 - (age * 0.7)
        super().__init__()

    def calculate_heart_zone(self, heart_rate: int) -> Zone:
        """
        Figure out which heart zone user

        :param int heart_rate: Heart Rate as recorded by connected HRM
        :return: Current Heart Zone
        :rtype: Zone
        """
        # Calculate HR as % of MHR
        hr_percent = heart_rate / self.maximum_heart_rate
        heart_zone: Zone = self.calculate_zone(hr_percent)
        return heart_zone
