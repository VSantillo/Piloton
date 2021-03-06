from math import inf

from Piloton.Types.PowerZone import PowerZone
from Piloton.Types.Zone import Zone
from Piloton.Types.Zones import Zones


class PowerZones(Zones):
    ZONES = {
        PowerZone.NO_ZONE: -inf,
        PowerZone.ACTIVE_RECOVERY: 0.55,
        PowerZone.ENDURANCE: 0.75,
        PowerZone.TEMPO: 0.90,
        PowerZone.LACTATE_THRESHOLD: 1.05,
        PowerZone.VO2_MAX: 1.20,
        PowerZone.ANAEROBIC_CAPACITY: 1.50,
        PowerZone.NEUROMUSCULAR_POWER: inf,
    }

    COLORS = {
        PowerZone.NO_ZONE: "#85AAD5",
        PowerZone.ACTIVE_RECOVERY: "#47BAAB",
        PowerZone.ENDURANCE: "#B6C254",
        PowerZone.TEMPO: "#D1A438",
        PowerZone.LACTATE_THRESHOLD: "#CD9333",
        PowerZone.VO2_MAX: "#D3700E",
        PowerZone.ANAEROBIC_CAPACITY: "#DF5054",
        PowerZone.NEUROMUSCULAR_POWER: "#BF211E",
    }

    def __init__(self, ftp: int):
        """
        Initialize Power Zones
        :param ftp:
        """
        self.ftp = ftp
        super().__init__()

    def calculate_power_zone(self, power: float) -> Zone:
        """
        Calculate current Power Zone

        :param power: Power (W) from Indoor Bike Data
        :return: Current Power Zone
        :rtype: Zone
        """
        # Calculate Power as % of FTP
        power_percent: float = power / self.ftp
        power_zone: Zone = self.calculate_zone(power_percent)
        return power_zone
