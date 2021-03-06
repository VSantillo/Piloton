import asyncio
import array
from datetime import datetime
from typing import TYPE_CHECKING, List, Callable
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from Piloton.Types import LoopStatus


# Only import when type_checking
if TYPE_CHECKING:
    from Piloton import Piloton

    _Base = Piloton
else:
    _Base = object


class BleakMixin(_Base):  # type: ignore
    async def __scan_for_device(self, device_name: str) -> str:
        """
        Asynchronously scan for device using name

        :param device_name: Name of Bluetooth device
        :return: BLE address (if found)
        :rtype: str
        """
        # Scan for devices for about 5 seconds
        devices: List[BLEDevice] = await BleakScanner.discover(timeout=5)

        # Iterate through results to find BLE name to return address
        address = ""
        for device in devices:
            if device.name == device_name:
                address = device.address
                self.logger.info("Found devices (%s) at address (%s)", device_name, address)
                break

        return address

    async def __poll_device(self, device_address: str, data_uuid: str, data_handler: Callable):
        async with BleakClient(device_address) as client:
            # Wait until we're connected with the device
            connected = await client.is_connected()
            self.logger.debug("Device (%s) Connected: %s", device_address, connected)

            # Set up tracker for this asyncio loop
            poller_name = data_handler.__name__
            if poller_name not in self._loop_tracker:
                self._loop_tracker[poller_name] = LoopStatus.ACTIVE

            # Start Notify on UUID and process it on the handler
            await client.start_notify(data_uuid, data_handler)

            # Wait until another process asks this to stop
            while self._loop_tracker[poller_name] == LoopStatus.ACTIVE:
                await asyncio.sleep(1.0)

            # Stop notify when loop is no longer active
            await client.stop_notify(data_uuid)
