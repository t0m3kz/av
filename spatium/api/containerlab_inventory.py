"""ContainerLab inventory deployment API endpoints.

Handles deployment of network topologies using device inventories.
"""

import logging
from typing import Any

from fastapi import APIRouter, Query
import requests

from spatium.api.dependencies import get_inventory_service
from spatium.api.exceptions import DeploymentError, create_http_exception
from spatium.core.config import get_settings
from spatium.models.deployment import DeploymentResponse

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(
    prefix="/devices/inventory",
    tags=["deployment"],
    responses={404: {"description": "Not found"}},
)


def _validate_links(links: list[dict]) -> list[dict]:
    """Validate and convert links to ContainerLab format."""
    clab_links = []
    for i, link in enumerate(links):
        try:
            if "endpoints" in link:
                if not isinstance(link["endpoints"], list) or len(link["endpoints"]) != 2:
                    raise ValueError("endpoints must be a list with exactly 2 elements")
                clab_links.append({"endpoints": link["endpoints"]})
            elif "a" in link and "b" in link:
                clab_links.append({"endpoints": [link["a"], link["b"]]})
            else:
                raise ValueError("link must have 'endpoints' or 'a' and 'b' fields")
        except (KeyError, ValueError) as e:
            raise create_http_exception(
                422,
                f"Invalid link format at index {i}: {e}",
                {"link_index": i, "link_data": link},
            ) from e
    return clab_links


def _compose_topology(body: dict, nodes: dict, clab_links: list[dict]) -> dict:
    """Compose the topology dictionary for ContainerLab."""
    return {
        "name": body.get("name", "spatium-inventory-topo"),
        "prefix": body.get("prefix", "spatium"),
        "mgmt": {
            "network": body.get("mgmt_network", "spatium-mgmt"),
            "ipv4-subnet": body.get("mgmt_subnet", "172.20.0.0/23"),
        },
        "topology": {"nodes": nodes, "links": clab_links},
    }


@router.post("/deploy-containerlab", response_model=DeploymentResponse)
async def deploy_containerlab_topology(
    body: dict[str, Any],
    inventory: str = Query("default", description="Inventory name to deploy"),
) -> DeploymentResponse:
    """Deploy a ContainerLab topology using devices from the specified inventory.

    Args:
        body: Dictionary containing topology configuration with 'links' field
        inventory: Name of the inventory to use for deployment
        inventory_service: Injected inventory service

    Returns:
        DeploymentResponse: Status of the deployment operation

    Raises:
        HTTPException: When validation fails or deployment errors occur
    """
    inventory_service = get_inventory_service()
    try:
        # Validate input
        links = body.get("links")
        if not isinstance(links, list):
            raise create_http_exception(
                422,
                "Invalid input: 'links' must be a list of connections",
                {"field": "links", "expected_type": "list"},
            )

        # Get topology name from body or use default
        topology_name = body.get("name", "spatium-inventory-topo")

        # Build nodes from inventory
        inventory_devices = inventory_service.get_inventory(inventory)
        if not inventory_devices:
            raise create_http_exception(
                400,
                f"No devices found in inventory '{inventory}'",
                {"inventory": inventory, "device_count": 0},
            )

        nodes = {}
        for device in inventory_devices:
            nodes[device.host] = {
                "kind": device.device_model or "linux",  # fallback kind
                "image": "auto",  # Could be configurable in the future
            }

        logger.info(
            f"Building topology '{topology_name}' with {len(nodes)} nodes "
            f"from inventory '{inventory}'"
        )

        # Validate and convert links to ContainerLab format
        clab_links = _validate_links(links)

        # Compose topology in ContainerLab format
        topology = _compose_topology(body, nodes, clab_links)

        # Get ContainerLab API URL from settings or use default
        clab_api_url = settings.CONTAINERLAB_API_URL
        api_endpoint = f"{clab_api_url}/v0/topologies"

        logger.info(f"Deploying topology to ContainerLab API at {api_endpoint}")

        # Call ContainerLab API
        response = requests.post(api_endpoint, json=topology, timeout=settings.CONTAINERLAB_TIMEOUT)
        response.raise_for_status()

        result = response.json()
        logger.info(f"Successfully deployed topology '{topology_name}'")

        return DeploymentResponse(
            success=True,
            topology_name=topology_name,
            topology_file=None,  # ContainerLab API doesn't return file path
            output=str(result),
            error=None,
        )

    except requests.RequestException as e:
        error_msg = f"ContainerLab API request failed: {e}"
        logger.error(error_msg)
        raise create_http_exception(
            503,
            "ContainerLab service unavailable",
            {"error": error_msg, "api_url": api_endpoint},
        ) from e
    except DeploymentError as e:
        logger.error(f"Deployment error: {e}")
        raise create_http_exception(500, f"Deployment failed: {e}") from e
    except Exception as e:
        error_msg = f"Unexpected error during topology deployment: {e}"
        logger.error(error_msg)
        raise create_http_exception(500, error_msg) from e
