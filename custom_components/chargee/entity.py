"""Base entity for the Chargee P1 integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
    format_mac,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import ChargeeDataUpdateCoordinator


class ChargeeEntity(CoordinatorEntity[ChargeeDataUpdateCoordinator]):
    """Base class providing shared device info for all Chargee entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ChargeeDataUpdateCoordinator) -> None:
        """Initialize the entity and build the device registry entry."""
        super().__init__(coordinator)
        device = coordinator.data.device
        serial = device.serial or coordinator.config_entry.unique_id or ""

        # The serial number is also the device MAC address (12 hex chars).
        connections = (
            {(CONNECTION_NETWORK_MAC, format_mac(serial))} if serial else set()
        )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=MANUFACTURER,
            model=device.product_type,
            name=device.product_name or "Chargee P1",
            serial_number=serial or None,
            sw_version=device.firmware_version,
            connections=connections,
        )
