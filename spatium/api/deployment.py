"""
Deployment API endpoints for network topology management.
Provides endpoints for deploying, destroying, and listing network topologies.
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends

from spatium.api.exceptions import create_http_exception, DeploymentError
from spatium.models.deployment import TopologyConfig, DeploymentResponse
from spatium.services.deployment import ContainerLabDeploymentService
from spatium.api.dependencies import get_deployment_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/deployment",
    tags=["deployment"],
    responses={404: {"description": "Not found"}},
)


@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_topology(
    config: TopologyConfig,
    deployment_service: ContainerLabDeploymentService = Depends(get_deployment_service)
) -> DeploymentResponse:
    """
    Deploy a network topology using ContainerLab.
    
    Args:
        config: Topology configuration including nodes and links
        deployment_service: Injected deployment service
        
    Returns:
        DeploymentResponse: Result of the deployment operation
    """
    try:
        logger.info(f"Deploying topology '{config.name}' with {len(config.nodes)} nodes")
        result = await deployment_service.deploy_topology(config)
        return result
    except DeploymentError as e:
        logger.error(f"Deployment error: {e}")
        raise create_http_exception(500, f"Deployment failed: {e}")
    except Exception as e:
        error_msg = f"Unexpected error during deployment: {e}"
        logger.error(error_msg)
        raise create_http_exception(500, error_msg)


@router.delete("/destroy/{topology_name}", response_model=DeploymentResponse)
async def destroy_topology(
    topology_name: str,
    deployment_service: ContainerLabDeploymentService = Depends(get_deployment_service)
) -> DeploymentResponse:
    """
    Destroy a deployed topology.
    
    Args:
        topology_name: Name of the topology to destroy
        deployment_service: Injected deployment service
        
    Returns:
        DeploymentResponse: Result of the destroy operation
    """
    try:
        logger.info(f"Destroying topology '{topology_name}'")
        result = await deployment_service.destroy_topology(topology_name)
        return result
    except DeploymentError as e:
        logger.error(f"Destroy error: {e}")
        raise create_http_exception(500, f"Failed to destroy topology: {e}")
    except Exception as e:
        error_msg = f"Unexpected error during destroy: {e}"
        logger.error(error_msg)
        raise create_http_exception(500, error_msg)


@router.get("/list")
async def list_deployments(
    deployment_service: ContainerLabDeploymentService = Depends(get_deployment_service)
) -> Dict[str, Any]:
    """
    List all deployed topologies.
    
    Args:
        deployment_service: Injected deployment service
        
    Returns:
        Dict containing list of deployed topologies and their status
    """
    try:
        logger.info("Listing all deployments")
        result = await deployment_service.list_deployments()
        return result
    except Exception as e:
        error_msg = f"Failed to list deployments: {e}"
        logger.error(error_msg)
        raise create_http_exception(500, error_msg)
