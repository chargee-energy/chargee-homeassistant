"""Fixtures for the Chargee P1 tests."""

from __future__ import annotations

from collections.abc import Generator
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from homeassistant.const import CONF_HOST, CONF_PORT

from custom_components.chargee.api import ChargeeDevice, ChargeeMeasurement
from custom_components.chargee.const import DOMAIN

from pytest_homeassistant_custom_component.common import MockConfigEntry

pytest_plugins = "pytest_homeassistant_custom_component"


def _load_fixture(name: str) -> dict:
    """Load a JSON fixture from the fixtures directory."""
    path = Path(__file__).parent / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of the custom component in every test."""
    yield


@pytest.fixture(autouse=True)
def _threaded_resolver():
    """Avoid the eager pycares resolver thread.

    Home Assistant's client session uses ``AsyncResolver`` (aiodns/pycares),
    which spawns a daemon thread as soon as the connector is created. That
    thread is flagged by the test harness as a leak. Requests in the test suite
    are always mocked, so a ``ThreadedResolver`` (which spawns nothing until
    actually used) is a safe drop-in.
    """
    with patch(
        "homeassistant.helpers.aiohttp_client.AsyncResolver",
        aiohttp.ThreadedResolver,
    ):
        yield


@pytest.fixture
def device_data() -> dict:
    """Return the sample /api response."""
    return _load_fixture("device.json")


@pytest.fixture
def measurement_data() -> dict:
    """Return the sample /api/v1/data response."""
    return _load_fixture("data.json")


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry for the integration."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="sparky",
        unique_id="6055F9C6C89C",
        data={
            CONF_HOST: "192.168.0.204",
            CONF_PORT: 80,
            "serial": "6055F9C6C89C",
            "product_name": "sparky",
            "product_type": "sparky-v3.2",
        },
    )


@pytest.fixture
def mock_client(
    device_data: dict, measurement_data: dict
) -> Generator[AsyncMock, None, None]:
    """Patch the API client used by the integration."""
    with patch(
        "custom_components.chargee.ChargeeLocalApiClient", autospec=True
    ) as client_class:
        client = client_class.return_value
        client.get_device = AsyncMock(
            return_value=ChargeeDevice.from_dict(device_data)
        )
        client.get_measurement = AsyncMock(
            return_value=ChargeeMeasurement.from_dict(measurement_data)
        )
        client.identify = AsyncMock(return_value=True)
        yield client
