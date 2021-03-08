import os
import json
import signal
import asyncio
import logging
from datetime import datetime
from typing import List, Dict

from Piloton.Devices import Bike, HRM
from Piloton.Mixins import BleakMixin, InfluxMixin, LoggingMixin, RichMixin
from Piloton.Types import Device, HeartZone, HeartZones, LoopStatus, Menu, PowerZone, PowerZones
from Piloton.UI.Menus import MainMenu
from Piloton.UI.Displays import LiveMetrics


class Piloton(InfluxMixin, RichMixin, BleakMixin, LoggingMixin):  # type: ignore
    def __init__(self, data_path: str = "data/"):
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
        self.loop_tracker: Dict[str, LoopStatus] = {}
        # Detect if data_path is present
        if not os.path.exists(data_path):
            self.logger.critical("Unable to find Piloton data path. Quitting now.")
            exit(1)
        self.data_path = data_path

        # Load Device data
        with open(f"{self.data_path}devices.json", "r") as fh:
            device_info = json.load(fh)
            self.logger.info("Device Data Loaded")

        # Load User data
        with open(f"{self.data_path}users.json", "r") as fh:
            user_info = json.load(fh)
            self.logger.info("User Data Loaded")

        # Set up our devices
        self.bike: Bike = Bike(device_info["bike"])
        self.hrm: HRM = HRM(device_info["hrm"])
        self.devices: List[Device] = [self.bike, self.hrm]

        # Set up performance metrics
        self.heart_zone: HeartZone = HeartZone.NO_ZONE
        self.heart_zones: HeartZones = HeartZones(age=user_info["age"])
        self.power_zone: PowerZone = PowerZone.NO_ZONE
        self.power_zones: PowerZones = PowerZones(ftp=user_info["ftp"])

        # Attach signal handlers
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)

    def update(self) -> None:
        """
        Update User and Device data from json
        """
        # Load Device data
        with open(f"{self.data_path}devices.json", "r") as fh:
            device_info = json.load(fh)
            self.logger.info("Device Data Loaded")

        # Load User data
        with open(f"{self.data_path}users.json", "r") as fh:
            user_info = json.load(fh)
            self.logger.info("User Data Loaded")

        # Set up our devices
        self.bike = Bike(device_info["bike"])
        self.hrm = HRM(device_info["hrm"])
        self.devices = [self.bike, self.hrm]

        # Set up performance metrics
        self.heart_zones = HeartZones(age=user_info["age"])
        self.power_zones = PowerZones(ftp=user_info["ftp"])

    def stop(self, *args, **kwargs) -> None:
        """
        Stop asyncio loops by sending a signal that should break them

        :param args: Unnecessary, don't include
        :param kwargs: Unnecessary, don't include
        :return: Nothing
        """
        # Find active device loops
        for device in self.devices:
            if device.loop_status != LoopStatus.INACTIVE:
                device.loop_status = LoopStatus.INACTIVE

        # Find active non-device loops
        for loop, value in self.loop_tracker.items():
            if value != LoopStatus.INACTIVE:
                self.loop_tracker[loop] = LoopStatus.INACTIVE

    def scan_for_devices(self) -> bool:
        """
        Scan for devices

        :return: True, if all devices found. False, else.
        :rtype: bool
        """
        # Attempt to scan for all devices
        for device in self.devices:

            # Attempt to find device
            device_found: bool = device.scan_for_device(self._loop)
            if not device_found:
                return False

        return True

    def __indoor_bike_data_handler(self, sender, data):
        # Update Bike with data
        self.bike.update(data)

        # Calculate Power Zone
        self.power_zone = self.power_zones.calculate_power_zone(self.bike.power)

        # Write data point to Influx
        data_point = [
            {
                "measurement": "indoor_bike_data",
                "tags": {},
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "speed": self.bike.speed,
                    "cadence": self.bike.cadence,
                    "power": self.bike.power,
                    "power_zone": self.power_zone.value,
                },
            }
        ]
        self.influx_client.write_points(data_point)

    def __hrm_data_handler(self, sender, data):
        # Update HRM with data
        self.hrm.update(data)

        # Calculate Heart Zone
        self.heart_zone = self.heart_zones.calculate_heart_zone(self.hrm.heart_rate)

        # Write data point to Influx
        data_point = [
            {
                "measurement": "heart_rate_monitor",
                "tags": {},
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "heart_rate": self.hrm.heart_rate,
                    "zone": self.heart_zone.value,
                },
            }
        ]
        self.influx_client.write_points(data_point)

    def poll_indoor_bike_data(self):
        return self._loop.run_until_complete(self.bike.poll_device(self.__indoor_bike_data_handler))

    def poll_hrm_data(self):
        return self._loop.run_until_complete(self.hrm.poll_device(self.__hrm_data_handler))

    def poll_data(self, live_metrics):
        tasks = asyncio.gather(
            *(
                self.bike.poll_device(self.__indoor_bike_data_handler),
                self.hrm.poll_device(self.__hrm_data_handler),
                live_metrics.live_output(),
            )
        )
        return self._loop.run_until_complete(tasks)

    def start_workout(self, length: int):
        """
        Start Workout of length. If no length, run until Ctrl+C

        :param length:
        :return:
        """
        # Scan for bike
        self.logger.info("Scanning for devices before starting workout.")
        self.scan_for_devices()

        self.logger.info("Beginning workout!")
        return self.poll_data(LiveMetrics(self))

    def app(self):
        """

        :return:
        """
        active: bool = True
        current_view = MainMenu
        last_menu = MainMenu
        while active:
            # Call current view
            if callable(current_view):
                current_view = current_view()

            # Render Menu
            if isinstance(current_view, Menu):
                # Show menu and prompt user for input
                selection: int = self.render_menu(current_view)

                # Set up breadcrumb to return to this menu, if form
                last_menu = current_view

                # Handle the selection, returning if none.
                current_view = current_view.handle_selection(selection)
                if current_view is None:
                    self.logger.info("Quitting Piloton")
                    active = False

            # Render "Form"
            if isinstance(current_view, list):
                response = self.render_form(current_view)
                if isinstance(response, int):
                    self.start_workout(response)  # Live view will override here
                    current_view = MainMenu
                elif response is not None:
                    current_view = response()
                else:
                    current_view = last_menu
