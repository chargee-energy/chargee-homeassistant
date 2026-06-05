"""Config flow for the Chargee P1 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession

try:  # Home Assistant 2025.2+ moved the service info models.
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
except ImportError:  # pragma: no cover - fallback for HA < 2025.2
    from homeassistant.components.zeroconf import ZeroconfServiceInfo

from .api import ChargeeError, ChargeeLocalApiClient
from .const import (
    CONF_PRODUCT_NAME,
    CONF_PRODUCT_TYPE,
    CONF_SERIAL,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DOMAIN,
    LOGGER,
    ZEROCONF_DEVICE,
    ZEROCONF_SERIAL,
)


class ChargeeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chargee P1."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._host: str | None = None
        self._discovered_name: str | None = None

    async def _async_validate(self, host: str, port: int) -> dict[str, str]:
        """Connect to the device and return its identifying info.

        Raises ChargeeError on failure.
        """
        session = async_get_clientsession(self.hass)
        client = ChargeeLocalApiClient(
            host=host, session=session, port=port, timeout=DEFAULT_TIMEOUT
        )
        device = await client.get_device()
        if not device.serial:
            raise ChargeeError("Device did not report a serial number")
        return {
            CONF_SERIAL: device.serial,
            CONF_PRODUCT_NAME: device.product_name or "Chargee P1",
            CONF_PRODUCT_TYPE: device.product_type or "",
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the manual setup step where the user enters a host."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            try:
                info = await self._async_validate(host, port)
            except ChargeeError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - surface unexpected errors safely
                LOGGER.exception("Unexpected error connecting to Chargee device")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info[CONF_SERIAL])
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=info[CONF_PRODUCT_NAME],
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        **info,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=self._host or ""): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle a device discovered via mDNS."""
        host = discovery_info.host
        properties = discovery_info.properties
        serial = properties.get(ZEROCONF_SERIAL)

        if not serial:
            return self.async_abort(reason="no_serial")

        await self.async_set_unique_id(serial)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._host = host
        device_kind = (properties.get(ZEROCONF_DEVICE) or "Chargee").capitalize()
        self._discovered_name = f"{device_kind} {serial}"

        self.context["title_placeholders"] = {"name": self._discovered_name}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup of a discovered device."""
        errors: dict[str, str] = {}
        assert self._host is not None

        if user_input is not None:
            try:
                info = await self._async_validate(self._host, DEFAULT_PORT)
            except ChargeeError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error connecting to Chargee device")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info[CONF_PRODUCT_NAME],
                    data={
                        CONF_HOST: self._host,
                        CONF_PORT: DEFAULT_PORT,
                        **info,
                    },
                )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"name": self._discovered_name or "Chargee P1"},
            errors=errors,
        )
