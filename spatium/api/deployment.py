from fastapi import APIRouter, HTTPException
from spatium.models.deployment import TopologyConfig, DeploymentResponse
from spatium.deployment.containerlab import ContainerLabDeployer
from typing import Dict, Any

router = APIRouter(
    prefix="/deployment",
    tags=["deployment"],
    responses={404: {"description": "Not found"}},
)

deployer = ContainerLabDeployer()


@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_topology(config: TopologyConfig) -> Dict[str, Any]:
    """
    Deploy a network topology using ContainerLab.
    """
    try:
        topology = deployer.create_sonic_topology(
            name=config.name,
            nodes=[node.model_dump() for node in config.nodes],
            links=[link.model_dump() for link in config.links],
            mgmt_network=config.mgmt_network,
        )
        result = await deployer.deploy_topology(topology)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {e}")


@router.delete("/destroy/{topology_name}", response_model=DeploymentResponse)
async def destroy_topology(topology_name: str) -> Dict[str, Any]:
    """
    Destroy a deployed topology.
    """
    try:
        result = await deployer.destroy_topology(topology_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to destroy topology: {e}")


@router.get("/list")
async def list_deployments() -> Dict[str, Any]:
    """
    List all deployed topologies.
    """
    try:
        result = await deployer.list_deployments()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list deployments: {e}")
