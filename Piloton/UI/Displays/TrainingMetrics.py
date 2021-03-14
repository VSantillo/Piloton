from __future__ import annotations
import asyncio
from typing import List, Tuple

from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from Piloton.Types import Display, LoopStatus


class TrainingMetrics(Display):
    def __init__(self, piloton, resistance: int):
        """
        Initialize Training Metrics display

        :param Piloton piloton: Piloton object to pass data through
        :param int resistance: Bike resistance to set for testing
        """
        self.piloton = piloton
        self.piloton.bike.resistance = resistance

    def _generate_cadence_readout(self, cadence) -> List[Tuple[str, str]]:
        """
        Generate a readout based on how many samples a given cadence has at the current training resistance

        :param cadence:
        :return: Read out of the current cadence's readout
        """
        text = []

        # Look up number of data points for given resistance and cadence
        number_data_points: int = len(self.piloton.training_data[self.piloton.bike.resistance][cadence])

        # Create readout based on sample size
        if number_data_points > 15:
            text.extend([("█", "green"), ("█", "yellow"), ("█", "red")])
        elif number_data_points > 5:
            text.extend([("█", "green"), ("█ ", "yellow")])
        elif number_data_points > 1:
            text.append(("█  ", "green"))
        else:
            text.append(("   ", "white"))
        text.append((" ", "white"))

        return text

    def _generate_grid(self) -> List[Tuple[str, str]]:
        """
        Generate the grid of cadence readouts

        :return: Grid of cadence readouts
        """
        text = []

        for cadence_bucket in range(120, 10, -10):
            text.append((f"\n  {cadence_bucket:3d}    ", "white"))
            for cadence in range(cadence_bucket, cadence_bucket + 10):
                text.extend(self._generate_cadence_readout(cadence))

        return text

    def _generate_training_panel(self) -> Panel:
        """
        Generate the Training panel for this display

        :return: Display of training data
        """
        text = Text.assemble(
            ("  Cad.    0   1   2   3   4   5   6   7   8   9    ", "white"),
            *self._generate_grid(),
            (f"\n  Resistance: {self.piloton.bike.resistance}  -  Cadence: {self.piloton.bike.cadence} RPM", "white"),
        )
        panel = Panel(text, title="Training", box=box.HEAVY, border_style="#85AAD5")
        return panel

    def generate_layout(self) -> Layout:
        """
        Generate layout on refresh

        :return: Piloton training layout
        """
        # Split layout
        layout = Layout()
        layout.split(Layout(name="main", size=15))

        # Add main panel
        layout["main"].split(
            Layout(self._generate_training_panel(), name="training"),
        )

        return layout

    async def live_output(self):
        """
        Live Training Metrics Output Loop. Will continue until signal interrupt.
        """
        # Get function name
        func_name = "_training_live_output"

        # Set status to active
        self.piloton.loop_tracker[func_name] = LoopStatus.ACTIVE

        # Block until device threads connect
        for loop, status in self.piloton.loop_tracker.items():
            while status == LoopStatus.CONNECTING:
                await asyncio.sleep(1)

        # Raise notification and link it to the handler
        with Live(self.generate_layout(), refresh_per_second=4) as live:
            while self.piloton.loop_tracker[func_name] == LoopStatus.ACTIVE:
                live.update(self.generate_layout())
                await asyncio.sleep(0.4)
