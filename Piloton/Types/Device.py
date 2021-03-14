import asyncio
from typing import Callable

from Piloton.Mixins import BleakMixin, LoggingMixin
from Piloton.Types.LoopStatus import LoopStatus


class Device(LoggingMixin, BleakMixin):  # type: ignore
    def __init__(self, name: str):
        """
        Create device, set up logger, name, and BLE address

        :param str name: Bluetooth searchable name of device
        """
        # Call to Super
        super().__init__()

        self.name: str = name
        self.loop_status = LoopStatus.ACTIVE
        self.ble_address: str = ""

    def scan_for_device(self, loop: asyncio.AbstractEventLoop) -> bool:
        """
         Scan for device and set BLE address

        :param asyncio.AbstractEventLoop loop: Main Asyncio loop to use
        :return: True, if device found. False, else.
        :rtype: bool
        """
        # Warn, if address is already present
        if self.ble_address:
            self.logger.warning("Scanning for device, but address already present: %s", self.ble_address)

        # Start scanning process
        self.logger.info("Scanning for BLE Device by Name: %s", self.name)

        # Attempt to find device
        self.loop_status = LoopStatus.ACTIVE
        escape_counter: int = 0  # Give up after 5 tries
        result: bool = True
        while not self.ble_address and self.loop_status == LoopStatus.ACTIVE:
            # Use Asyncio loop to find bike
            ble_address = loop.run_until_complete(self.scan())

            if ble_address:
                self.ble_address = ble_address
                self.logger.debug("Setting device (%s) to BLE address (%s)", self.name, self.ble_address)
                self.loop_status = LoopStatus.INACTIVE
            else:
                if escape_counter < 4:
                    escape_counter += 1
                else:
                    self.logger.warning("Unable to find device (%s).")
                    result = False

                self.logger.warning("Unable to find device (%s). Retrying...", self.name)

        self.loop_status = LoopStatus.INACTIVE
        return result

    def poll_device(self, data_handler: Callable, data_uuid: str = ""):
        return super().poll_device(data_handler, data_uuid)
