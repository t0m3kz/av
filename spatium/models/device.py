from pydantic import BaseModel, Field


class DeviceConfigRequest(BaseModel):
    """Request model for device configuration."""

    host: str = Field(..., description="Device hostname or IP address")
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    port: int | None = Field(22, description="SSH port")
    private_key: str | None = Field(None, description="Path to SSH private key file")
    device_model: str | None = Field(
        None, description="Device model to select proper config command"
    )
    method: str | None = Field("ssh", description="Config retrieval method: 'ssh' or 'rest'")
    rest_url: str | None = Field(
        None, description="Custom REST API URL for config retrieval (overrides default)"
    )


class DeviceConfigResponse(BaseModel):
    """Response model for device configuration."""

    running_config: str | None
    version_info: str | None
    interfaces: str | None
    source: str
    error: str | None = None
