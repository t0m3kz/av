import json
import pathlib

from fastapi.testclient import TestClient
import pytest

from spatium.api.dependencies import get_inventory_service
from spatium.clients.ssh_client import SSHClient
from spatium.main import app

MOCKS_DIR = pathlib.Path(__file__).parent.parent / "mocks"


@pytest.fixture(autouse=True)
def clear_inventory():
    # Clear the singleton inventory service
    inventory_service = get_inventory_service()
    inventory_service._inventories.clear()
    yield
    inventory_service._inventories.clear()


def test_collect_configs_from_topology(monkeypatch, tmp_path):
    # Use mock SSH client
    from spatium.api.dependencies import get_ssh_client_factory

    sample = json.load((MOCKS_DIR / "ssh_output_1.json").open())

    class MockSSHClient:
        def __init__(self, **kwargs):
            self.host = kwargs["host"]

    def factory(**kwargs):
        return MockSSHClient(**kwargs)

    # Patch SSHClient.get_config method using monkeypatch to ensure restoration after test
    async def async_get_config(self, command="show runningconfiguration all"):
        return {"host": self.host, "running_config": sample["running_config"], "error": None}

    monkeypatch.setattr(SSHClient, "get_config", async_get_config)
    app.dependency_overrides = {}
    app.dependency_overrides[get_ssh_client_factory] = lambda: factory
    client = TestClient(app)
    # Add device to topology
    device = {
        "host": "10.0.0.10",
        "username": "admin",
        "password": "pw",
        "port": 22,
        "device_model": "sonic",
    }
    client.post("/topology/inventory/add?inventory=testtopo_collect", json=device)
    # Save configs
    output_folder = str(tmp_path)
    resp = client.post(f"/configs/save?inventory=testtopo_collect&output_folder={output_folder}")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    for result in data["results"]:
        assert "saved" in result["message"]
    # Check file written
    config_file = tmp_path / "10.0.0.10_config.txt"
    assert config_file.exists()
    with config_file.open() as f:
        content = f.read()
        assert sample["running_config"].strip() in content
    app.dependency_overrides = {}


def test_bulk_add_devices_to_topology(monkeypatch):
    from spatium.api.dependencies import get_ssh_client_factory

    sample = json.load((MOCKS_DIR / "ssh_output_1.json").open())

    class MockSSHClient:
        def __init__(self, **kwargs):
            self.host = kwargs["host"]

    def factory(**kwargs):
        return MockSSHClient(**kwargs)

    # Patch SSHClient.get_config method using monkeypatch to ensure restoration after test
    async def async_get_config(self, command="show runningconfiguration all"):
        return {"host": self.host, "running_config": sample["running_config"], "error": None}

    monkeypatch.setattr(SSHClient, "get_config", async_get_config)
    app.dependency_overrides = {}
    app.dependency_overrides[get_ssh_client_factory] = lambda: factory
    client = TestClient(app)
    topology = "testtopo_bulk"
    devices = [
        {
            "host": f"10.0.0.{i}",
            "username": "admin",
            "password": "pw",
            "port": 22,
            "device_model": "sonic",
        }
        for i in range(11, 14)
    ]
    client.post(f"/topology/inventory/add?inventory={topology}", json=devices)
    # Confirm all devices are present
    resp = client.get(f"/topology/inventory/list?inventory={topology}")
    hosts = [d["host"] for d in resp.json()]
    for i in range(11, 14):
        assert f"10.0.0.{i}" in hosts
    app.dependency_overrides = {}


def test_save_configs_returns_per_host_message(monkeypatch, tmp_path):
    # Use mock SSH client
    from spatium.api.dependencies import get_ssh_client_factory

    sample = json.load((MOCKS_DIR / "ssh_output_1.json").open())

    class MockSSHClient:
        def __init__(self, **kwargs):
            self.host = kwargs["host"]

    def factory(**kwargs):
        return MockSSHClient(**kwargs)

    # Patch SSHClient globally to ensure all code paths use the sync mock
    import spatium.clients.ssh_client

    spatium.clients.ssh_client.SSHClient = MockSSHClient

    async def async_get_config(self, command="show runningconfiguration all"):
        return {"host": self.host, "running_config": sample["running_config"], "error": None}

    monkeypatch.setattr(SSHClient, "get_config", async_get_config)
    app.dependency_overrides = {}
    app.dependency_overrides[get_ssh_client_factory] = lambda: factory
    # Add multiple devices to topology
    devices = [
        {
            "host": f"10.0.0.{i}",
            "username": "admin",
            "password": "pw",
            "port": 22,
            "device_model": "sonic",
        }
        for i in range(10, 13)
    ]
    client = TestClient(app)
    topology = "testtopo_save_config"
    client.post(f"/topology/inventory/add?inventory={topology}", json=devices)
    # Save configs
    output_folder = str(tmp_path)
    resp = client.post(f"/configs/save?inventory={topology}&output_folder={output_folder}")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    for i in range(10, 13):
        host = f"10.0.0.{i}"
        found = False
        for result in data["results"]:
            if result["host"] == host:
                assert (
                    f"Configuration for host {host} saved to {output_folder}/{host}_config.txt"
                    in result["message"]
                )
                found = True
        assert found, f"No result for host {host}"
    app.dependency_overrides = {}
