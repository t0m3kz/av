"""
FastAPI dependencies for the Spatium API.
"""
from functools import lru_cache
from typing import Callable

from fastapi import Depends

from spatium.core.config import get_settings, Settings
from spatium.clients.ssh_client import SSHClient
from spatium.clients.rest_client import RestClient
from spatium.services.inventory import InventoryService
from spatium.services.device_config import DeviceConfigService
from spatium.services.deployment import ContainerLabDeploymentService


def get_ssh_client_factory() -> Callable:
    """Get SSH client factory for dependency injection."""
    return SSHClient


def get_rest_client_factory() -> Callable:
    """Get REST client factory for dependency injection."""
    return RestClient


@lru_cache()
def get_inventory_service() -> InventoryService:
    """Get inventory service instance (singleton)."""
    return InventoryService()


def get_device_config_service(
    ssh_client_factory: Callable = Depends(get_ssh_client_factory),
    rest_client_factory: Callable = Depends(get_rest_client_factory)
) -> DeviceConfigService:
    """Get device configuration service instance."""
    return DeviceConfigService(ssh_client_factory, rest_client_factory)


@lru_cache()
def get_deployment_service() -> ContainerLabDeploymentService:
    """Get deployment service instance (singleton)."""
    return ContainerLabDeploymentService()
