"""Response models for the Spatium API."""

from typing import Any

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model."""

    success: bool = Field(default=True, description="Whether the operation was successful")
    message: str | None = Field(None, description="Response message")


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")


class InventoryResponse(BaseResponse):
    """Response model for inventory operations."""

    inventory: str = Field(..., description="Inventory name")
    affected_hosts: list[str] | None = Field(None, description="List of affected host IPs")


class DeviceConfigResult(BaseModel):
    """Result model for device configuration retrieval."""

    host: str = Field(..., description="Device host IP or hostname")
    running_config: str | dict[str, Any] | None = Field(
        None, description="Device running configuration"
    )
    source: str = Field(..., description="Configuration source (ssh/rest)")
    error: str | None = Field(None, description="Error message if retrieval failed")


class ConfigResponse(BaseResponse):
    """Response model for device configuration operations."""

    inventory: str = Field(..., description="Inventory name")
    results: list[DeviceConfigResult] = Field(..., description="Configuration results")
    messages: list[str] = Field(default_factory=list, description="Operation messages")


class ConfigSaveResult(BaseModel):
    """Result model for configuration save operations."""

    host: str = Field(..., description="Device host IP or hostname")
    source: str = Field(..., description="Configuration source (ssh/rest)")
    error: str | None = Field(None, description="Error message if save failed")
    message: str = Field(..., description="Save operation message")
    file_path: str | None = Field(None, description="Path to saved configuration file")


class ConfigSaveResponse(BaseResponse):
    """Response model for configuration save operations."""

    inventory: str = Field(..., description="Inventory name")
    results: list[ConfigSaveResult] = Field(..., description="Save results")
