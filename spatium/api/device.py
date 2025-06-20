# Application context: The working directory is set to the project root ('.') at startup (see main.py)
from fastapi import APIRouter, Depends
from spatium.device_config.ssh_client import SSHClient
from spatium.models.device import DeviceConfigRequest, DeviceConfigResponse
from typing import List, Callable
import os
import json
from datetime import datetime

router = APIRouter()

def get_ssh_client_factory():
    return SSHClient

@router.post(
    "/device/configs", response_model=List[DeviceConfigResponse]
)
async def get_device_configs(
    requests: List[DeviceConfigRequest],
    ssh_client_factory: Callable = Depends(get_ssh_client_factory),
    save_output: bool = False,  # New query param to control saving
):
    responses = []
    for idx, req in enumerate(requests):
        try:
            client = ssh_client_factory(
                host=req.host,
                username=req.username,
                password=req.password,
                private_key=req.private_key,
                port=req.port,
            )
            result = await client.get_config()
            for field in ("running_config", "version_info", "interfaces"):
                if field not in result:
                    result[field] = None
            responses.append(result)
        except Exception as e:
            result = {
                "error": str(e),
                "source": "ssh",
                "running_config": None,
                "version_info": None,
                "interfaces": None,
            }
            responses.append(result)
        # Save each result as a JSON file if requested
        if save_output:
            os.makedirs("outputs", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/device_config_{idx}_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)
    return responses
