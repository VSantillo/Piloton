from Piloton.Types.Zone import Zone


class PowerZone(Zone):
    """
    Power Zone representation
    """

    NO_ZONE = 0
    ACTIVE_RECOVERY = 1
    ENDURANCE = 2
    TEMPO = 3
    LACTATE_THRESHOLD = 4
    VO2_MAX = 5
    ANAEROBIC_CAPACITY = 6
    NEUROMUSCULAR_POWER = 7
