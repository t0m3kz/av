import json
import pathlib
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from fastapi.testclient import TestClient
from spatium.api.device import router, get_ssh_client_factory
import types

# Load all mock outputs once for the class
MOCKS_DIR = pathlib.Path(__file__).parent.parent / "mocks"
MOCK_OUTPUTS = {
    fname: json.load(open(MOCKS_DIR / fname))
    for fname in ["ssh_output_1.json", "ssh_output_2.json", "ssh_output_error.json"]
}

def get_sample_output(filename):
    return MOCK_OUTPUTS[filename]

class MockSSHClient:
    def __init__(self, host, username, password=None, private_key=None, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.private_key = private_key
        self.port = port
        self._sample = None
    async def get_config(self):
        return self._sample

def get_mock_ssh_client_factory(sample):
    def factory(**kwargs):
        client = MockSSHClient(**kwargs)
        client._sample = sample
        return client
    return factory

class TestDeviceAPI:
    def test_get_device_config_ssh(self, client, monkeypatch):
        from main import app
        for mock_file in ["ssh_output_1.json", "ssh_output_2.json"]:
            sample = get_sample_output(mock_file)
            # Override dependency
            app.dependency_overrides[get_ssh_client_factory] = lambda: get_mock_ssh_client_factory(sample)
            data = {
                "host": "192.168.1.1",
                "username": "admin",
                "password": "password",
                "port": 22,
            }
            response = client.post("/device/configs", json=[data])
            assert response.status_code == 200
            response_data = response.json()[0]
            assert response_data["running_config"] == sample["running_config"]
            assert response_data["version_info"] == sample["version_info"]
            assert response_data["interfaces"] == sample["interfaces"]
            assert response_data["source"] == "ssh"
        app.dependency_overrides = {}

    def test_get_device_config_ssh_error(self, client, monkeypatch):
        from main import app
        sample = get_sample_output("ssh_output_error.json")
        def error_factory(**kwargs):
            class ErrorClient:
                async def get_config(self):
                    return {
                        "error": sample["error"],
                        "source": "ssh",
                        "running_config": None,
                        "version_info": None,
                        "interfaces": None,
                    }
            return ErrorClient()
        app.dependency_overrides[get_ssh_client_factory] = lambda: error_factory
        data = {
            "host": "192.168.1.1",
            "username": "admin",
            "password": "wrongpw",
            "port": 22,
        }
        response = client.post("/device/configs", json=[data])
        assert response.status_code == 200
        response_data = response.json()[0]
        assert response_data["error"] == sample["error"]
        assert response_data["source"] == "ssh"
        assert "running_config" in response_data
        assert "version_info" in response_data
        assert "interfaces" in response_data
        assert response_data["running_config"] in (None, "")
        assert response_data["version_info"] in (None, "")
        assert response_data["interfaces"] in (None, "")
        app.dependency_overrides = {}
