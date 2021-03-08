from Piloton.Types import Menu
from Piloton.UI.Menus import MainMenu
from Piloton.UI.Forms.DeviceSettings import DeviceSettings as DeviceSettingsForm


class DeviceSettings(Menu):

    __menuname__ = "Device Settings"

    def __init__(self):
        options = {
            "Update Bike Name": DeviceSettingsForm.update_bike_name,
            "Update HRM Name": DeviceSettingsForm.update_hrm_name,
            "Back": MainMenu.MainMenu,
        }
        super().__init__(options)
