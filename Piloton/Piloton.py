import array
import signal
import asyncio
import logging
import datetime
from typing import MutableMapping

from Piloton.Types import HeartZone, HeartZones, LoopStatus, PowerZone, PowerZones
from Piloton.Mixins import BleakMixin, InfluxMixin, RichMixin


# TODO: User-specific, set in JSON or CLI
FTP: int = 195
AGE: int = 27

# Significant data UUIDs
INDOOR_BIKE_DATA_UUID = "00002ad2-0000-1000-8000-00805f9b34fb"
HRM_DATA_UUID = "00002a37-0000-1000-8000-00805f9b34fb"


class Piloton(InfluxMixin, RichMixin, BleakMixin):  # type: ignore
    def __init__(self, bike_name: str, hrm_name: str):
        # Set up Logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Piloton is starting up!")

        # Influx members
        self.influx_host: str = "localhost"
        self.influx_port: str = "8086"
        self.influx_username: str = "root"
        self.influx_password: str = "root"
        self.influx_database: str = "piloton"

        # Call to Super
        super().__init__()

        # Set up our Asyncio loop and tracker
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._loop_tracker: MutableMapping[str, LoopStatus] = {}

        # Set our Bluetooth-related variables
        self.bike_name: str = bike_name
        self.hrm_name: str = hrm_name
        self.bike_ble_address: str = ""
        self.hrm_ble_address: str = ""

        # Set our Physical Bike Metrics (all instantaneous forms)
        self.bike_speed: float = 0.0  # mph
        self.bike_cadence: int = 0  # rpm
        self.bike_power: int = 0  # Watts
        self.bike_resistance: int = 0  # Unitless, IC4 resistance
        self.heart_rate: int = 0  # BPM

        # Set up our Zone information
        self.heart_zone: HeartZone = HeartZone.NO_ZONE
        self.power_zone: PowerZone = PowerZone.NO_ZONE
        self.power_zones: PowerZones = PowerZones(ftp=FTP)
        self.heart_zones: HeartZones = HeartZones(age=AGE)

        # Attach signal handlers
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)

    def stop(self, *args, **kwargs) -> None:
        """
        Stop asyncio loops by sending a signal that should break them

        :param args: Unnecessary, don't include
        :param kwargs: Unnecessary, don't include
        :return: Nothing
        """
        # Find active loops
        for loop, value in self._loop_tracker.items():
            if value == LoopStatus.ACTIVE:
                self._loop_tracker[loop] = LoopStatus.INACTIVE

    def __indoor_bike_data_handler(self, sender, data):
        # Unpack from data bytes
        data_bytes: bytes = bytes(data)[:-1]
        data_array: array = array.array("h", data_bytes)  # 'h' = treat data as 2-byte short

        # TODO: This block assumes that the bike being listened to only broadcasts 0x44-02 in its prefix.
        #  To support multiple bikes, this portion should be addressable based on the features string.
        #  However, because I don't have access to that information (and subsequently know what
        #  transformations are necessary), this block is hardcoded for the IC4.
        features: int = data_array[0]
        speed: int = data_array[1]  # This value is always km/h
        cadence: int = data_array[2]
        power: int = data_array[3]

        # Set physical bike metrics
        self.bike_speed = (speed / 100) * 0.6213711922
        self.bike_cadence = cadence * 0.5
        self.bike_power = power

        # TODO: Predict resistance here
        self.bike_resistance = 17
        self.power_zone = self.power_zones.calculate_power_zone(power)

        # Write data point to Influx
        data_point = [
            {
                "measurement": "indoor_bike_data",
                "tags": {},
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "speed": self.bike_speed,
                    "cadence": self.bike_cadence,
                    "power": self.bike_power,
                    "power_zone": self.power_zone.value,
                },
            }
        ]
        self.influx_client.write_points(data_point)

    def __hrm_data_handler(self, sender, data):
        # Unpack from data bytes
        data_bytes: bytes = bytes(data)

        self.heart_rate = int.from_bytes(data_bytes, "big")
        self.heart_zone = self.heart_zones.calculate_heart_zone(self.heart_rate)

        # Write data point to Influx
        data_point = [
            {
                "measurement": "heart_rate_monitor",
                "tags": {},
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "heart_rate": self.heart_rate,
                    "zone": self.heart_zone.value,
                },
            }
        ]
        self.influx_client.write_points(data_point)

    def scan_for_bike(self) -> None:
        """
        Scan for device and set BLE address
        """
        # Warn, if address is already present
        if self.bike_ble_address:
            self.logger.warning("Scanning for Bike, but address already present.")

        # Start scanning process
        self.logger.info("Scanning for BLE Device by Name: %s", self.bike_name)

        escape_counter: int = 0  # Give up after 5 tries
        while not self.bike_ble_address:
            # Use Asyncio to find bike
            ble_address = self._loop.run_until_complete(self.__scan_for_device(device_name=self.bike_name))

            if ble_address:
                self.logger.debug("Setting self.bike_ble_address = %s", ble_address)
                self.bike_ble_address = ble_address
            else:
                self.logger.warning("Unable to find bike. Retrying...")
                if escape_counter < 4:
                    escape_counter += 1
                else:
                    self.logger.warning("Unable to find bike.")

                    # TODO: Figure out how to handle this elegantly.
                    exit()

    def scan_for_hrm(self) -> None:
        """
        Scan for device and set BLE address
        """
        # Warn, if address is already present
        if self.hrm_ble_address:
            self.logger.warning("Scanning for HRM, but address already present")

        # Start scanning process
        self.logger.info("Scanning for BLE Device by Name: %s", self.hrm_name)

        escape_counter: int = 0  # Give up after 5 tries
        while not self.hrm_ble_address:
            ble_address = self._loop.run_until_complete(self.__scan_for_device(device_name=self.hrm_name))

            if ble_address:
                self.logger.debug("Setting self.hrm_ble_address = %s", ble_address)
                self.hrm_ble_address = ble_address
            else:
                self.logger.warning("Unable to find HRM. Retrying...")
                if escape_counter < 4:
                    escape_counter += 1
                else:
                    self.logger.warning("Unable to find HRM.")

                    # TODO: Figure out how to handle this elegantly.
                    exit()

    def poll_indoor_bike_data(self):
        return self._loop.run_until_complete(
            self.__poll_device(self.bike_ble_address, INDOOR_BIKE_DATA_UUID, self.__indoor_bike_data_handler)
        )

    def poll_hrm_data(self):
        return self._loop.run_until_complete(
            self.__poll_device(self.hrm_ble_address, HRM_DATA_UUID, self.__hrm_data_handler)
        )

    def poll_data(self):
        tasks = asyncio.gather(
            *(
                self._live_output(),
                self.__poll_device(self.bike_ble_address, INDOOR_BIKE_DATA_UUID, self.__indoor_bike_data_handler),
                self.__poll_device(self.hrm_ble_address, HRM_DATA_UUID, self.__hrm_data_handler),
            )
        )
        return self._loop.run_until_complete(tasks)
