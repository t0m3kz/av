from pydantic import BaseModel, Field


class NodeConfig(BaseModel):
    """Node configuration for a topology."""

    name: str = Field(..., description="Node name")
    type: str = Field("sonic-vs", description="Node type/kind")
    image: str = Field("docker-sonic-vs:latest", description="Container image")
    ports: list[str] | None = Field(None, description="Port mappings")


class LinkConfig(BaseModel):
    """Link configuration between nodes in a topology."""

    node1: str = Field(..., description="First node name")
    interface1: str | None = Field("", description="First node interface")
    node2: str = Field(..., description="Second node name")
    interface2: str | None = Field("", description="Second node interface")


class TopologyConfig(BaseModel):
    """Topology configuration including nodes and links."""

    name: str = Field(..., description="Topology name")
    nodes: list[NodeConfig] = Field(..., description="List of nodes")
    links: list[LinkConfig] = Field(..., description="List of links")
    mgmt_network: str | None = Field("spatium-mgmt", description="Management network name")


class DeploymentResponse(BaseModel):
    """Response model for deployment operations."""

    success: bool = Field(..., description="Whether the operation was successful")
    topology_name: str | None = Field(None, description="Topology name")
    topology_file: str | None = Field(None, description="Path to topology file")
    output: str | None = Field(None, description="Command output")
    error: str | None = Field(None, description="Error message if operation failed")
