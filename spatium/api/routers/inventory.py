"""Device inventory management API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from spatium.api.dependencies import get_inventory_service
from spatium.api.exceptions import create_http_exception
from spatium.api.responses import InventoryResponse
from spatium.models.device import DeviceConfigRequest
from spatium.services.inventory import InventoryService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add", response_model=InventoryResponse)
async def add_devices_to_inventory(
    request: Request,
    inventory: str = Query("default", description="Inventory name"),
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Add devices to the inventory."""
    try:
        data = await request.json()

        # Handle single device or list of devices
        if isinstance(data, dict):
            devices = [DeviceConfigRequest(**data)]
        elif isinstance(data, list):
            devices = [DeviceConfigRequest(**item) for item in data]
        else:
            raise HTTPException(
                status_code=422,
                detail="Request body must be a device object or list of device objects",
            )

        added_hosts = inventory_service.add_devices(devices, inventory)

        if not added_hosts:
            return InventoryResponse(
                success=True,
                message="No new devices were added (all devices already exist)",
                inventory=inventory,
                affected_hosts=[],
            )

        return InventoryResponse(
            success=True,
            message=f"Successfully added {len(added_hosts)} device(s) to inventory",
            inventory=inventory,
            affected_hosts=added_hosts,
        )

    except ValueError as e:
        raise create_http_exception(422, f"Validation error: {e}") from e
    except Exception as e:
        logger.error(f"Error adding devices to inventory {inventory}: {e}")
        raise create_http_exception(500, f"Failed to add devices: {e}") from e


@router.get("/list", response_model=list[DeviceConfigRequest])
def list_devices_in_inventory(
    inventory: str = Query("default", description="Inventory name"),
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> list[DeviceConfigRequest]:
    """List devices in the inventory."""
    """List all devices in the specified inventory."""
    try:
        return inventory_service.get_inventory(inventory)
    except Exception as e:
        logger.error(f"Error listing devices in inventory {inventory}: {e}")
        raise create_http_exception(500, f"Failed to list devices: {e}") from e


@router.post("/remove", response_model=InventoryResponse)
async def remove_devices_from_inventory(
    request: Request,
    inventory: str = Query("default", description="Inventory name"),
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Remove devices from the inventory."""
    try:
        data = await request.json()

        # Handle single device or list of devices
        if isinstance(data, dict):
            devices = [DeviceConfigRequest(**data)]
        elif isinstance(data, list):
            devices = [DeviceConfigRequest(**item) for item in data]
        else:
            raise HTTPException(
                status_code=422,
                detail="Request body must be a device object or list of device objects",
            )

        device_hosts = {device.host for device in devices}
        removed_hosts = inventory_service.remove_devices(device_hosts, inventory)

        return InventoryResponse(
            success=True,
            message=f"Successfully removed {len(removed_hosts)} device(s) from inventory",
            inventory=inventory,
            affected_hosts=removed_hosts,
        )

    except ValueError as e:
        raise create_http_exception(422, f"Validation error: {e}") from e
    except Exception as e:
        logger.error(f"Error removing devices from inventory {inventory}: {e}")
        raise create_http_exception(500, f"Failed to remove devices: {e}") from e


@router.post("/clear", response_model=InventoryResponse)
def clear_inventory(
    inventory: str = Query("default", description="Inventory name"),
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Clear the inventory."""
    """Clear all devices from the specified inventory."""
    try:
        removed_count = inventory_service.clear_inventory(inventory)

        return InventoryResponse(
            success=True,
            message=f"Successfully cleared {removed_count} device(s) from inventory",
            inventory=inventory,
            affected_hosts=[],
        )

    except Exception as e:
        logger.error(f"Error clearing inventory {inventory}: {e}")
        raise create_http_exception(500, f"Failed to clear inventory: {e}") from e


@router.get("/names")
def list_inventory_names(
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> list[str]:
    """List all inventory names."""
    """List all inventory names."""
    try:
        return inventory_service.list_inventory_names()
    except Exception as e:
        logger.error(f"Error listing inventory names: {e}")
        raise create_http_exception(500, f"Failed to list inventory names: {e}") from e


@router.get("/stats")
def get_inventory_stats(
    inventory: str = Query("default", description="Inventory name"),
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> dict[str, int | dict[str, int]]:
    """Get inventory statistics."""
    """Get statistics for the specified inventory."""
    try:
        return inventory_service.get_inventory_stats(inventory)
    except Exception as e:
        logger.error(f"Error getting stats for inventory {inventory}: {e}")
        raise create_http_exception(500, f"Failed to get inventory stats: {e}") from e
