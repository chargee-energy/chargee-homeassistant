"""Data update coordinator for the Chargee P1 integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ChargeeConnectionError,
    ChargeeDevice,
    ChargeeError,
    ChargeeLocalApiClient,
    ChargeeMeasurement,
)
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER

type ChargeeConfigEntry = ConfigEntry[ChargeeDataUpdateCoordinator]


@dataclass(slots=True)
class ChargeeData:
    """Bundle of the latest device info and measurement."""

    device: ChargeeDevice
    measurement: ChargeeMeasurement


class ChargeeDataUpdateCoordinator(DataUpdateCoordinator[ChargeeData]):
    """Poll a Chargee dongle and share the result with all entities."""

    config_entry: ChargeeConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ChargeeConfigEntry,
        client: ChargeeLocalApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client
        # Cached device info; refreshed lazily so static metadata survives
        # transient measurement read failures.
        self._device: ChargeeDevice | None = None

    async def _async_update_data(self) -> ChargeeData:
        """Fetch the latest device info and measurement."""
        try:
            if self._device is None:
                self._device = await self.client.get_device()
            measurement = await self.client.get_measurement()
        except ChargeeConnectionError as err:
            raise UpdateFailed(f"Could not connect to Chargee device: {err}") from err
        except ChargeeError as err:
            raise UpdateFailed(f"Error talking to Chargee device: {err}") from err

        return ChargeeData(device=self._device, measurement=measurement)
