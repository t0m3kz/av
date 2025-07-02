from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from spatium.models.deployment import LinkConfig, NodeConfig, TopologyConfig
from spatium.services.deployment import ContainerLabDeploymentService


class TestContainerLabDeployer:
    def test_create_topology_config(self):
        """Test creating a topology configuration object."""
        # Test data
        nodes = [
            NodeConfig(name="sonic1", type="sonic-vs", image="sonic:latest"),
            NodeConfig(name="sonic2", type="sonic-vs", image="sonic:latest"),
        ]
        links = [LinkConfig(node1="sonic1", interface1="eth1", node2="sonic2", interface2="eth1")]

        # Create topology config
        topology_config = TopologyConfig(name="test-topo", nodes=nodes, links=links)

        # Check topology config structure
        assert topology_config.name == "test-topo"
        assert len(topology_config.nodes) == 2
        assert len(topology_config.links) == 1
        assert topology_config.nodes[0].name == "sonic1"
        assert topology_config.nodes[0].type == "sonic-vs"
        assert topology_config.nodes[0].image == "sonic:latest"

    @pytest.mark.asyncio
    async def test_deploy_topology_success(self):
        """Test successful topology deployment."""
        # Create deployer with mocked subprocess
        with (
            patch(
                "spatium.services.deployment.asyncio.create_subprocess_exec", new=AsyncMock()
            ) as mock_subprocess,
            patch("spatium.services.deployment.yaml.dump") as mock_yaml_dump,
            patch("builtins.open", MagicMock()),
            patch("spatium.services.deployment.shutil.which", return_value="/usr/bin/containerlab"),
        ):
            # Set up mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"Deployed successfully", b"")
            mock_subprocess.return_value = mock_process

            # Create deployer and deploy topology
            deployer = ContainerLabDeploymentService()

            # Create a valid topology config
            topology_config = TopologyConfig(
                name="test-topo",
                nodes=[NodeConfig(name="sonic1", type="sonic-vs", image="sonic:latest")],
                links=[],
            )

            result = await deployer.deploy_topology(topology_config)

            # Check yaml was dumped
            mock_yaml_dump.assert_called_once()

            # Check subprocess was called with correct args
            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0]
            assert args[0] == "containerlab"
            assert args[1] == "deploy"
            assert args[2] == "-t"

            # Check result
            assert result.success is True
            assert result.topology_name == "test-topo"
            assert result.output is not None

    @pytest.mark.asyncio
    async def test_deploy_topology_failure(self):
        """Test failed topology deployment."""
        # Create deployer with mocked subprocess
        with (
            patch(
                "spatium.services.deployment.asyncio.create_subprocess_exec", new=AsyncMock()
            ) as mock_subprocess,
            patch("spatium.services.deployment.yaml.dump"),
            patch("builtins.open", MagicMock()),
            patch("spatium.services.deployment.shutil.which", return_value="/usr/bin/containerlab"),
        ):
            # Set up mock process that fails
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate.return_value = (b"", b"Deployment failed")
            mock_subprocess.return_value = mock_process

            # Create deployer and deploy topology
            deployer = ContainerLabDeploymentService()

            # Create a valid topology config
            topology_config = TopologyConfig(
                name="test-topo",
                nodes=[NodeConfig(name="sonic1", type="sonic-vs", image="sonic:latest")],
                links=[],
            )

            result = await deployer.deploy_topology(topology_config)

            # Check result indicates failure
            assert result.success is False
            assert result.error is not None

    @pytest.mark.asyncio
    async def test_destroy_topology(self):
        """Test topology destruction."""
        # Create deployer with mocked subprocess
        with (
            patch(
                "spatium.services.deployment.asyncio.create_subprocess_exec", new=AsyncMock()
            ) as mock_subprocess,
            patch("spatium.services.deployment.shutil.which", return_value="/usr/bin/containerlab"),
        ):
            # Set up mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"Destroyed successfully", b"")
            mock_subprocess.return_value = mock_process

            # Create deployer and destroy topology
            deployer = ContainerLabDeploymentService()
            result = await deployer.destroy_topology("test-topo")

            # Check subprocess was called with correct args
            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0]
            assert args[0] == "containerlab"
            assert args[1] == "destroy"
            assert args[2] == "-t"

            # Check result
            assert result.success is True
            assert result.topology_name == "test-topo"

    @pytest.mark.asyncio
    async def test_list_deployments(self):
        """Test listing deployments."""
        # Create deployer with mocked subprocess
        with (
            patch(
                "spatium.services.deployment.asyncio.create_subprocess_exec", new=AsyncMock()
            ) as mock_subprocess,
            patch("spatium.services.deployment.shutil.which", return_value="/usr/bin/containerlab"),
        ):
            # Set up mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"List of deployments", b"")
            mock_subprocess.return_value = mock_process

            # Create deployer and list deployments
            deployer = ContainerLabDeploymentService()
            result = await deployer.list_deployments()

            # Check subprocess was called with correct args
            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0]
            assert args[0] == "containerlab"
            assert args[1] == "inspect"
            assert args[2] == "--all"  # Check result
        assert result["success"] is True
        assert "deployments" in result
        assert "count" in result
        assert result["count"] >= 0
