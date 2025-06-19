from fastapi import APIRouter, HTTPException
from spatium.models.device import DeviceCredentials, ConfigAnalysisRequest
from spatium.device_config.sonic_client import SonicClient
from spatium.analysis.batfish_analyzer import analyze_config_with_batfish
from typing import Dict, Any

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)

sonic_client = SonicClient()


@router.post("/config")
async def analyze_config(request: ConfigAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze network device configuration using Batfish.

    This endpoint accepts a device configuration as text and analyzes it using Batfish.
    """
    try:
        analysis = analyze_config_with_batfish(request.config)
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/device")
async def analyze_device_config(credentials: DeviceCredentials) -> Dict[str, Any]:
    """
    Retrieve and analyze configuration from a SONiC device.

    This endpoint connects to a SONiC device, retrieves its configuration,
    and then analyzes it using Batfish.
    """
    try:
        # First, get the config
        config = await sonic_client.get_config(
            host=credentials.host,
            username=credentials.username,
            password=credentials.password,
            method=credentials.method,
            ssh_port=credentials.ssh_port,
            gnmi_port=credentials.gnmi_port,
            private_key=credentials.private_key_path,
            gnmi_paths=credentials.gnmi_paths,
        )

        # Extract the running config for analysis
        running_config = None
        if "ssh" in config and "running_config" in config["ssh"]:
            running_config = config["ssh"]["running_config"]

        if not running_config:
            return {
                "config": config,
                "analysis": None,
                "error": "Could not extract running configuration for analysis",
            }

        # Analyze with Batfish
        analysis = analyze_config_with_batfish(running_config)

        return {"config": config, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
