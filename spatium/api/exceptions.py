"""
Custom exceptions for the Spatium API.
"""
from fastapi import HTTPException
from typing import Any, Dict, Optional


class SpatiumException(Exception):
    """Base exception for Spatium API."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DeviceNotFoundError(SpatiumException):
    """Raised when a device is not found in inventory."""
    pass


class DeviceConnectionError(SpatiumException):
    """Raised when connection to device fails."""
    pass


class InventoryError(SpatiumException):
    """Raised when inventory operations fail."""
    pass


class ConfigurationError(SpatiumException):
    """Raised when configuration retrieval fails."""
    pass


class DeploymentError(SpatiumException):
    """Raised when deployment operations fail."""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create a standardized HTTP exception."""
    detail = {"message": message}
    if details:
        detail.update(details)
    return HTTPException(status_code=status_code, detail=detail)
