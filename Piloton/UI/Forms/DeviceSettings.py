import json
from rich.prompt import Prompt

from Piloton.Types import Form, FormPrompt


class DeviceSettings(Form):

    __formname__ = "Device Settings"

    @staticmethod
    def update_bike_name():
        return [FormPrompt(Prompt, DeviceSettings._update_bike_name, "Update Bike Name")]

    @staticmethod
    def _update_bike_name(response):
        # Open JSON
        with open("data/devices.json", "r") as fh:
            # Load JSON
            data = json.load(fh)

        # Set Name
        data["bike"] = response

        with open("data/devices.json", "w") as fh:
            # Write
            json.dump(data, fh, indent=4)

    @staticmethod
    def update_hrm_name():
        return [FormPrompt(Prompt, DeviceSettings._update_hrm_name, "Update HRM Name")]

    @staticmethod
    def _update_hrm_name(response):
        # Open JSON
        with open("data/devices.json", "r") as fh:
            # Load JSON
            data = json.load(fh)

        # Set Name
        data["hrm"] = response

        with open("data/devices.json", "w") as fh:
            # Write
            json.dump(data, fh, indent=4)
