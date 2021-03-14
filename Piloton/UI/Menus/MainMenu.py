from Piloton.Types.Menu import Menu
from Piloton.UI.Menus import DeviceSettings
from Piloton.UI.Menus import UserSettings
from Piloton.UI.Forms import Workout, Training


class MainMenu(Menu):

    __menuname__ = "Main Menu"

    def __init__(self):
        options = {
            "Workout": Workout.start_workout,
            "User Settings": UserSettings.UserSettings,
            "Device Settings": DeviceSettings.DeviceSettings,
            "Training": Training.start_training,
            "Quit": None,
        }
        super().__init__(options)
