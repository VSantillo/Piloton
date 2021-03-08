from Piloton.Types import Menu
from Piloton.UI.Menus import MainMenu
from Piloton.UI.Forms import UserSettings as UserSettingsForm


class UserSettings(Menu):

    __menuname__ = "User Settings"

    def __init__(self):
        options = {
            "Update Name": UserSettingsForm.update_name,
            "Update Age": UserSettingsForm.update_age,
            "Update FTP": UserSettingsForm.update_ftp,
            "Back": MainMenu.MainMenu,
        }
        super().__init__(options)
