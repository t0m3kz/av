"""
Response models for the Spatium API.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = Field(default=True, description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Response message")


class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class InventoryResponse(BaseResponse):
    """Response model for inventory operations."""
    inventory: str = Field(..., description="Inventory name")
    affected_hosts: Optional[List[str]] = Field(None, description="List of affected host IPs")


class DeviceConfigResult(BaseModel):
    """Result model for device configuration retrieval."""
    host: str = Field(..., description="Device host IP or hostname")
    running_config: Optional[str] = Field(None, description="Device running configuration")
    source: str = Field(..., description="Configuration source (ssh/rest)")
    error: Optional[str] = Field(None, description="Error message if retrieval failed")


class ConfigResponse(BaseResponse):
    """Response model for device configuration operations."""
    inventory: str = Field(..., description="Inventory name")
    results: List[DeviceConfigResult] = Field(..., description="Configuration results")
    messages: List[str] = Field(default_factory=list, description="Operation messages")


class ConfigSaveResult(BaseModel):
    """Result model for configuration save operations."""
    host: str = Field(..., description="Device host IP or hostname")
    source: str = Field(..., description="Configuration source (ssh/rest)")
    error: Optional[str] = Field(None, description="Error message if save failed")
    message: str = Field(..., description="Save operation message")
    file_path: Optional[str] = Field(None, description="Path to saved configuration file")


class ConfigSaveResponse(BaseResponse):
    """Response model for configuration save operations."""
    inventory: str = Field(..., description="Inventory name")
    results: List[ConfigSaveResult] = Field(..., description="Save results")
