from __future__ import annotations


class Menu:

    __menuname__: str = "Menu"

    def __init__(self, options):
        """
        Initialize a Menu

        :param options: Menu options
        """
        self.options = options

    def handle_selection(self, selection):
        """
        Handle selection by reading the value from the given keys and returning the apporopriate resposne

        :param selection: User selection
        :return:
        """
        option = list(self.options.keys())[selection - 1]
        if option == "Quit":
            return

        return self.options[option]
