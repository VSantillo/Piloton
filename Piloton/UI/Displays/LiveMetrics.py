from __future__ import annotations

import asyncio
from math import inf
from typing import Tuple, List, Optional, Union

from Piloton.Types import Display, HeartZone, PowerZone, LoopStatus


from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class LiveMetrics(Display):
    def __init__(self, piloton):
        self.piloton = piloton

    def _generate_cadence_panel(self) -> Panel:
        text = Text(f"\n{round(self.piloton.bike.cadence)}\n", justify="center")
        text.stylize("bold white")
        panel = Panel(text, title="Cadence (RPM)", box=box.HEAVY, border_style="#BF211E")
        return panel

    def _generate_resistance_panel(self) -> Panel:
        text = Text(f"\n{self.piloton.bike.resistance}\n", justify="center")
        text.stylize("bold white")
        panel = Panel(text, title="Resistance", box=box.HEAVY, border_style="#E9CE2C")
        return panel

    def _generate_power_panel(self) -> Panel:
        text = Text(f"\n{round(self.piloton.bike.power)}\n", justify="center")
        text.stylize("bold white")
        panel = Panel(text, title="Power (W)", box=box.HEAVY, border_style="#E89005")
        return panel

    def _generate_heart_zone_header(self, heart_zone: HeartZone) -> Tuple[str, str]:
        return f"{heart_zone}\n", f"bold {self.piloton.heart_zones.COLORS[heart_zone]}"

    def _generate_heart_zone_progress_bar(self, current_zone: HeartZone) -> List[Tuple[str, str]]:
        bar = [(f"«««", "bold white")]

        # Build up the bar, rendering the color based on if the current zone exceeds it
        for zone, zone_color in self.piloton.heart_zones.COLORS.items():
            if current_zone.value >= zone.value:
                bar.append(("███", zone_color))
            else:
                bar.append(("  ", "white"))

        bar.append(("»»»\n", "bold white"))

        return bar

    def _generate_heart_rate_panel(self) -> Panel:
        text = Text.assemble(
            self._generate_heart_zone_header(self.piloton.heart_zone),
            *self._generate_heart_zone_progress_bar(self.piloton.heart_zone),
            (f"{self.piloton.hrm.heart_rate}", "bold white"),
            justify="center",
        )

        current_color: str = self.piloton.heart_zones.COLORS[self.piloton.heart_zone]
        panel = Panel(text, title="Heart Rate (BPM)", box=box.HEAVY, border_style=current_color)
        return panel

    def _generate_power_zone_header(self, zone_number: int, zone: PowerZone, ftp_percent: float):
        return (
            (f"{zone_number} - ", "white"),
            (f"{zone}", f"bold {self.piloton.power_zones.COLORS[zone]}"),
            (f" - {round(ftp_percent)}%\n", "white"),
        )

    def _generate_power_zone_bar(self, current_zone: PowerZone):
        bar = [("«««", "bold white")]

        # Build up the bar, rendering the color based on if the current zone exceeds it
        for zone, zone_color in self.piloton.power_zones.COLORS.items():
            if current_zone.value >= zone.value:
                bar.append(("███", zone_color))
            else:
                bar.append(("  ", "white"))

        bar.append(("»»»\n", "bold white"))

        return bar

    def _generate_power_zone_footer(self, low_limit, low_color, cur_power, cur_color, up_limit, up_color):
        return (
            (f"{low_limit}", low_color),
            (" - ", "white"),
            (f"{round(cur_power)}", cur_color),
            (" - ", "white"),
            (f"{up_limit}", up_color),
        )

    def _generate_power_zone_panel(self) -> Panel:
        # Calculate FTP percent
        ftp: int = self.piloton.power_zones.ftp
        ftp_percent: float = self.piloton.bike.power / ftp * 100

        # Set up lower and upper limits
        lower_zone: PowerZone = PowerZone(0)
        upper_zone: PowerZone = PowerZone(1)

        if self.piloton.power_zone != PowerZone.NO_ZONE:
            lower_zone = PowerZone(self.piloton.power_zone.value - 1)
            upper_zone = PowerZone(self.piloton.power_zone.value)

        # Get upper and lower limits
        lower_limit: Optional[int] = 0
        upper_limit: Optional[Union[int, float]]
        if self.piloton.power_zone in [PowerZone.NO_ZONE, PowerZone.ACTIVE_RECOVERY]:
            upper_limit = round(ftp * self.piloton.power_zones.ZONES[upper_zone])
        elif self.piloton.power_zone == PowerZone.NEUROMUSCULAR_POWER:
            lower_limit = round(ftp * self.piloton.power_zones.ZONES[lower_zone])
            upper_limit = inf
        else:
            lower_limit = round(ftp * self.piloton.power_zones.ZONES[lower_zone])
            upper_limit = round(ftp * self.piloton.power_zones.ZONES[upper_zone])

        # Set colors
        lower_color: str = self.piloton.power_zones.COLORS[lower_zone]
        current_color: str = self.piloton.power_zones.COLORS[upper_zone]
        next_color: str = current_color
        if upper_zone != PowerZone.NEUROMUSCULAR_POWER:
            next_color = self.piloton.power_zones.COLORS[PowerZone(self.piloton.power_zone.value + 1)]

        # Set text output
        text = Text.assemble(
            *self._generate_power_zone_header(self.piloton.power_zone.value, self.piloton.power_zone, ftp_percent),
            *self._generate_power_zone_bar(self.piloton.power_zone),
            *self._generate_power_zone_footer(
                lower_limit,
                lower_color,
                self.piloton.bike.power,
                current_color,
                upper_limit,
                next_color,
            ),
            justify="center",
        )
        panel = Panel(text, title="Power Zone", box=box.HEAVY, border_style=current_color)
        return panel

    def generate_layout(self) -> Layout:
        """
        Generate layout on refresh

        :return: Piloton Layout
        """
        # Split layout
        layout = Layout()
        layout.split(
            Layout(name="upper", size=5),
            Layout(name="hz", size=5),
            Layout(name="pz", size=5),
        )

        # Add upper panels
        layout["upper"].split(
            Layout(self._generate_cadence_panel(), name="cadence"),
            Layout(self._generate_resistance_panel(), name="resistance"),
            Layout(self._generate_power_panel(), name="power"),
            direction="horizontal",
        )

        # Add lower panels
        layout["hz"].split(
            Layout(self._generate_heart_rate_panel(), name="heart_rate"),
            direction="horizontal",
        )

        layout["pz"].split(
            Layout(self._generate_power_zone_panel(), name="power_zone"),
            direction="horizontal",
        )

        return layout

    async def live_output(self):
        # Get function name
        func_name = "__live_output"

        # Set status to active
        if func_name not in self.piloton.loop_tracker:
            self.piloton.loop_tracker[func_name] = LoopStatus.ACTIVE

        # Raise notification and link it to the handler
        with Live(self.generate_layout(), refresh_per_second=4, screen=True) as live:
            while self.piloton.loop_tracker[func_name] == LoopStatus.ACTIVE:
                live.update(self.generate_layout())
                await asyncio.sleep(0.4)
