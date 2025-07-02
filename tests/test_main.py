from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest

from spatium.main import app
from spatium.services.inventory import InventoryService


@pytest.fixture(autouse=True)
def clear_inventory():
    # Clear all inventories from the singleton service
    service = InventoryService()
    for inventory_name in list(service._inventories.keys()):
        service.clear_inventory(inventory_name)
    yield
    # Clear again after test
    for inventory_name in list(service._inventories.keys()):
        service.clear_inventory(inventory_name)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def mock_clab_api():
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "spatium-inventory-topo",
            "nodes": {},
            "links": [],
        }
        mock_post.return_value = mock_response
        yield mock_post


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()

    # More flexible assertion to handle different response formats
    assert isinstance(data, dict), "Response is not a dictionary"

    # Check for name or message
    assert any(key in data for key in ["name", "message"]), (
        "Response missing 'name' or 'message' field"
    )

    # Check for version or other fields if present
    if "version" in data:
        assert isinstance(data["version"], str), "Version is not a string"


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "Spatium"
    assert "version" in data
    assert "description" in data


def test_about_route(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"].lower() == "spatium"
    assert "version" in data
    assert "description" in data


def test_bulk_add_devices(client):
    devices = [
        {
            "host": f"10.0.1.{i}",
            "username": "admin",
            "password": "pw",
            "port": 22,
            "device_model": "sonic",
        }
        for i in range(1, 4)
    ]
    resp = client.post(
        "/topology/inventory/add", params={"inventory": "testtopo_main"}, json=devices
    )
    assert resp.status_code == 200
    assert resp.json()["success"]
    assert len(resp.json()["affected_hosts"]) == 3

    resp = client.get("/topology/inventory/list", params={"inventory": "testtopo_main"})
    hosts = [d["host"] for d in resp.json()]
    for i in range(1, 4):
        assert f"10.0.1.{i}" in hosts


def test_deploy_containerlab_topology(client, mock_clab_api):
    # Add devices to topology
    devices = [
        {
            "host": f"10.0.0.{i}",
            "username": "admin",
            "password": "pass",
            "port": 22,
            "device_model": "sonic",
        }
        for i in range(1, 4)
    ]
    resp = client.post(
        "/topology/inventory/add", params={"inventory": "testtopo_deploy"}, json=devices
    )
    assert resp.status_code == 200

    # Deploy topology with links in {a, b} format
    links = [
        {"a": "10.0.0.1:eth1", "b": "10.0.0.2:eth1"},
        {"a": "10.0.0.2:eth2", "b": "10.0.0.3:eth1"},
    ]
    resp = client.post(
        "/devices/inventory/deploy-containerlab",
        params={"inventory": "testtopo_deploy"},
        json={"links": links},
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    # Check the new DeploymentResponse format
    assert data["success"] is True
    assert data["topology_name"] == "spatium-inventory-topo"
    assert data["error"] is None

    # Check that the topology sent to clab-api-server has the correct structure
    called_args, called_kwargs = mock_clab_api.call_args
    sent_topology = called_kwargs["json"]
    assert "topology" in sent_topology
    assert "nodes" in sent_topology["topology"]
    assert "links" in sent_topology["topology"]

    # Each link should be a dict with 'endpoints' key
    for link in sent_topology["topology"]["links"]:
        assert "endpoints" in link
        assert isinstance(link["endpoints"], list)

    # Deploy topology with links in {endpoints: [...]} format
    links2 = [
        {"endpoints": ["10.0.0.1:eth3", "10.0.0.2:eth4"]},
        {"endpoints": ["10.0.0.2:eth5", "10.0.0.3:eth6"]},
    ]
    resp2 = client.post(
        "/devices/inventory/deploy-containerlab",
        params={"inventory": "testtopo_deploy"},
        json={"links": links2},
    )
    assert resp2.status_code in (200, 201)
    data2 = resp2.json()
    assert data2["success"] is True
    called_args2, called_kwargs2 = mock_clab_api.call_args
    sent_topology2 = called_kwargs2["json"]
    for link in sent_topology2["topology"]["links"]:
        assert "endpoints" in link
        assert isinstance(link["endpoints"], list)
