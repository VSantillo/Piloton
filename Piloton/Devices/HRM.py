from typing import Callable

from Piloton.Types import Device, LoopStatus


class HRM(Device):
    def __init__(self, name: str):
        """
        Initialize Heart Rate Monitor (HRM)

        :param name: Heart Rate Monitor Name
        """
        # Call to super
        super().__init__(name)

        # Set up heart rate monitor instance members
        self.heart_rate: int = 0  # BPM
        self.hrm_data_uuid: str = "00002a37-0000-1000-8000-00805f9b34fb"
        self.loop_status: LoopStatus = LoopStatus.INACTIVE

    def update(self, data) -> None:
        """
        Update hrm parameters with data received from heart rate monitor

        :param data: Heart Rate Monitor data
        """
        # Unpack from data bytes
        data_bytes: bytes = bytes(data)

        # Set heart rate from data
        self.heart_rate = int.from_bytes(data_bytes, "big")

    def poll_device(self, data_handler: Callable, data_uuid: str = ""):
        """
        Function to call base class poll device

        :param Callable data_handler: Function to handle data
        :param str data_uuid: UUID to list to data on
        :return: Asyncio loop
        """
        return super().poll_device(data_handler, self.hrm_data_uuid)
