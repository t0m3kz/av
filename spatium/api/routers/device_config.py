"""Device configuration retrieval API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, Query

from spatium.api.dependencies import get_device_config_service, get_inventory_service
from spatium.api.exceptions import create_http_exception
from spatium.api.responses import ConfigResponse, ConfigSaveResponse
from spatium.models.device import DeviceConfigRequest
from spatium.services.device_config import DeviceConfigService
from spatium.services.inventory import InventoryService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/configs",
    tags=["device-config"],
    responses={404: {"description": "Not found"}},
)


@router.post("/get", response_model=ConfigResponse)
async def get_device_configs(
    inventory: str = Query("default", description="Inventory name"),
    host: str | None = Query(None, description="Filter by specific host"),
    inventory_service: InventoryService = Depends(get_inventory_service),
    config_service: DeviceConfigService = Depends(get_device_config_service),
) -> ConfigResponse:
    """Fetch configurations from devices in the specified inventory."""
    try:
        # Get devices from inventory
        if host:
            devices = inventory_service.filter_devices_by_host(host, inventory)
            if not devices:
                return ConfigResponse(
                    success=True,
                    message=f"No device found with host '{host}' in inventory '{inventory}'",
                    inventory=inventory,
                    results=[],
                    messages=[f"No device found with host '{host}' in inventory '{inventory}'"],
                )
        else:
            devices = inventory_service.get_inventory(inventory)
            if not devices:
                return ConfigResponse(
                    success=True,
                    message=f"No devices found in inventory '{inventory}'",
                    inventory=inventory,
                    results=[],
                    messages=[f"No devices found in inventory '{inventory}'"],
                )

        # Fetch configurations
        results = await config_service.fetch_configs_bulk(devices)

        # Generate messages
        messages = []
        for result in results:
            if result.error:
                messages.append(f"Failed to fetch config for {result.host}: {result.error}")
            else:
                messages.append(f"Configuration fetched for {result.host}")

        return ConfigResponse(
            success=True,
            message=f"Retrieved configurations for {len(results)} device(s)",
            inventory=inventory,
            results=results,
            messages=messages,
        )

    except Exception as e:
        logger.error(f"Error fetching device configs from inventory {inventory}: {e}")
        raise create_http_exception(500, f"Failed to fetch device configurations: {e}") from e


@router.post("/save", response_model=ConfigSaveResponse)
async def save_device_configs(
    inventory: str = Query("default", description="Inventory name"),
    host: str | None = Query(None, description="Filter by specific host"),
    output_folder: str = Query("outputs", description="Output folder for saved configurations"),
    inventory_service: InventoryService = Depends(get_inventory_service),
    config_service: DeviceConfigService = Depends(get_device_config_service),
) -> ConfigSaveResponse:
    """Fetch configurations from devices and save them to files."""
    try:
        # Get devices from inventory
        if host:
            devices = inventory_service.filter_devices_by_host(host, inventory)
            if not devices:
                return ConfigSaveResponse(
                    success=True,
                    message=f"No device found with host '{host}' in inventory '{inventory}'",
                    inventory=inventory,
                    results=[],
                )
        else:
            devices = inventory_service.get_inventory(inventory)
            if not devices:
                return ConfigSaveResponse(
                    success=True,
                    message=f"No devices found in inventory '{inventory}'",
                    inventory=inventory,
                    results=[],
                )

        # Fetch and save configurations
        results = await config_service.save_configs_to_files(devices, output_folder)

        success_count = sum(1 for r in results if not r.error)

        return ConfigSaveResponse(
            success=True,
            message=f"Saved configurations for {success_count}/{len(results)} device(s)",
            inventory=inventory,
            results=results,
        )

    except Exception as e:
        logger.error(f"Error saving device configs from inventory {inventory}: {e}")
        raise create_http_exception(500, f"Failed to save device configurations: {e}") from e


@router.post("/device", response_model=ConfigResponse)
async def get_single_device_config(
    device: DeviceConfigRequest = Body(..., description="Device configuration request"),
    config_service: DeviceConfigService = Depends(get_device_config_service),
) -> ConfigResponse:
    """Fetch configuration from a single device using specified method (SSH or REST)."""
    try:
        result = await config_service.fetch_config(device)

        message = f"Configuration fetched from {device.host} via {device.method or 'ssh'}"
        if result.error:
            message = f"Failed to fetch config from {device.host}: {result.error}"

        return ConfigResponse(
            success=not bool(result.error),
            message=message,
            inventory="single-device",
            results=[result],
            messages=[message],
        )

    except Exception as e:
        logger.error(f"Error fetching config from device {device.host}: {e}")
        raise create_http_exception(500, f"Failed to fetch device configuration: {e}") from e


@router.post("/test-connectivity")
async def test_device_connectivity(
    devices: list[DeviceConfigRequest],
    config_service: DeviceConfigService = Depends(get_device_config_service),
) -> dict[str, Any]:
    """Test connectivity to devices using the config service."""
    try:
        connectivity_results = []

        for device in devices:
            method = (device.method or "ssh").lower()

            if method == "rest":
                # Test REST connectivity
                try:
                    rest_client = config_service.rest_client_factory(
                        host=device.host,
                        username=device.username,
                        password=device.password,
                        port=device.port or 80,
                        use_https=False,
                        device_type=(device.device_model or "").lower(),
                        timeout=10,
                    )
                    is_connected = await rest_client.test_connection()
                    connectivity_results.append(
                        {
                            "host": device.host,
                            "method": "rest",
                            "connected": is_connected,
                            "error": None if is_connected else "Connection failed",
                        }
                    )
                except Exception as e:
                    connectivity_results.append(
                        {"host": device.host, "method": "rest", "connected": False, "error": str(e)}
                    )
            else:
                # Test SSH connectivity
                try:
                    ssh_client = config_service.ssh_client_factory(
                        host=device.host,
                        username=device.username,
                        password=device.password,
                        private_key=device.private_key,
                        port=device.port or 22,
                        timeout=10,
                    )
                    is_connected = await ssh_client.test_connection()
                    connectivity_results.append(
                        {
                            "host": device.host,
                            "method": "ssh",
                            "connected": is_connected,
                            "error": None if is_connected else "Connection failed",
                        }
                    )
                except Exception as e:
                    connectivity_results.append(
                        {"host": device.host, "method": "ssh", "connected": False, "error": str(e)}
                    )

        successful_connections = sum(1 for r in connectivity_results if r["connected"])

        return {
            "success": True,
            "message": (
                f"Tested connectivity to {len(devices)} device(s). "
                f"{successful_connections} successful."
            ),
            "results": connectivity_results,
        }

    except Exception as e:
        logger.error(f"Error testing device connectivity: {e}")
        raise create_http_exception(500, f"Failed to test device connectivity: {e}") from e
