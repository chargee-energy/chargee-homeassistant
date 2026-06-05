"""Constants for the Chargee P1 integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final = "chargee"

LOGGER: Final = logging.getLogger(__package__)

MANUFACTURER: Final = "Chargee"

# Polling interval for the local API. The dongle updates roughly once per
# second, but the smart meter telegram cadence is what limits useful resolution.
DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=5)

# Network timeout for a single request to the dongle.
DEFAULT_TIMEOUT: Final = 10

# Default HTTP port exposed by the local API (see documentation).
DEFAULT_PORT: Final = 80

# Config entry data keys.
CONF_SERIAL: Final = "serial"
CONF_PRODUCT_NAME: Final = "product_name"
CONF_PRODUCT_TYPE: Final = "product_type"

# mDNS TXT record keys broadcast by Sparky and Flint.
ZEROCONF_SERIAL: Final = "sn"
ZEROCONF_FIRMWARE: Final = "fw"
ZEROCONF_HARDWARE: Final = "hwid"
ZEROCONF_DEVICE: Final = "device"
