"""Tests for the Chargee P1 sensors."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_energy_sensors(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_client: AsyncMock
) -> None:
    """Energy and power sensors expose the documented sample values."""
    await _setup(hass, mock_config_entry)

    state = hass.states.get("sensor.sparky_energy_import")
    assert state is not None
    assert state.state == "40571.711"
    assert state.attributes["state_class"] == "total_increasing"
    assert state.attributes["device_class"] == "energy"

    power = hass.states.get("sensor.sparky_active_power")
    assert power is not None
    assert power.state == "8742"


async def test_gas_sensor(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_client: AsyncMock
) -> None:
    """The gas sensor is created for a meter that reports gas."""
    await _setup(hass, mock_config_entry)

    gas = hass.states.get("sensor.sparky_gas")
    assert gas is not None
    assert gas.state == "13891.3"
    assert gas.attributes["device_class"] == "gas"


async def test_missing_fields_skip_entities(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_client: AsyncMock
) -> None:
    """No entity is created for a field that is absent (e.g. single-phase)."""
    from custom_components.chargee.api import ChargeeMeasurement

    mock_client.get_measurement.return_value = ChargeeMeasurement.from_dict(
        {"active_power_w": 100, "total_power_import_kwh": 5.0}
    )
    await _setup(hass, mock_config_entry)

    assert hass.states.get("sensor.sparky_active_power") is not None
    assert hass.states.get("sensor.sparky_gas") is None
    assert hass.states.get("sensor.sparky_active_power_phase_3") is None
