import json
from rich.prompt import Prompt, IntPrompt


from Piloton.Types import Form, FormPrompt


class UserSettings(Form):

    __formname__ = "User Settings"

    @staticmethod
    def update_name():
        return [FormPrompt(Prompt, UserSettings._update_name, "Update User Name")]

    @staticmethod
    def _update_name(response):
        # Open JSON
        with open("data/users.json", "r") as fh:
            # Load JSON
            data = json.load(fh)

        # Set Name
        data["name"] = response

        with open("data/users.json", "w") as fh:
            # Write
            json.dump(data, fh, indent=4)

    @staticmethod
    def update_age():
        return [FormPrompt(IntPrompt, UserSettings._update_age, "Update Age")]

    @staticmethod
    def _update_age(response):
        # Open JSON
        with open("data/users.json", "r") as fh:
            # Load JSON
            data = json.load(fh)

        # Set age
        data["age"] = response

        with open("data/users.json", "w") as fh:
            # Write
            json.dump(data, fh, indent=4)

    @staticmethod
    def update_ftp():
        return [FormPrompt(IntPrompt, UserSettings._update_ftp, "Update FTP")]

    @staticmethod
    def _update_ftp(response):
        # Open JSON
        with open("data/users.json", "r") as fh:
            # Load JSON
            data = json.load(fh)

        # Set ftp
        data["ftp"] = response

        with open("data/users.json", "w") as fh:
            # Write
            json.dump(data, fh, indent=4)
