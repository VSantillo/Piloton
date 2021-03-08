from __future__ import annotations
from typing import TYPE_CHECKING, List

from rich.console import Console
from rich.prompt import IntPrompt

from Piloton.Types.Menu import Menu
from Piloton.Types.Form import FormPrompt

# Only import when type_checking
if TYPE_CHECKING:
    from Piloton import Piloton

    _Base = Piloton
else:
    _Base = object


class RichMixin(_Base):  # type: ignore
    def __init__(self):
        self._console = Console()

        super().__init__()

    def render_menu(self, menu: Menu) -> int:
        """
        Render Menu

        :param menu: Menu (See Types/Menu.py)
        :return: User's selection from menu
        :rtype: int
        """
        self._console.print(f"{'='*40}")
        self._console.print(f"{menu.__menuname__}")

        # Print out all of the options in the menu
        options: List[str] = []
        for index, option in enumerate(menu.options.keys()):
            # We don't want to zero-index our menus
            index += 1

            # Add option index
            options.append(str(index))

            # Prettify name
            self._console.print(f"    ({index})> {option}")

        # Print out a 40 char bar just as a visual index
        self._console.print(f"\n{'-'*40}")

        # Prompt for input
        selection: int = IntPrompt.ask("Selection", choices=options)

        return selection

    def render_form(self, form: List[FormPrompt]):
        """
        Render Form

        :param form: List of form prompts
        :return:
        """
        for prompt in form:
            response = prompt.run(console=self._console)
            return prompt.handle_response(response)
