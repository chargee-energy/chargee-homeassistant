"""The Chargee P1 integration."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ChargeeLocalApiClient
from .const import DEFAULT_PORT, DEFAULT_TIMEOUT
from .coordinator import ChargeeConfigEntry, ChargeeDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: ChargeeConfigEntry
) -> bool:
    """Set up Chargee P1 from a config entry."""
    session = async_get_clientsession(hass)
    client = ChargeeLocalApiClient(
        host=entry.data[CONF_HOST],
        session=session,
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        timeout=DEFAULT_TIMEOUT,
    )

    coordinator = ChargeeDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ChargeeConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
