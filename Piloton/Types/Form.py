from typing import Any, Tuple, Dict, Callable
from rich.prompt import PromptType


class FormPrompt:
    """
    Helper class to easily store Prompts for Forms
    """

    def __init__(self, prompt, handler, *args, **kwargs):
        """
        Set up a data structure to represent Prompt information such that they
        can be easily stored and called upon when rendering

        :param PromptType prompt: Type of Prompt to use
        :param Callable handler: Function to handle response
        :param args: Arguments for Prompt
        :param kwargs: Kwargs for Prompt
        """
        self.prompt: PromptType = prompt
        self.handler: Callable = handler
        self.args: Tuple[Any] = args
        self.kwargs: Dict[Any] = kwargs

    def run(self, console=None):
        """
        Return prompt to console

        :param console: Active rich console
        :return: Prompt being asked
        """
        return self.prompt.ask(*self.args, console=console, **self.kwargs)

    def handle_response(self, response):
        """
        Handle form response

        :param Any response: Call the handler with the response
        :return: Response from handler
        """
        return self.handler(response)


class Form:
    __formname__ = "Form"
