"""FastAPI dependencies for the Spatium API."""

from collections.abc import Callable
from functools import lru_cache
from typing import Any

from spatium.clients.rest_client import RestClient
from spatium.clients.ssh_client import SSHClient
from spatium.services.deployment import ContainerLabDeploymentService
from spatium.services.device_config import DeviceConfigService
from spatium.services.inventory import InventoryService


def get_ssh_client_factory() -> Callable:
    """Get SSH client factory for dependency injection."""
    return SSHClient


def get_rest_client_factory() -> Callable:
    """Get REST client factory for dependency injection."""
    return RestClient


@lru_cache
def get_inventory_service() -> InventoryService:
    """Get inventory service instance (singleton)."""
    return InventoryService()


def get_device_config_service(
    ssh_client_factory: Callable[..., Any] | None = None,
    rest_client_factory: Callable[..., Any] | None = None,
) -> DeviceConfigService:
    """Get device configuration service instance."""
    if ssh_client_factory is None:
        ssh_client_factory = get_ssh_client_factory()
    if rest_client_factory is None:
        rest_client_factory = get_rest_client_factory()
    return DeviceConfigService(ssh_client_factory, rest_client_factory)


@lru_cache
def get_deployment_service() -> ContainerLabDeploymentService:
    """Get deployment service instance (singleton)."""
    return ContainerLabDeploymentService()
