from pydantic import BaseModel, Field
from typing import List, Optional


class NodeConfig(BaseModel):
    name: str = Field(..., description="Node name")
    type: str = Field("sonic-vs", description="Node type/kind")
    image: str = Field("docker-sonic-vs:latest", description="Container image")
    ports: Optional[List[str]] = Field(None, description="Port mappings")


class LinkConfig(BaseModel):
    node1: str = Field(..., description="First node name")
    interface1: Optional[str] = Field("", description="First node interface")
    node2: str = Field(..., description="Second node name")
    interface2: Optional[str] = Field("", description="Second node interface")


class TopologyConfig(BaseModel):
    name: str = Field(..., description="Topology name")
    nodes: List[NodeConfig] = Field(..., description="List of nodes")
    links: List[LinkConfig] = Field(..., description="List of links")
    mgmt_network: Optional[str] = Field(
        "spatium-mgmt", description="Management network name"
    )


class DeploymentResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    topology_name: Optional[str] = Field(None, description="Topology name")
    topology_file: Optional[str] = Field(None, description="Path to topology file")
    output: Optional[str] = Field(None, description="Command output")
    error: Optional[str] = Field(None, description="Error message if operation failed")
