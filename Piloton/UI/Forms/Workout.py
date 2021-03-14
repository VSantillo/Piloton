from typing import List, Tuple, Union
from rich.prompt import IntPrompt
from Piloton.Types import Form, FormPrompt
from Piloton.UI.Menus import MainMenu


class Workout(Form):

    __formname__ = "Workout"

    @staticmethod
    def start_workout() -> List[FormPrompt]:
        return [
            FormPrompt(
                IntPrompt,
                Workout._start_workout,
                "Enter Length of Workout in Minutes (0: Forever, -1: Main Menu)",
            )
        ]

    @staticmethod
    def _start_workout(response):
        # Return if user signaled quitting
        if response == -1:
            return

        return "workout", response
