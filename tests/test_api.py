"""Tests for the bundled Chargee API client."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import aiohttp
from aioresponses import aioresponses
import pytest

from custom_components.chargee.api import (
    ChargeeConnectionError,
    ChargeeLocalApiClient,
    ChargeeResponseError,
)

HOST = "192.168.0.204"
# yarl normalizes away the default HTTP port, so requests go to http://host/...
BASE = f"http://{HOST}"


@pytest.fixture
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """A client session using a threaded resolver.

    The default ``AsyncResolver`` eagerly spawns a pycares thread which the
    Home Assistant test harness flags as a lingering thread. ``aioresponses``
    intercepts requests before any DNS lookup, so a threaded resolver is safe.
    """
    connector = aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver())
    async with aiohttp.ClientSession(connector=connector) as client_session:
        yield client_session


def _client(session: aiohttp.ClientSession) -> ChargeeLocalApiClient:
    """Build a client bound to the test session."""
    return ChargeeLocalApiClient(HOST, session)


async def test_get_device(
    session: aiohttp.ClientSession, device_data: dict
) -> None:
    """It parses the /api response into a ChargeeDevice."""
    client = _client(session)
    with aioresponses() as mocked:
        mocked.get(f"{BASE}/api", payload=device_data)
        device = await client.get_device()

    assert device.serial == "6055F9C6C89C"
    assert device.product_type == "sparky-v3.2"
    assert device.api_version == "v1"


async def test_get_measurement(
    session: aiohttp.ClientSession, measurement_data: dict
) -> None:
    """It parses the /api/v1/data response into a ChargeeMeasurement."""
    client = _client(session)
    with aioresponses() as mocked:
        mocked.get(f"{BASE}/api/v1/data", payload=measurement_data)
        measurement = await client.get_measurement()

    assert measurement.active_power_w == 8742
    assert measurement.total_power_import_kwh == 40571.711
    assert measurement.total_gas_m3 == 13891.3
    assert measurement.gas_timestamp == 260315094500


async def test_partial_measurement_handles_missing_fields(
    session: aiohttp.ClientSession,
) -> None:
    """Missing/optional fields stay None (single-phase Flint style payload)."""
    client = _client(session)
    with aioresponses() as mocked:
        mocked.get(
            f"{BASE}/api/v1/data",
            payload={"active_power_w": 120, "total_power_import_kwh": 1.5},
        )
        measurement = await client.get_measurement()

    assert measurement.active_power_w == 120
    assert measurement.active_power_l3_w is None
    assert measurement.total_gas_m3 is None


async def test_identify(session: aiohttp.ClientSession) -> None:
    """Identify returns True when the device acknowledges."""
    client = _client(session)
    with aioresponses() as mocked:
        mocked.get(f"{BASE}/api/v1/identify", payload={"identify": "ok"})
        assert await client.identify() is True


async def test_telegram_returns_text(session: aiohttp.ClientSession) -> None:
    """The telegram endpoint returns raw text."""
    client = _client(session)
    with aioresponses() as mocked:
        mocked.get(f"{BASE}/api/v1/telegram", body="/ISK5\\2M550T-1011\n!1F28")
        telegram = await client.get_telegram()

    assert telegram.startswith("/ISK5")


async def test_http_error_raises_response_error(
    session: aiohttp.ClientSession,
) -> None:
    """Non-200 responses raise a response error."""
    client = _client(session)
    with aioresponses() as mocked:
        mocked.get(f"{BASE}/api", status=500)
        with pytest.raises(ChargeeResponseError):
            await client.get_device()


async def test_connection_error_raises(session: aiohttp.ClientSession) -> None:
    """Connection failures raise a connection error."""
    client = _client(session)
    with aioresponses() as mocked:
        mocked.get(f"{BASE}/api", exception=aiohttp.ClientError("boom"))
        with pytest.raises(ChargeeConnectionError):
            await client.get_device()
