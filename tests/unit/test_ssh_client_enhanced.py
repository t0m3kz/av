"""Enhanced tests for SSH client covering edge cases and error scenarios."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from spatium.api.exceptions import ConfigurationError
from spatium.clients.ssh_client import SSHClient


class TestSSHClientEnhanced:
    """Enhanced test cases for SSH client functionality."""

    @pytest.fixture
    def ssh_client(self):
        """Create SSH client instance for testing."""
        return SSHClient(
            host="192.168.1.1",
            username="admin",
            password="password",
            port=22,
            timeout=30,
        )

    @pytest.fixture
    def ssh_client_with_key(self):
        """Create SSH client instance with private key authentication."""
        return SSHClient(
            host="192.168.1.1",
            username="admin",
            private_key="/path/to/key",
            port=2222,
            timeout=60,
        )

    @pytest.mark.asyncio
    async def test_test_connection_success(self, ssh_client):
        """Test successful SSH connection test."""
        with patch("asyncssh.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            result = await ssh_client.test_connection()

            assert result is True
            mock_connect.assert_called_once_with(
                "192.168.1.1",
                port=22,
                username="admin",
                password="password",
                client_keys=None,
                known_hosts=None,
                connect_timeout=30,
            )
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, ssh_client):
        """Test SSH connection test failure."""
        with patch("asyncssh.connect") as mock_connect:
            mock_connect.side_effect = Exception("Connection refused")

            result = await ssh_client.test_connection()

            assert result is False

    @pytest.mark.asyncio
    async def test_test_connection_with_private_key(self, ssh_client_with_key):
        """Test SSH connection test with private key authentication."""
        with patch("asyncssh.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            result = await ssh_client_with_key.test_connection()

            assert result is True
            mock_connect.assert_called_once_with(
                "192.168.1.1",
                port=2222,
                username="admin",
                password=None,
                client_keys=["/path/to/key"],
                known_hosts=None,
                connect_timeout=60,
            )

    @pytest.mark.asyncio
    async def test_execute_command_success(self, ssh_client):
        """Test successful command execution."""
        with patch("asyncssh.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_result = MagicMock()
            mock_result.stdout = "Configuration output\n"

            mock_conn.run = AsyncMock(return_value=mock_result)
            mock_connect.return_value = mock_conn

            result = await ssh_client.execute_command("show running-config")

            assert result == "Configuration output"
            mock_conn.run.assert_called_once_with("show running-config", timeout=30)
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_command_asyncssh_error(self, ssh_client):
        """Test command execution with AsyncSSH error."""
        with patch("asyncssh.connect") as mock_connect:
            mock_connect.side_effect = Exception("AsyncSSH connection error")

            with pytest.raises(ConfigurationError) as exc_info:
                await ssh_client.execute_command("show running-config")

            assert "Command execution error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_command_connection_established_but_run_fails(self, ssh_client):
        """Test command execution when connection succeeds but run fails."""
        with patch("asyncssh.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_conn.run = AsyncMock(side_effect=Exception("Command failed"))
            mock_connect.return_value = mock_conn

            with pytest.raises(ConfigurationError) as exc_info:
                await ssh_client.execute_command("show running-config")

            assert "Command execution error" in str(exc_info.value)
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_config_success_with_json_formatting(self, ssh_client):
        """Test successful config retrieval with JSON formatting."""
        config_json = {"PORT": {"Ethernet0": {"alias": "eth0"}}}
        config_str = json.dumps(config_json)

        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                config_str,  # main config command
                "SONiC version 1.0",  # version info
                "Interface Status\nEthernet0 up",  # interfaces info
            ]

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert result["error"] is None
            # Should be formatted JSON
            assert '"PORT"' in result["running_config"]
            assert result["version_info"] == "SONiC version 1.0"
            assert "Ethernet0" in result["interfaces"]

    @pytest.mark.asyncio
    async def test_get_config_empty_primary_command_fallback_to_sonic(self, ssh_client):
        """Test config retrieval when primary command returns empty, fallback to SONiC."""
        sonic_config = {"DEVICE_METADATA": {"localhost": {"hostname": "sonic"}}}

        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                "",  # empty primary config
                json.dumps(sonic_config),  # sonic fallback config
                "SONiC version 1.0",  # version info
                "Interface Status",  # interfaces info
            ]

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert result["error"] is None
            assert '"DEVICE_METADATA"' in result["running_config"]
            # Verify fallback command was called
            calls = mock_execute.call_args_list
            assert any("config_db.json" in str(call) for call in calls)

    @pytest.mark.asyncio
    async def test_get_config_empty_primary_and_fallback_fails(self, ssh_client):
        """Test config retrieval when both primary and fallback commands fail."""
        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                "",  # empty primary config
                Exception("Fallback command failed"),  # sonic fallback fails
                "Version info",  # version succeeds
                "Interface info",  # interfaces succeed
            ]

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert result["error"] is None
            assert result["running_config"] == ""  # Empty config

    @pytest.mark.asyncio
    async def test_get_config_non_json_config(self, ssh_client):
        """Test config retrieval with non-JSON configuration."""
        config_text = "!\n! Configuration\n!\ninterface Ethernet0\n  no shutdown\n!"

        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                config_text,  # main config command
                "Version info",  # version info
                "Interface info",  # interfaces info
            ]

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert result["error"] is None
            # Should remain as original text (not JSON formatted)
            assert result["running_config"] == config_text
            assert "interface Ethernet0" in result["running_config"]

    @pytest.mark.asyncio
    async def test_get_config_invalid_json(self, ssh_client):
        """Test config retrieval with invalid JSON that should remain as text."""
        invalid_json = '{"incomplete": json'

        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                invalid_json,  # invalid JSON config
                "Version info",  # version info
                "Interface info",  # interfaces info
            ]

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert result["error"] is None
            # Should remain as original text (not parsed)
            assert result["running_config"] == invalid_json

    @pytest.mark.asyncio
    async def test_get_config_version_info_fails(self, ssh_client):
        """Test config retrieval when version info fails."""
        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                "Configuration data",  # main config
                Exception("Version command failed"),  # version fails
                "Interface info",  # interfaces succeed
            ]

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert result["error"] is None
            assert result["running_config"] == "Configuration data"
            assert result["version_info"] is None
            assert result["interfaces"] == "Interface info"

    @pytest.mark.asyncio
    async def test_get_config_interfaces_info_fails(self, ssh_client):
        """Test config retrieval when interfaces info fails."""
        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                "Configuration data",  # main config
                "Version info",  # version succeeds
                Exception("Interfaces command failed"),  # interfaces fail
            ]

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert result["error"] is None
            assert result["running_config"] == "Configuration data"
            assert result["version_info"] == "Version info"
            assert result["interfaces"] is None

    @pytest.mark.asyncio
    async def test_get_config_all_additional_info_fails(self, ssh_client):
        """Test config retrieval when all additional info commands fail."""
        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                "Configuration data",  # main config succeeds
                Exception("Version failed"),  # version fails
                Exception("Interfaces failed"),  # interfaces fail
            ]

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert result["error"] is None
            assert result["running_config"] == "Configuration data"
            assert result["version_info"] is None
            assert result["interfaces"] is None

    @pytest.mark.asyncio
    async def test_get_config_main_command_fails(self, ssh_client):
        """Test config retrieval when main command fails completely."""
        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = Exception("Main command failed")

            result = await ssh_client.get_config("show running-configuration")

            assert result["host"] == "192.168.1.1"
            assert result["source"] == "ssh"
            assert "Main command failed" in result["error"]
            assert result["running_config"] is None
            assert result["version_info"] is None
            assert result["interfaces"] is None

    @pytest.mark.asyncio
    async def test_get_config_custom_command(self, ssh_client):
        """Test config retrieval with custom command."""
        with patch.object(ssh_client, "execute_command") as mock_execute:
            mock_execute.side_effect = [
                "Custom command output",  # custom config command
                "Version info",  # version info
                "Interface info",  # interfaces info
            ]

            result = await ssh_client.get_config("show configuration")

            assert result["running_config"] == "Custom command output"
            # Verify custom command was called
            mock_execute.assert_any_call("show configuration")

    @pytest.mark.asyncio
    async def test_different_timeout_values(self):
        """Test SSH client with different timeout values."""
        client_short_timeout = SSHClient(
            host="192.168.1.1",
            username="admin",
            password="password",
            timeout=5,
        )

        client_long_timeout = SSHClient(
            host="192.168.1.1",
            username="admin",
            password="password",
            timeout=120,
        )

        assert client_short_timeout.timeout == 5
        assert client_long_timeout.timeout == 120

    @pytest.mark.asyncio
    async def test_different_port_values(self):
        """Test SSH client with different port values."""
        client_custom_port = SSHClient(
            host="192.168.1.1",
            username="admin",
            password="password",
            port=2222,
        )

        assert client_custom_port.port == 2222

    @pytest.mark.asyncio
    async def test_client_initialization_with_all_parameters(self):
        """Test SSH client initialization with all parameters."""
        client = SSHClient(
            host="10.0.0.1",
            username="testuser",
            password="testpass",
            port=2222,
            private_key="/path/to/private/key",
            timeout=90,
        )

        assert client.host == "10.0.0.1"
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert client.port == 2222
        assert client.private_key == "/path/to/private/key"
        assert client.timeout == 90

    @pytest.mark.asyncio
    async def test_execute_command_with_different_timeouts(self, ssh_client):
        """Test command execution respects timeout settings."""
        ssh_client.timeout = 10

        with patch("asyncssh.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_result = MagicMock()
            mock_result.stdout = "Output\n"
            mock_conn.run = AsyncMock(return_value=mock_result)
            mock_connect.return_value = mock_conn

            await ssh_client.execute_command("show running-config")

            # Verify timeout was passed to run command
            mock_conn.run.assert_called_once_with("show running-config", timeout=10)
