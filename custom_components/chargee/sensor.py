"""Sensor platform for the Chargee P1 integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .api import ChargeeMeasurement
from .coordinator import ChargeeConfigEntry, ChargeeDataUpdateCoordinator
from .entity import ChargeeEntity


def _parse_gas_timestamp(value: int | None) -> datetime | None:
    """Parse a ``YYMMDDhhmmss`` integer into a timezone-aware datetime."""
    if value is None:
        return None
    try:
        naive = datetime.strptime(str(value), "%y%m%d%H%M%S")
    except (ValueError, TypeError):
        return None
    return naive.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)


@dataclass(frozen=True, kw_only=True)
class ChargeeSensorEntityDescription(SensorEntityDescription):
    """Describe a Chargee sensor."""

    value_fn: Callable[[ChargeeMeasurement], StateType | datetime]


SENSORS: tuple[ChargeeSensorEntityDescription, ...] = (
    # --- Energy: grid import (maps to HA Energy dashboard consumption) ---
    ChargeeSensorEntityDescription(
        key="total_power_import_kwh",
        translation_key="total_power_import_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda m: m.total_power_import_kwh,
    ),
    ChargeeSensorEntityDescription(
        key="total_power_import_t1_kwh",
        translation_key="total_power_import_t1_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.total_power_import_t1_kwh,
    ),
    ChargeeSensorEntityDescription(
        key="total_power_import_t2_kwh",
        translation_key="total_power_import_t2_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.total_power_import_t2_kwh,
    ),
    # --- Energy: grid export (maps to HA Energy dashboard return) ---
    ChargeeSensorEntityDescription(
        key="total_power_export_kwh",
        translation_key="total_power_export_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda m: m.total_power_export_kwh,
    ),
    ChargeeSensorEntityDescription(
        key="total_power_export_t1_kwh",
        translation_key="total_power_export_t1_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.total_power_export_t1_kwh,
    ),
    ChargeeSensorEntityDescription(
        key="total_power_export_t2_kwh",
        translation_key="total_power_export_t2_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.total_power_export_t2_kwh,
    ),
    # --- Active power ---
    ChargeeSensorEntityDescription(
        key="active_power_w",
        translation_key="active_power_w",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda m: m.active_power_w,
    ),
    ChargeeSensorEntityDescription(
        key="active_power_l1_w",
        translation_key="active_power_l1_w",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda m: m.active_power_l1_w,
    ),
    ChargeeSensorEntityDescription(
        key="active_power_l2_w",
        translation_key="active_power_l2_w",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda m: m.active_power_l2_w,
    ),
    ChargeeSensorEntityDescription(
        key="active_power_l3_w",
        translation_key="active_power_l3_w",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda m: m.active_power_l3_w,
    ),
    # --- Voltage ---
    ChargeeSensorEntityDescription(
        key="active_voltage_l1_v",
        translation_key="active_voltage_l1_v",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.active_voltage_l1_v,
    ),
    ChargeeSensorEntityDescription(
        key="active_voltage_l2_v",
        translation_key="active_voltage_l2_v",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.active_voltage_l2_v,
    ),
    ChargeeSensorEntityDescription(
        key="active_voltage_l3_v",
        translation_key="active_voltage_l3_v",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.active_voltage_l3_v,
    ),
    # --- Current ---
    ChargeeSensorEntityDescription(
        key="active_current_a",
        translation_key="active_current_a",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda m: m.active_current_a,
    ),
    ChargeeSensorEntityDescription(
        key="active_current_l1_a",
        translation_key="active_current_l1_a",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.active_current_l1_a,
    ),
    ChargeeSensorEntityDescription(
        key="active_current_l2_a",
        translation_key="active_current_l2_a",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.active_current_l2_a,
    ),
    ChargeeSensorEntityDescription(
        key="active_current_l3_a",
        translation_key="active_current_l3_a",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.active_current_l3_a,
    ),
    # --- Gas (maps to HA Energy dashboard gas) ---
    ChargeeSensorEntityDescription(
        key="total_gas_m3",
        translation_key="total_gas_m3",
        device_class=SensorDeviceClass.GAS,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda m: m.total_gas_m3,
    ),
    ChargeeSensorEntityDescription(
        key="gas_timestamp",
        translation_key="gas_timestamp",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda m: _parse_gas_timestamp(m.gas_timestamp),
    ),
    # --- Diagnostics ---
    ChargeeSensorEntityDescription(
        key="active_tariff",
        translation_key="active_tariff",
        device_class=SensorDeviceClass.ENUM,
        options=["1", "2"],
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda m: str(m.active_tariff) if m.active_tariff is not None else None,
    ),
    ChargeeSensorEntityDescription(
        key="wifi_strength",
        translation_key="wifi_strength",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.wifi_strength,
    ),
    ChargeeSensorEntityDescription(
        key="wifi_ssid",
        translation_key="wifi_ssid",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.wifi_ssid,
    ),
    ChargeeSensorEntityDescription(
        key="meter_model",
        translation_key="meter_model",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.meter_model,
    ),
    ChargeeSensorEntityDescription(
        key="smr_version",
        translation_key="smr_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda m: m.smr_version,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ChargeeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chargee sensors based on the data the device reports."""
    coordinator = entry.runtime_data
    measurement = coordinator.data.measurement

    async_add_entities(
        ChargeeSensor(coordinator, description)
        for description in SENSORS
        if description.value_fn(measurement) is not None
    )


class ChargeeSensor(ChargeeEntity, SensorEntity):
    """A single sensor backed by a measurement field."""

    entity_description: ChargeeSensorEntityDescription

    def __init__(
        self,
        coordinator: ChargeeDataUpdateCoordinator,
        description: ChargeeSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        serial = coordinator.data.device.serial or coordinator.config_entry.unique_id
        self._attr_unique_id = f"{serial}_{description.key}"

    @property
    def native_value(self) -> StateType | datetime:
        """Return the current value for this sensor."""
        return self.entity_description.value_fn(self.coordinator.data.measurement)
