import pytest
from fastapi.testclient import TestClient
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from main import app

# Add the project root to the path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock pybatfish before importing anything that depends on it
sys.modules["pybatfish"] = MagicMock()
sys.modules["pybatfish.client"] = MagicMock()
sys.modules["pybatfish.client.commands"] = MagicMock()
sys.modules["pybatfish.question"] = MagicMock()

# Now import the app


@pytest.fixture
def client():
    """
    Test client for the FastAPI application
    """
    return TestClient(app)


@pytest.fixture
def mock_ssh_client():
    """
    Mock for the SSH client
    """
    with patch("spatium.device_config.ssh_client.SSHClient") as mock:
        instance = mock.return_value
        instance.get_config.return_value = {
            "running_config": "interface Ethernet0\n  mtu 9100\n  no shutdown",
            "version_info": "SONiC 4.0.0",
            "interfaces": "Ethernet0 up",
            "source": "ssh",
        }
        yield instance


@pytest.fixture
def mock_gnmi_client():
    """
    Mock for the gNMI client
    """
    with patch("spatium.device_config.gnmi_client.SonicGNMIClient") as mock:
        instance = mock.return_value
        instance.get_config.return_value = {
            "gnmi_data": {"path": "openconfig-interfaces:interfaces", "data": {}},
            "source": "gnmi",
        }
        yield instance


@pytest.fixture
def mock_batfish_analyzer():
    """
    Mock for the Batfish analyzer
    """
    with patch("spatium.analysis.batfish_analyzer.analyze_config_with_batfish") as mock:
        mock.return_value = {
            "interfaces": [{"Interface": "Ethernet0", "VRF": "default"}],
            "ip_owners": [{"IP": "192.168.1.1", "Interface": "Ethernet0"}],
            "routes": [],
            "layer3_topology": [],
            "undefined_references": [],
        }
        yield mock


@pytest.fixture
def mock_containerlab_deployer():
    """
    Mock for the ContainerLab deployer
    """
    with patch("spatium.deployment.containerlab.ContainerLabDeployer") as mock:
        instance = mock.return_value
        instance.create_sonic_topology.return_value = {
            "name": "test-topo",
            "prefix": "spatium-test-topo",
            "topology": {
                "nodes": {
                    "sonic1": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"}
                },
                "links": [],
            },
        }
        instance.deploy_topology.return_value = {
            "success": True,
            "topology_name": "test-topo",
            "topology_file": "/tmp/test-topo.yaml",
            "output": "Deployed topology",
        }
        instance.destroy_topology.return_value = {
            "success": True,
            "topology_name": "test-topo",
            "output": "Destroyed topology",
        }
        instance.list_deployments.return_value = {
            "success": True,
            "output": "List of deployments",
        }
        yield instance


@pytest.fixture(autouse=True, scope="session")
def patch_asyncssh_connect():
    import spatium.device_config.ssh_client

    # Patch asyncssh.connect globally for all tests
    with patch("asyncssh.connect", new_callable=AsyncMock) as mock_connect:
        yield mock_connect
