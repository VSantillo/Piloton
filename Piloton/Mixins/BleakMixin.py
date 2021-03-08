import asyncio
from typing import TYPE_CHECKING, List, Callable

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

from Piloton.Types.LoopStatus import LoopStatus


# Only import when type_checking
if TYPE_CHECKING:
    from Piloton.Types import Device

    _Base = Device
else:
    _Base = object


class BleakMixin(_Base):  # type: ignore
    async def scan(self) -> str:
        """
        Asynchronously scan for device using name

        :return: BLE address (if found)
        :rtype: str
        """
        # Scan for devices for about 5 seconds
        devices: List[BLEDevice] = await BleakScanner.discover(timeout=5)

        # Iterate through results to find BLE name to return address
        address = ""
        for device in devices:
            if device.name == self.name:
                address = device.address
                self.logger.info("Found devices (%s) at address (%s)", self.name, address)
                break

        return address

    async def poll_device(self, data_handler: Callable, data_uuid: str):
        self.loop_status = LoopStatus.CONNECTING  # For display purposes, need to connect before loading UI
        async with BleakClient(self.ble_address) as client:
            # Wait until we're connected with the device
            connected = await client.is_connected()
            self.logger.debug("Device (%s) Connected: %s", self.ble_address, connected)

            # Start Notify on UUID and process it on the handler
            self.loop_status = LoopStatus.ACTIVE
            await client.start_notify(data_uuid, data_handler)

            # Wait until another process asks this to stop
            while self.loop_status == LoopStatus.ACTIVE:
                await asyncio.sleep(1.0)

            # Stop notify when loop is no longer active
            await client.stop_notify(data_uuid)
