"""Tests for the Chargee P1 config flow."""

from __future__ import annotations

from ipaddress import ip_address
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.config_entries import SOURCE_USER, SOURCE_ZEROCONF
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

try:
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
except ImportError:  # pragma: no cover - fallback for HA < 2025.2
    from homeassistant.components.zeroconf import ZeroconfServiceInfo

from custom_components.chargee.api import ChargeeConnectionError, ChargeeDevice
from custom_components.chargee.const import DOMAIN

from pytest_homeassistant_custom_component.common import MockConfigEntry


def _zeroconf_info() -> ZeroconfServiceInfo:
    return ZeroconfServiceInfo(
        ip_address=ip_address("192.168.0.204"),
        ip_addresses=[ip_address("192.168.0.204")],
        port=80,
        hostname="sparky-6055F9C6C89C.local.",
        type="_chargee_p1._tcp.local.",
        name="sparky-6055F9C6C89C._chargee_p1._tcp.local.",
        properties={
            "sn": "6055F9C6C89C",
            "fw": "98",
            "hwid": "3.2",
            "device": "sparky",
        },
    )


@pytest.fixture
def mock_flow_client(device_data: dict):
    """Patch the client used inside the config flow."""
    with patch(
        "custom_components.chargee.config_flow.ChargeeLocalApiClient", autospec=True
    ) as client_class:
        client = client_class.return_value
        client.get_device = AsyncMock(
            return_value=ChargeeDevice.from_dict(device_data)
        )
        yield client


@pytest.fixture
def mock_setup_entry():
    """Prevent the entry from being fully set up (no real network call)."""
    with patch(
        "custom_components.chargee.async_setup_entry", return_value=True
    ) as setup:
        yield setup


async def test_user_flow(
    hass: HomeAssistant,
    mock_flow_client: AsyncMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """A user can set up the device manually."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.0.204"}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "sparky"
    assert result["data"][CONF_HOST] == "192.168.0.204"
    assert result["result"].unique_id == "6055F9C6C89C"


async def test_user_flow_cannot_connect(hass: HomeAssistant) -> None:
    """A connection failure shows an error."""
    with patch(
        "custom_components.chargee.config_flow.ChargeeLocalApiClient", autospec=True
    ) as client_class:
        client_class.return_value.get_device = AsyncMock(
            side_effect=ChargeeConnectionError("boom")
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "1.2.3.4"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_duplicate_aborts(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_flow_client: AsyncMock,
) -> None:
    """Setting up an already-configured serial aborts."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.0.204"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_zeroconf_flow(
    hass: HomeAssistant,
    mock_flow_client: AsyncMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """A discovered device leads to a confirmation step and entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_ZEROCONF}, data=_zeroconf_info()
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "6055F9C6C89C"
