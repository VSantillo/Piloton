from typing import Callable

from Piloton.Types import Device


class HRM(Device):
    def __init__(self, name: str):
        """
        Sets up HRM BLE device

        :param name: Name of device to be searched for
        """
        # Call to super
        super().__init__(name)

        # Set up heart rate monitor instance members
        self.heart_rate: int = 0  # BPM
        self.hrm_data_uuid: str = "00002a37-0000-1000-8000-00805f9b34fb"

    def update(self, data):
        # Unpack from data bytes
        data_bytes: bytes = bytes(data)

        self.heart_rate = int.from_bytes(data_bytes, "big")

    def poll_device(self, data_handler: Callable, data_uuid: str = ""):
        return super().poll_device(data_handler, self.hrm_data_uuid)
