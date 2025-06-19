from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class DeviceCredentials(BaseModel):
    host: str = Field(..., description="Device hostname or IP address")
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    method: Literal["ssh", "gnmi", "both"] = Field(
        "both", description="Configuration retrieval method"
    )
    ssh_port: int = Field(22, description="SSH port")
    gnmi_port: int = Field(8080, description="gNMI port")
    private_key_path: Optional[str] = Field(
        None, description="Path to SSH private key file"
    )
    gnmi_paths: Optional[List[str]] = Field(
        None, description="List of gNMI paths to query"
    )


class ConfigAnalysisRequest(BaseModel):
    config: str = Field(..., description="Device configuration text to analyze")
