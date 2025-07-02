"""Tests for device configuration router endpoints."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from spatium.api.dependencies import get_device_config_service, get_inventory_service
from spatium.api.responses import ConfigSaveResult, DeviceConfigResult
from spatium.main import app
from spatium.services.device_config import DeviceConfigService
from spatium.services.inventory import InventoryService


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_inventory_service():
    """Mock inventory service."""
    return MagicMock(spec=InventoryService)


@pytest.fixture
def mock_config_service():
    """Mock device config service."""
    return MagicMock(spec=DeviceConfigService)


class TestDeviceConfigRouter:
    """Test device configuration router endpoints."""

    def test_get_device_configs_success(self, client, mock_inventory_service, mock_config_service):
        """Test successful device config retrieval."""
        # Setup mocks
        mock_devices = [
            {"host": "10.0.0.1", "username": "admin", "password": "pass", "port": 22},
            {"host": "10.0.0.2", "username": "admin", "password": "pass", "port": 22},
        ]
        mock_inventory_service.get_inventory.return_value = mock_devices

        mock_config_service.fetch_configs_bulk.return_value = [
            DeviceConfigResult(host="10.0.0.1", running_config="config1", source="ssh", error=None),
            DeviceConfigResult(host="10.0.0.2", running_config="config2", source="ssh", error=None),
        ]

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/get?inventory=test")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 2
            assert data["inventory"] == "test"

        finally:
            app.dependency_overrides.clear()

    def test_get_device_configs_with_host_filter(
        self, client, mock_inventory_service, mock_config_service
    ):
        """Test device config retrieval with host filter."""
        # Setup mocks
        mock_device = [{"host": "10.0.0.1", "username": "admin", "password": "pass", "port": 22}]
        mock_inventory_service.filter_devices_by_host.return_value = mock_device

        mock_config_service.fetch_configs_bulk.return_value = [
            DeviceConfigResult(host="10.0.0.1", running_config="config1", source="ssh", error=None)
        ]

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/get?inventory=test&host=10.0.0.1")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 1
            assert data["results"][0]["host"] == "10.0.0.1"

        finally:
            app.dependency_overrides.clear()

    def test_get_device_configs_no_devices(
        self, client, mock_inventory_service, mock_config_service
    ):
        """Test config retrieval when no devices in inventory."""
        # Setup mocks
        mock_inventory_service.get_inventory.return_value = []

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/get?inventory=empty")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 0
            assert "No devices found" in data["message"]

        finally:
            app.dependency_overrides.clear()

    def test_get_device_configs_host_not_found(
        self, client, mock_inventory_service, mock_config_service
    ):
        """Test config retrieval when host filter returns no devices."""
        # Setup mocks
        mock_inventory_service.filter_devices_by_host.return_value = []

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/get?inventory=test&host=nonexistent")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 0
            assert "No device found with host 'nonexistent'" in data["message"]

        finally:
            app.dependency_overrides.clear()

    def test_get_device_configs_with_errors(
        self, client, mock_inventory_service, mock_config_service
    ):
        """Test config retrieval when some devices have errors."""
        # Setup mocks
        mock_devices = [
            {"host": "10.0.0.1", "username": "admin", "password": "pass", "port": 22},
            {"host": "10.0.0.2", "username": "admin", "password": "pass", "port": 22},
        ]
        mock_inventory_service.get_inventory.return_value = mock_devices

        mock_config_service.fetch_configs_bulk.return_value = [
            DeviceConfigResult(host="10.0.0.1", running_config="config1", source="ssh", error=None),
            DeviceConfigResult(
                host="10.0.0.2", running_config=None, source="ssh", error="Connection failed"
            ),
        ]

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/get?inventory=test")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 2
            # Check that errors are included
            error_result = next((r for r in data["results"] if r["host"] == "10.0.0.2"), None)
            assert error_result is not None
            assert error_result["error"] == "Connection failed"

        finally:
            app.dependency_overrides.clear()

    def test_get_device_configs_exception(
        self, client, mock_inventory_service, mock_config_service
    ):
        """Test exception handling in get_device_configs."""
        # Setup mocks to raise exception
        mock_inventory_service.get_inventory.side_effect = Exception("Test error")

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/get?inventory=test")

            assert response.status_code == 500

        finally:
            app.dependency_overrides.clear()

    def test_save_device_configs_success(self, client, mock_inventory_service, mock_config_service):
        """Test successful device config saving."""
        # Setup mocks
        mock_devices = [{"host": "10.0.0.1", "username": "admin", "password": "pass", "port": 22}]
        mock_inventory_service.get_inventory.return_value = mock_devices

        mock_config_service.save_configs_to_files.return_value = [
            ConfigSaveResult(
                host="10.0.0.1",
                source="ssh",
                error=None,
                message="Configuration saved successfully",
                file_path="/tmp/10.0.0.1_config.txt",
            )
        ]

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/save?inventory=test&output_folder=/tmp")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 1
            assert data["results"][0]["error"] is None

        finally:
            app.dependency_overrides.clear()

    def test_save_device_configs_no_devices(
        self, client, mock_inventory_service, mock_config_service
    ):
        """Test config saving when no devices in inventory."""
        # Setup mocks
        mock_inventory_service.get_inventory.return_value = []

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/save?inventory=empty&output_folder=/tmp")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 0
            assert "No devices found" in data["message"]

        finally:
            app.dependency_overrides.clear()

    def test_save_device_configs_with_host_filter(
        self, client, mock_inventory_service, mock_config_service
    ):
        """Test config saving with host filter."""
        # Setup mocks
        mock_device = [{"host": "10.0.0.1", "username": "admin", "password": "pass", "port": 22}]
        mock_inventory_service.filter_devices_by_host.return_value = mock_device

        mock_config_service.save_configs_to_files.return_value = [
            ConfigSaveResult(
                host="10.0.0.1",
                source="ssh",
                error=None,
                message="Configuration saved successfully",
                file_path="/tmp/10.0.0.1_config.txt",
            )
        ]

        # Override dependencies
        app.dependency_overrides[get_inventory_service] = lambda: mock_inventory_service
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            response = client.post("/configs/save?inventory=test&host=10.0.0.1&output_folder=/tmp")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 1

        finally:
            app.dependency_overrides.clear()

    def test_get_single_device_config_success(self, client, mock_config_service):
        """Test successful single device config retrieval."""
        # Setup mock
        mock_config_service.fetch_config.return_value = DeviceConfigResult(
            host="10.0.0.1", running_config="test config", source="ssh", error=None
        )

        # Override dependencies
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            device_request = {
                "host": "10.0.0.1",
                "username": "admin",
                "password": "pass",
                "port": 22,
                "method": "ssh",
            }

            response = client.post("/configs/device", json=device_request)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 1
            assert data["results"][0]["host"] == "10.0.0.1"

        finally:
            app.dependency_overrides.clear()

    def test_get_single_device_config_error(self, client, mock_config_service):
        """Test single device config retrieval with error."""
        # Setup mock
        mock_config_service.fetch_config.return_value = DeviceConfigResult(
            host="10.0.0.1", running_config=None, source="ssh", error="Connection failed"
        )

        # Override dependencies
        app.dependency_overrides[get_device_config_service] = lambda: mock_config_service

        try:
            device_request = {
                "host": "10.0.0.1",
                "username": "admin",
                "password": "pass",
                "port": 22,
                "method": "ssh",
            }

            response = client.post("/configs/device", json=device_request)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False  # Should be False when there's an error
            assert len(data["results"]) == 1
            assert data["results"][0]["error"] == "Connection failed"

        finally:
            app.dependency_overrides.clear()
