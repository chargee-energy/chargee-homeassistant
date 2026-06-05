"""Async client for the Chargee Local API v1.

The client wraps the HTTP endpoints documented for the Chargee P1 dongle
(Sparky and Flint). It is intentionally small and free of Home Assistant
dependencies so it can be reused and unit-tested in isolation.
"""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
from yarl import URL

from .errors import ChargeeConnectionError, ChargeeResponseError
from .models import ChargeeDevice, ChargeeMeasurement


class ChargeeLocalApiClient:
    """Talk to a Chargee P1 dongle over its local HTTP API."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        *,
        port: int = 80,
        timeout: int = 10,
    ) -> None:
        """Initialize the client.

        Args:
            host: IP address or hostname of the dongle (without scheme).
            session: Shared aiohttp session (provided by Home Assistant).
            port: HTTP port, defaults to 80.
            timeout: Per-request timeout in seconds.
        """
        self._host = host
        self._port = port
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def base_url(self) -> URL:
        """Return the base URL for the device."""
        return URL.build(scheme="http", host=self._host, port=self._port)

    async def _request(self, path: str) -> aiohttp.ClientResponse:
        """Perform a GET request and return the raw response."""
        url = self.base_url.join(URL(path))
        try:
            response = await self._session.get(url, timeout=self._timeout)
        except asyncio.TimeoutError as err:
            raise ChargeeConnectionError(
                f"Timeout while connecting to {self._host}"
            ) from err
        except aiohttp.ClientError as err:
            raise ChargeeConnectionError(
                f"Error connecting to {self._host}: {err}"
            ) from err

        if response.status != 200:
            response.release()
            raise ChargeeResponseError(
                f"Unexpected status {response.status} from {url}"
            )
        return response

    async def _get_json(self, path: str) -> dict[str, Any]:
        """Perform a GET request and decode a JSON object response."""
        response = await self._request(path)
        try:
            # The dongle sets the correct content-type, but be lenient.
            data = await response.json(content_type=None)
        except (aiohttp.ContentTypeError, ValueError) as err:
            raise ChargeeResponseError(
                f"Invalid JSON received from {path}"
            ) from err
        finally:
            response.release()

        if not isinstance(data, dict):
            raise ChargeeResponseError(f"Expected JSON object from {path}")
        return data

    async def get_device(self) -> ChargeeDevice:
        """Return device information from ``/api``."""
        return ChargeeDevice.from_dict(await self._get_json("/api"))

    async def get_measurement(self) -> ChargeeMeasurement:
        """Return the most recent measurement from ``/api/v1/data``."""
        return ChargeeMeasurement.from_dict(await self._get_json("/api/v1/data"))

    async def get_telegram(self) -> str:
        """Return the most recent raw DSMR telegram from ``/api/v1/telegram``."""
        response = await self._request("/api/v1/telegram")
        try:
            return await response.text()
        finally:
            response.release()

    async def identify(self) -> bool:
        """Blink the status light via ``/api/v1/identify``."""
        data = await self._get_json("/api/v1/identify")
        return data.get("identify") == "ok"
