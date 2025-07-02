"""Inventory service for managing device inventories."""

import logging

from spatium.api.exceptions import DeviceNotFoundError
from spatium.models.device import DeviceConfigRequest

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for managing device inventories."""

    def __init__(self) -> None:
        """Initialize InventoryService with empty inventories."""
        self._inventories: dict[str, list[DeviceConfigRequest]] = {}

    def get_inventory(self, name: str = "default") -> list[DeviceConfigRequest]:
        """Get devices from specified inventory."""
        if not name or not isinstance(name, str):
            name = "default"

        if name not in self._inventories:
            self._inventories[name] = []

        return self._inventories[name]

    def add_devices(
        self, devices: list[DeviceConfigRequest], inventory_name: str = "default"
    ) -> list[str]:
        """Add devices to inventory. Returns list of added device hosts."""
        inventory = self.get_inventory(inventory_name)
        existing_hosts = {device.host for device in inventory}
        added_hosts = []

        for device in devices:
            if device.host not in existing_hosts:
                inventory.append(device)
                added_hosts.append(device.host)
                existing_hosts.add(device.host)
            else:
                logger.warning(f"Device {device.host} already exists in inventory {inventory_name}")

        return added_hosts

    def remove_devices(self, device_hosts: set[str], inventory_name: str = "default") -> list[str]:
        """Remove devices from inventory by host. Returns list of removed hosts."""
        inventory = self.get_inventory(inventory_name)
        original_count = len(inventory)

        self._inventories[inventory_name] = [
            device for device in inventory if device.host not in device_hosts
        ]

        removed_count = original_count - len(self._inventories[inventory_name])
        removed_hosts = list(device_hosts.intersection({device.host for device in inventory}))

        logger.info(f"Removed {removed_count} devices from inventory {inventory_name}")
        return removed_hosts

    def clear_inventory(self, inventory_name: str = "default") -> int:
        """Clear all devices from inventory. Returns number of devices removed."""
        inventory = self.get_inventory(inventory_name)
        count = len(inventory)
        inventory.clear()

        logger.info(f"Cleared {count} devices from inventory {inventory_name}")
        return count

    def list_inventory_names(self) -> list[str]:
        """Get list of all inventory names."""
        return list(self._inventories.keys())

    def get_device_by_host(self, host: str, inventory_name: str = "default") -> DeviceConfigRequest:
        """Get a specific device by host from inventory."""
        inventory = self.get_inventory(inventory_name)

        for device in inventory:
            if device.host == host:
                return device

        raise DeviceNotFoundError(
            f"Device with host '{host}' not found in inventory '{inventory_name}'"
        )

    def filter_devices_by_host(
        self, host: str, inventory_name: str = "default"
    ) -> list[DeviceConfigRequest]:
        """Filter devices by host from inventory."""
        inventory = self.get_inventory(inventory_name)
        return [device for device in inventory if device.host == host]

    def get_inventory_stats(
        self, inventory_name: str = "default"
    ) -> dict[str, int | dict[str, int]]:
        """Get statistics for an inventory."""
        inventory = self.get_inventory(inventory_name)
        device_models: dict[str, int] = {}

        for device in inventory:
            model = device.device_model or "unknown"
            device_models[model] = device_models.get(model, 0) + 1

        return {"total_devices": len(inventory), "device_models": device_models}
