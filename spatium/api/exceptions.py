"""Custom exceptions for the Spatium API."""

from typing import Any

from fastapi import HTTPException


class SpatiumError(Exception):
    """Base exception for Spatium API."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize SpatiumError with message and optional details."""
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DeviceNotFoundError(SpatiumError):
    """Raised when a device is not found in inventory."""

    pass


class DeviceConnectionError(SpatiumError):
    """Raised when connection to device fails."""

    pass


class InventoryError(SpatiumError):
    """Raised when inventory operations fail."""

    pass


class ConfigurationError(SpatiumError):
    """Raised when configuration retrieval fails."""

    pass


class DeploymentError(SpatiumError):
    """Raised when deployment operations fail."""

    pass


def create_http_exception(
    status_code: int, message: str, details: dict[str, Any] | None = None
) -> HTTPException:
    """Create a standardized HTTP exception."""
    detail = {"message": message}
    if details:
        detail.update(details)
    return HTTPException(status_code=status_code, detail=detail)
