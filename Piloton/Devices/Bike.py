import array
from typing import Callable

from Piloton.Types import Device, LoopStatus
from Piloton.Mixins import ClassifierMixin


class Bike(Device, ClassifierMixin):
    def __init__(self, name: str):
        """
        Initialize Bike

        :param str name: Bike name
        """
        # Call to super
        super().__init__(name)

        # Set up bike instance members
        self.speed: float = 0.0  # mph
        self.cadence: int = 0  # rpm
        self.power: int = 0  # Watts
        self.resistance: int = 0  # Unitless, IC4 resistancec
        self.indoor_bike_data_uuid: str = "00002ad2-0000-1000-8000-00805f9b34fb"
        self.loop_status: LoopStatus = LoopStatus.INACTIVE
        self.training: bool = False

    def update(self, data) -> None:
        """
        Update bike parameters with data received from indoor bike data

        :param data: Indoor bike data
        """
        # Unpack from data bytes
        data_bytes: bytes = bytes(data)[:-1]
        data_array: array.array = array.array("h", data_bytes)  # 'h' = treat data as 2-byte short

        # TODO: This block assumes that the bike being listened to only broadcasts 0x44-02 in its prefix.
        #  To support different bikes, this portion should be addressable based on the features.
        #  However, because I don't have access to that information, this block is hardcoded for any
        #  spin bikes broadcast 0x44-02.
        features: int = data_array[0]
        speed: int = data_array[1]  # This value is always received as km/h
        cadence: int = data_array[2]
        power: int = data_array[3]

        # Update bike members
        self.speed = (speed / 100) * 0.6213711922  # Converting to Imperial units
        self.cadence = round(cadence * 0.5)
        self.power = power

        # Predict resistance, if we're not training
        if not self.training:
            self.resistance = self.predict_resistance(self.cadence, self.power, self.speed)

    def poll_device(self, data_handler: Callable, data_uuid: str = ""):
        """
        Function to call base class poll device

        :param Callable data_handler: Function to handle data
        :param str data_uuid: UUID to list to data on
        :return: Asyncio loop
        """
        return super().poll_device(data_handler, self.indoor_bike_data_uuid)
