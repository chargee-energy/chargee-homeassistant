"""Data models for the Chargee API.

These dataclasses describe the documented Local API v1 payloads. They are kept
deliberately transport-agnostic so a future Cloud/Web API client can return the
exact same models, allowing the coordinator and entities to remain unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


def _get(data: dict[str, Any], key: str) -> Any:
    """Return a value, treating an explicit ``null`` the same as missing."""
    return data.get(key)


@dataclass(slots=True)
class ChargeeDevice:
    """Device information from the ``/api`` endpoint."""

    product_type: str | None = None
    product_name: str | None = None
    serial: str | None = None
    firmware_version: str | None = None
    api_version: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChargeeDevice":
        """Create a device from an API response, ignoring unknown keys."""
        known = {f.name for f in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in known})


@dataclass(slots=True)
class ChargeeMeasurement:
    """Most recent measurement from the ``/api/v1/data`` endpoint.

    Every field is optional: the API omits data points that are ``null`` or not
    available, which depends on the connected smart meter (e.g. single-phase
    Flint vs. three-phase Sparky with gas).
    """

    unique_id: str | None = None
    smr_version: int | None = None
    meter_model: str | None = None
    wifi_ssid: str | None = None
    wifi_strength: int | None = None
    active_tariff: int | None = None

    total_power_import_kwh: float | None = None
    total_power_import_t1_kwh: float | None = None
    total_power_import_t2_kwh: float | None = None
    total_power_export_kwh: float | None = None
    total_power_export_t1_kwh: float | None = None
    total_power_export_t2_kwh: float | None = None

    active_power_w: float | None = None
    active_power_l1_w: float | None = None
    active_power_l2_w: float | None = None
    active_power_l3_w: float | None = None

    active_voltage_l1_v: float | None = None
    active_voltage_l2_v: float | None = None
    active_voltage_l3_v: float | None = None

    active_current_a: float | None = None
    active_current_l1_a: float | None = None
    active_current_l2_a: float | None = None
    active_current_l3_a: float | None = None

    total_gas_m3: float | None = None
    gas_timestamp: int | None = None
    unique_gas_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChargeeMeasurement":
        """Create a measurement from an API response, ignoring unknown keys."""
        known = {f.name for f in fields(cls)}
        return cls(**{key: _get(data, key) for key in known if key in data})
