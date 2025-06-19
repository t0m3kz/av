import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from spatium.deployment.containerlab import ContainerLabDeployer

class TestContainerLabDeployer:
    def test_create_sonic_topology(self):
        deployer = ContainerLabDeployer()
        
        # Test data
        nodes = [
            {"name": "sonic1", "type": "sonic-vs", "image": "sonic:latest"},
            {"name": "sonic2", "type": "sonic-vs", "image": "sonic:latest"}
        ]
        
        links = [
            {"node1": "sonic1", "interface1": "eth1", "node2": "sonic2", "interface2": "eth1"}
        ]
        
        # Create topology
        topology = deployer.create_sonic_topology("test-topo", nodes, links)
        
        # Check topology structure
        assert topology["name"] == "test-topo"
        assert topology["prefix"] == "spatium-test-topo"
        assert "mgmt" in topology
        assert "topology" in topology
        
        # Check nodes
        assert "sonic1" in topology["topology"]["nodes"]
        assert "sonic2" in topology["topology"]["nodes"]
        assert topology["topology"]["nodes"]["sonic1"]["kind"] == "sonic-vs"
        assert topology["topology"]["nodes"]["sonic1"]["image"] == "sonic:latest"
        
        # Check links
        assert len(topology["topology"]["links"]) == 1
        assert topology["topology"]["links"][0] == ["sonic1eth1", "sonic2eth1"]
    
    @pytest.mark.asyncio
    async def test_deploy_topology_success(self):
        # Create deployer with mocked subprocess
        with patch("spatium.deployment.containerlab.asyncio.create_subprocess_exec", new=AsyncMock()) as mock_subprocess, \
             patch("spatium.deployment.containerlab.yaml.dump") as mock_yaml_dump, \
             patch("builtins.open", MagicMock()):
            
            # Set up mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"Deployed successfully", b"")
            mock_subprocess.return_value = mock_process
            
            # Create deployer and deploy topology
            deployer = ContainerLabDeployer()
            topology = {"name": "test-topo", "topology": {"nodes": {}, "links": []}}
            result = await deployer.deploy_topology(topology)
            
            # Check yaml was dumped
            mock_yaml_dump.assert_called_once()
            
            # Check subprocess was called with correct args
            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0]
            assert args[0] == "containerlab"
            assert args[1] == "deploy"
            assert args[2] == "-t"
            
            # Check result
            assert result["success"] is True
            assert result["topology_name"] == "test-topo"
            assert "output" in result
    
    @pytest.mark.asyncio
    async def test_deploy_topology_failure(self):
        # Create deployer with mocked subprocess
        with patch("spatium.deployment.containerlab.asyncio.create_subprocess_exec", new=AsyncMock()) as mock_subprocess, \
             patch("spatium.deployment.containerlab.yaml.dump"), \
             patch("builtins.open", MagicMock()):
            
            # Set up mock process that fails
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate.return_value = (b"", b"Deployment failed")
            mock_subprocess.return_value = mock_process
            
            # Create deployer and deploy topology
            deployer = ContainerLabDeployer()
            topology = {"name": "test-topo", "topology": {"nodes": {}, "links": []}}
            result = await deployer.deploy_topology(topology)
            
            # Check result indicates failure
            assert result["success"] is False
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_destroy_topology(self):
        # Create deployer with mocked subprocess
        with patch("spatium.deployment.containerlab.asyncio.create_subprocess_exec", new=AsyncMock()) as mock_subprocess, \
             patch("spatium.deployment.containerlab.os.path.exists", return_value=True):
            
            # Set up mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"Destroyed successfully", b"")
            mock_subprocess.return_value = mock_process
            
            # Create deployer and destroy topology
            deployer = ContainerLabDeployer()
            result = await deployer.destroy_topology("test-topo")
            
            # Check subprocess was called with correct args
            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0]
            assert args[0] == "containerlab"
            assert args[1] == "destroy"
            assert args[2] == "-t"
            
            # Check result
            assert result["success"] is True
            assert result["topology_name"] == "test-topo"
    
    @pytest.mark.asyncio
    async def test_list_deployments(self):
        # Create deployer with mocked subprocess
        with patch("spatium.deployment.containerlab.asyncio.create_subprocess_exec", new=AsyncMock()) as mock_subprocess:
            
            # Set up mock process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"List of deployments", b"")
            mock_subprocess.return_value = mock_process
            
            # Create deployer and list deployments
            deployer = ContainerLabDeployer()
            result = await deployer.list_deployments()
            
            # Check subprocess was called with correct args
            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0]
            assert args[0] == "containerlab"
            assert args[1] == "inspect"
            assert args[2] == "--all"
            
            # Check result
            assert result["success"] is True
            assert result["output"] == "List of deployments"