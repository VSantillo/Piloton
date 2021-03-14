from rich.prompt import IntPrompt
from Piloton.Types import Form, FormPrompt


class Training(Form):

    __formname__ = "Training"

    @staticmethod
    def start_training():
        return [
            FormPrompt(
                IntPrompt,
                Training._start_training,
                "Enter Resistance (-1: Main Menu)",
            )
        ]

    @staticmethod
    def _start_training(response):
        # Return if user signaled quitting
        if response == -1:
            return

        return "training", response
