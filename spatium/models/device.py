from pydantic import BaseModel, Field
from typing import Optional


class DeviceConfigRequest(BaseModel):
    host: str = Field(..., description="Device hostname or IP address")
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    port: Optional[int] = Field(22, description="SSH port")
    private_key: Optional[str] = Field(
        None, description="Path to SSH private key file"
    )
    device_model: Optional[str] = Field(
        None, description="Device model to select proper config command"
    )
    method: Optional[str] = Field(
        "ssh", description="Config retrieval method: 'ssh' or 'rest'"
    )
    rest_url: Optional[str] = Field(
        None, description="Custom REST API URL for config retrieval (overrides default)"
    )


class DeviceConfigResponse(BaseModel):
    running_config: Optional[str]
    version_info: Optional[str]
    interfaces: Optional[str]
    source: str
    error: Optional[str] = None