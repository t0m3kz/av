from fastapi import APIRouter, HTTPException
from spatium.models.device import DeviceCredentials
from spatium.device_config.sonic_client import SonicClient
from typing import Dict, Any

router = APIRouter(
    prefix="/device",
    tags=["device"],
    responses={404: {"description": "Not found"}},
)

sonic_client = SonicClient()

@router.post("/config")
async def get_device_config(credentials: DeviceCredentials) -> Dict[str, Any]:
    """
    Retrieve configuration from a SONiC device.
    
    This endpoint connects to a SONiC device using the specified method (SSH, gNMI, or both)
    and retrieves its configuration.
    """
    try:
        config = await sonic_client.get_config(
            host=credentials.host,
            username=credentials.username,
            password=credentials.password,
            method=credentials.method,
            ssh_port=credentials.ssh_port,
            gnmi_port=credentials.gnmi_port,
            private_key=credentials.private_key_path,
            gnmi_paths=credentials.gnmi_paths
        )
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get device configuration: {str(e)}")