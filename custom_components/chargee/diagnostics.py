"""Diagnostics support for the Chargee P1 integration."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import CONF_SERIAL
from .coordinator import ChargeeConfigEntry

TO_REDACT = {
    CONF_HOST,
    CONF_SERIAL,
    "serial",
    "unique_id",
    "unique_gas_id",
    "wifi_ssid",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ChargeeConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    data = coordinator.data

    return {
        "entry": async_redact_data(entry.data, TO_REDACT),
        "device": async_redact_data(asdict(data.device), TO_REDACT),
        "measurement": async_redact_data(asdict(data.measurement), TO_REDACT),
    }
