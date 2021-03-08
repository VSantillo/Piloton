import array
from typing import Callable

from Piloton.Types import Device


class Bike(Device):
    def __init__(self, name: str):
        # Call to super
        super().__init__(name)

        # Set up bike instance members
        self.speed: float = 0.0  # mph
        self.cadence: int = 0  # rpm
        self.power: int = 0  # Watts
        self.resistance: int = 0  # Unitless, IC4 resistancec
        self.indoor_bike_data_uuid: str = "00002ad2-0000-1000-8000-00805f9b34fb"

    def update(self, data):
        # Unpack from data bytes
        data_bytes: bytes = bytes(data)[:-1]
        data_array: array = array.array("h", data_bytes)  # 'h' = treat data as 2-byte short

        # TODO: This block assumes that the bike being listened to only broadcasts 0x44-02 in its prefix.
        #  To support multiple bikes, this portion should be addressable based on the features string.
        #  However, because I don't have access to that information (and subsequently know what
        #  transformations are necessary), this block is hardcoded for the IC4.
        features: int = data_array[0]
        speed: int = data_array[1]  # This value is always received as km/h
        cadence: int = data_array[2]
        power: int = data_array[3]

        # Update bike members
        self.speed = (speed / 100) * 0.6213711922
        self.cadence = round(cadence * 0.5)
        self.power = power
        self.resistance = 17  # TODO: Predict resistance here

    def poll_device(self, data_handler: Callable, data_uuid: str = ""):
        return super().poll_device(data_handler, self.indoor_bike_data_uuid)
