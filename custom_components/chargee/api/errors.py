"""Exceptions for the Chargee API client."""

from __future__ import annotations


class ChargeeError(Exception):
    """Base error for all Chargee client failures."""


class ChargeeConnectionError(ChargeeError):
    """Raised when the device cannot be reached (network/timeout)."""


class ChargeeResponseError(ChargeeError):
    """Raised when the device returns an unexpected or invalid response."""
