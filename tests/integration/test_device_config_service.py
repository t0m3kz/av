"""
Integration tests for device configuration service with REST and SSH support.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from spatium.models.device import DeviceConfigRequest
from spatium.services.device_config import DeviceConfigService


class TestDeviceConfigServiceIntegration:
    """Integration tests for device configuration service."""

    @pytest.fixture
    def mock_ssh_client_factory(self):
        """Create a mock SSH client factory."""

        def factory(**kwargs):
            client = MagicMock()
            client.get_config = AsyncMock()
            client.test_connection = AsyncMock()
            return client

        return factory

    @pytest.fixture
    def mock_rest_client_factory(self):
        """Create a mock REST client factory."""

        def factory(**kwargs):
            client = MagicMock()
            client.get_config = AsyncMock()
            client.get_config_custom = AsyncMock()
            client.test_connection = AsyncMock()
            return client

        return factory

    @pytest.fixture
    def config_service(self, mock_ssh_client_factory, mock_rest_client_factory):
        """Create device configuration service with mocked clients."""
        return DeviceConfigService(mock_ssh_client_factory, mock_rest_client_factory)

    @pytest.mark.asyncio
    async def test_fetch_config_ssh_success(self, config_service, mock_ssh_client_factory):
        """Test successful SSH configuration retrieval."""
        # Setup
        device = DeviceConfigRequest(
            host="test-device",
            username="admin",
            password="password",
            method="ssh",
            device_model="sonic",
        )

        expected_config = {
            "host": "test-device",
            "running_config": "interface Ethernet0\n description test",
            "version_info": "SONiC v1.0",
            "interfaces": "Ethernet0: up",
            "source": "ssh",
            "error": None,
        }

        # Mock SSH client response
        ssh_client = mock_ssh_client_factory()
        ssh_client.get_config.return_value = expected_config
        config_service.ssh_client_factory = lambda **kwargs: ssh_client

        # Execute
        result = await config_service.fetch_config(device)

        # Verify
        assert result.host == "test-device"
        assert result.running_config == "interface Ethernet0\n description test"
        assert result.source == "ssh"
        assert result.error is None
        ssh_client.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_config_rest_success(self, config_service, mock_rest_client_factory):
        """Test successful REST configuration retrieval."""
        # Setup
        device = DeviceConfigRequest(
            host="test-device",
            username="admin",
            password="password",
            method="rest",
            device_model="sonic",
            port=8080,
        )

        config_data = {"PORT": {"Ethernet0": {"alias": "eth0"}}}

        # Mock REST client response
        rest_client = mock_rest_client_factory()
        rest_client.get_config.return_value = config_data
        config_service.rest_client_factory = lambda **kwargs: rest_client

        # Execute
        result = await config_service.fetch_config(device)

        # Verify
        assert result.host == "test-device"
        assert json.loads(result.running_config) == config_data
        assert result.source == "rest"
        assert result.error is None
        rest_client.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_config_rest_custom_url(self, config_service, mock_rest_client_factory):
        """Test REST configuration retrieval with custom URL."""
        # Setup
        device = DeviceConfigRequest(
            host="test-device",
            username="admin",
            password="password",
            method="rest",
            rest_url="/api/v1/custom-config",
        )

        config_data = {"custom": "configuration"}

        # Mock REST client response
        rest_client = mock_rest_client_factory()
        rest_client.get_config_custom.return_value = config_data
        config_service.rest_client_factory = lambda **kwargs: rest_client

        # Execute
        result = await config_service.fetch_config(device)

        # Verify
        assert result.host == "test-device"
        assert json.loads(result.running_config) == config_data
        assert result.source == "rest"
        assert result.error is None
        rest_client.get_config_custom.assert_called_once_with("/api/v1/custom-config")

    @pytest.mark.asyncio
    async def test_fetch_config_ssh_error(self, config_service, mock_ssh_client_factory):
        """Test SSH configuration retrieval with error."""
        # Setup
        device = DeviceConfigRequest(
            host="test-device", username="admin", password="password", method="ssh"
        )

        # Mock SSH client error
        ssh_client = mock_ssh_client_factory()
        ssh_client.get_config.side_effect = Exception("Connection timeout")
        config_service.ssh_client_factory = lambda **kwargs: ssh_client

        # Execute
        result = await config_service.fetch_config(device)

        # Verify
        assert result.host == "test-device"
        assert result.running_config is None
        assert result.source == "ssh"
        assert "Connection timeout" in result.error

    @pytest.mark.asyncio
    async def test_fetch_config_rest_error(self, config_service, mock_rest_client_factory):
        """Test REST configuration retrieval with error."""
        # Setup
        device = DeviceConfigRequest(
            host="test-device", username="admin", password="password", method="rest"
        )

        # Mock REST client error
        rest_client = mock_rest_client_factory()
        rest_client.get_config.side_effect = Exception("HTTP 404 Not Found")
        config_service.rest_client_factory = lambda **kwargs: rest_client

        # Execute
        result = await config_service.fetch_config(device)

        # Verify
        assert result.host == "test-device"
        assert result.running_config is None
        assert result.source == "rest"
        assert "HTTP 404 Not Found" in result.error

    @pytest.mark.asyncio
    async def test_fetch_configs_bulk_mixed_methods(
        self, config_service, mock_ssh_client_factory, mock_rest_client_factory
    ):
        """Test bulk configuration retrieval with mixed SSH and REST methods."""
        # Setup
        devices = [
            DeviceConfigRequest(
                host="ssh-device", username="admin", password="password", method="ssh"
            ),
            DeviceConfigRequest(
                host="rest-device", username="admin", password="password", method="rest"
            ),
        ]

        # Mock SSH client
        ssh_client = mock_ssh_client_factory()
        ssh_client.get_config.return_value = {
            "host": "ssh-device",
            "running_config": "ssh config data",
            "source": "ssh",
            "error": None,
        }

        # Mock REST client
        rest_client = mock_rest_client_factory()
        rest_client.get_config.return_value = {"rest": "config"}

        config_service.ssh_client_factory = lambda **kwargs: ssh_client
        config_service.rest_client_factory = lambda **kwargs: rest_client

        # Execute
        results = await config_service.fetch_configs_bulk(devices)

        # Verify
        assert len(results) == 2

        ssh_result = next(r for r in results if r.host == "ssh-device")
        assert ssh_result.source == "ssh"
        assert ssh_result.running_config == "ssh config data"
        assert ssh_result.error is None

        rest_result = next(r for r in results if r.host == "rest-device")
        assert rest_result.source == "rest"
        assert json.loads(rest_result.running_config) == {"rest": "config"}
        assert rest_result.error is None

    @pytest.mark.asyncio
    async def test_get_config_command(self, config_service):
        """Test getting configuration command for different device models."""
        # Test SONiC device
        cmd = config_service.get_config_command("sonic")
        assert cmd == "show running-configuration"

        # Test Arista device
        cmd = config_service.get_config_command("arista")
        assert cmd == "show running-config"

        # Test Cisco device
        cmd = config_service.get_config_command("cisco")
        assert cmd == "show running-config"

        # Test unknown device (should use default)
        cmd = config_service.get_config_command("unknown")
        assert cmd == "show running-configuration"

        # Test None device model (should use default)
        cmd = config_service.get_config_command(None)
        assert cmd == "show running-configuration"

    @pytest.mark.asyncio
    async def test_save_configs_to_files(self, config_service, mock_ssh_client_factory, tmp_path):
        """Test saving configurations to files."""
        # Setup
        devices = [
            DeviceConfigRequest(host="device1", username="admin", password="password", method="ssh")
        ]

        # Mock SSH client
        ssh_client = mock_ssh_client_factory()
        ssh_client.get_config.return_value = {
            "host": "device1",
            "running_config": "test configuration",
            "source": "ssh",
            "error": None,
        }
        config_service.ssh_client_factory = lambda **kwargs: ssh_client

        # Execute
        output_folder = str(tmp_path)
        results = await config_service.save_configs_to_files(devices, output_folder)

        # Verify
        assert len(results) == 1
        result = results[0]
        assert result.host == "device1"
        assert result.error is None
        assert result.file_path == f"{output_folder}/device1_config.txt"
        assert "saved to" in result.message

        # Verify file was created
        config_file = tmp_path / "device1_config.txt"
        assert config_file.exists()
        assert config_file.read_text() == "test configuration"
