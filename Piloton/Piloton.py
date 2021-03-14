import os
import json
import signal
import asyncio

from datetime import datetime
from typing import List, Dict, MutableMapping, Tuple

from Piloton.Devices import Bike, HRM
from Piloton.Mixins import InfluxMixin, LoggingMixin, RichMixin
from Piloton.Types import Device, HeartZone, HeartZones, LoopStatus, Menu, PowerZone, PowerZones
from Piloton.UI.Menus import MainMenu
from Piloton.UI.Displays import LiveMetrics, TrainingMetrics


class Piloton(LoggingMixin, InfluxMixin, RichMixin):  # type: ignore
    def __init__(self, data_path: str = "data/"):
        """
        Initialize Piloton

        :param str data_path: Path to directory containing device, user, and training data
        """
        # Influx members
        self.influx_host: str = "localhost"
        self.influx_port: str = "8086"
        self.influx_username: str = "root"
        self.influx_password: str = "root"
        self.influx_database: str = "piloton"

        # Call to Super
        super().__init__()
        self.logger.info("Piloton is starting up!")

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

        # Set up our Asyncio loop and tracker
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.loop_tracker: Dict[str, LoopStatus] = {}

        # Set up our devices
        self.bike: Bike = Bike(device_info["bike"])
        self.hrm: HRM = HRM(device_info["hrm"])
        self.devices: List[Device] = [self.bike, self.hrm]

        # Set up performance metrics
        self.heart_zone: HeartZone = HeartZone.NO_ZONE
        self.heart_zones: HeartZones = HeartZones(age=user_info["age"])
        self.power_zone: PowerZone = PowerZone.NO_ZONE
        self.power_zones: PowerZones = PowerZones(ftp=user_info["ftp"])

        # Set up training data
        self.training_data: MutableMapping[int, MutableMapping[int, List[Tuple[int, float]]]] = {}
        for resistance in range(0, 100):
            self.training_data[resistance] = {cadence: [] for cadence in range(20, 131)}

        # Load in training data from json
        training_data_path = f"{self.data_path}training.json"
        with open(training_data_path, "r") as fh:
            training_data = json.load(fh)

        if not training_data:
            # Write default data to json
            with open(f"{self.data_path}training.json", "w+") as fh:
                json.dump(self.training_data, fh, indent=4)
        else:
            # Load in values
            for resistance in range(0, 100):
                for cadence in range(20, 131):
                    self.training_data[resistance][cadence] = training_data[str(resistance)][str(cadence)]

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

        :param args: [Unused]
        :param kwargs: [Unused]
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

    def __indoor_bike_data_training_handler(self, sender, data):
        """
        When training, update the bike data and write bike data to Piloton's training data.

        :param sender: [Unused] Data sender
        :param data: Data
        :return: Nothing.
        """
        # Update Bike with Data
        self.bike.update(data)

        # To somewhat curb overfitting, there's a hard limit of 25 samples per resistance-cadence.
        if self.bike.cadence > 20:
            if len(self.training_data[self.bike.resistance][self.bike.cadence]) < 26:
                self.training_data[self.bike.resistance][self.bike.cadence].append((self.bike.power, self.bike.speed))

    def __indoor_bike_data_workout_handler(self, sender, data):
        """
        When working out, update the bike data and write bike data to InfluxDB

        :param sender: [Unused] Data sender
        :param data: Data
        :return: None
        """
        # Update Bike with data
        self.bike.update(data)

        # Calculate Power Zone
        self.power_zone = self.power_zones.calculate_power_zone(self.bike.power)

        # Write data point to Influx
        fields: Dict = {
            "speed": self.bike.speed,
            "cadence": self.bike.cadence,
            "power": self.bike.power,
            "power_zone": self.power_zone.value,
        }
        self.write_data_point(
            measurement="indoor_bike_data",
            tags={},
            time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            fields=fields,
        )

    def __hrm_data_workout_handler(self, sender, data):
        """
        When working out, update the hrm data and write hrm data to Influx DB

        :param sender: [Unused] Data sender
        :param data: Data
        :return: None
        """
        # Update HRM with data
        self.hrm.update(data)

        # Calculate Heart Zone
        self.heart_zone = self.heart_zones.calculate_heart_zone(self.hrm.heart_rate)

        # Write data point to Influx
        fields: Dict = {"heart_rate": self.hrm.heart_rate, "zone": self.heart_zone.value}
        self.write_data_point(
            measurement="heart_rate_monitor",
            tags={},
            time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            fields=fields,
        )

    def poll_indoor_bike_data(self):
        """
        Just poll indoor bike data
        """
        return self._loop.run_until_complete(self.bike.poll_device(self.__indoor_bike_data_workout_handler))

    def poll_hrm_data(self):
        """
        Poll just HRM data
        """
        return self._loop.run_until_complete(self.hrm.poll_device(self.__hrm_data_workout_handler))

    def start_workout(self):
        """
        Start Workout of length. If no length, run until Ctrl+C
        """
        # Train bike on training data
        self.bike.train(self.training_data)

        # Scan for devices
        if not self.bike.ble_address or not self.hrm.ble_address:
            self.logger.info("Scanning for devices before training.")
            self.devices = [self.bike, self.hrm]

            self.scan_for_devices()

        self.logger.info("Beginning workout!")
        tasks = asyncio.gather(
            *(
                self.bike.poll_device(self.__indoor_bike_data_workout_handler),
                self.hrm.poll_device(self.__hrm_data_workout_handler),
                LiveMetrics(self).live_output(),
            )
        )
        return self._loop.run_until_complete(tasks)

    def start_training(self, resistance: int):
        """
        Start training on resistance. Run until Ctrl+C.

        :param int resistance: Resistance being trained
        :return:
        """

        # Scan for devices
        if not self.bike.ble_address:
            self.logger.info("Scanning for devices before training.")
            self.devices = [self.bike]
            self.scan_for_devices()

        self.logger.info("Beginning training!")
        tasks = asyncio.gather(
            *(
                self.bike.poll_device(self.__indoor_bike_data_training_handler),
                TrainingMetrics(self, resistance).live_output(),
            )
        )
        return self._loop.run_until_complete(tasks)

    def app(self):
        """
        Main Piloton app loop
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
                if response is None:
                    current_view = last_menu
                elif "workout" in response:
                    self.bike.training = False
                    self.start_workout()  # Live view will override here
                    current_view = MainMenu
                elif "training" in response:
                    self.bike.training = True
                    self.start_training(response[1])
                    self.bike.training = False

                    # Save training data to json data
                    with open(f"{self.data_path}training.json", "w+") as fh:
                        json.dump(self.training_data, fh, indent=4)
                elif response is not None:
                    current_view = response()
