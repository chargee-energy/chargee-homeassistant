"""Button platform for the Chargee P1 integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ChargeeError
from .coordinator import ChargeeConfigEntry, ChargeeDataUpdateCoordinator
from .entity import ChargeeEntity

IDENTIFY_BUTTON = ButtonEntityDescription(
    key="identify",
    translation_key="identify",
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ChargeeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the identify button."""
    async_add_entities([ChargeeIdentifyButton(entry.runtime_data)])


class ChargeeIdentifyButton(ChargeeEntity, ButtonEntity):
    """Button that makes the device blink its status light."""

    entity_description: ButtonEntityDescription

    def __init__(self, coordinator: ChargeeDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = IDENTIFY_BUTTON
        serial = coordinator.data.device.serial or coordinator.config_entry.unique_id
        self._attr_unique_id = f"{serial}_{IDENTIFY_BUTTON.key}"

    async def async_press(self) -> None:
        """Trigger the identify action on the device."""
        try:
            await self.coordinator.client.identify()
        except ChargeeError as err:
            raise HomeAssistantError(f"Failed to identify Chargee device: {err}") from err
