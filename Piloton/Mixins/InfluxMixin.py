from __future__ import annotations

from influxdb import InfluxDBClient
from typing import Tuple, TYPE_CHECKING

# Only import when type_checking
if TYPE_CHECKING:
    from Piloton import Piloton

    _Base = Piloton
else:
    _Base = object

# These are required to connect to Influx
_MEMBER_REQUIREMENTS: Tuple[str, ...] = (
    "influx_host",
    "influx_port",
    "influx_username",
    "influx_password",
    "influx_database",
)


class InfluxMixin(_Base):  # type: ignore
    def __init__(self):
        """
        Set up Influx Client

        :return:
        """
        # Warn if any fields are missing from Base
        if any(not hasattr(self, requirement) for requirement in _MEMBER_REQUIREMENTS):
            self.logger.warning("Missing required field. Unable to setup InfluxDB Client.")
            return

        # Set up InfluxDB client
        self.influx_client: InfluxDBClient = InfluxDBClient(
            host=self.influx_host,
            port=self.influx_port,
            username=self.influx_username,
            password=self.influx_password,
            database=self.influx_database,
        )
        self.logger.debug("Successfully set up InfluxDB Client")
