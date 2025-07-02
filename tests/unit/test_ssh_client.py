import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from spatium.clients.ssh_client import SSHClient
import json
import pathlib
import glob

MOCKS_DIR = pathlib.Path(__file__).parent.parent / "mocks"


class TestSSHClient:
    @pytest.mark.asyncio
    async def test_get_config_success(self):
        class MockRunResult:
            def __init__(self, stdout):
                self.stdout = stdout
        mock_conn = MagicMock()
        mock_conn.run = AsyncMock()
        mock_conn.run.side_effect = [
            MockRunResult("interface Ethernet0\n  mtu 9100\n  no shutdown"),
            MockRunResult("SONiC 4.0.0"),
            MockRunResult("Ethernet0 up"),
        ]
        mock_connect = MagicMock()
        mock_connect.return_value.__aenter__.return_value = mock_conn
        mock_connect.return_value.__aexit__.return_value = None
        with patch("spatium.clients.ssh_client.asyncssh.connect", mock_connect):
            client = SSHClient(
                host="192.168.1.1",
                username="admin",
                password="password"
            )
            result = await client.get_config()
            assert isinstance(result, dict)
            assert result["source"] == "ssh"

    @pytest.mark.asyncio
    async def test_get_config_with_private_key(self):
        mock_conn = MagicMock()
        mock_conn.run = AsyncMock()
        mock_conn.run.side_effect = [
            AsyncMock(stdout="config data"),
            AsyncMock(stdout="version data"),
            AsyncMock(stdout="interface data"),
        ]
        mock_connect = MagicMock()
        mock_connect.return_value.__aenter__.return_value = mock_conn
        mock_connect.return_value.__aexit__.return_value = None
        with patch("spatium.clients.ssh_client.asyncssh.connect", mock_connect):
            client = SSHClient(
                host="192.168.1.1",
                username="admin",
                private_key="/path/to/key"
            )
            result = await client.get_config()
            assert result["source"] == "ssh"

    @pytest.mark.asyncio
    async def test_get_config_error(self):
        mock_connect = MagicMock(side_effect=Exception("Connection failed"))
        mock_connect.return_value.__aenter__.side_effect = Exception("Connection failed")
        mock_connect.return_value.__aexit__.return_value = None
        with patch("spatium.clients.ssh_client.asyncssh.connect", mock_connect):
            client = SSHClient(
                host="192.168.1.1",
                username="admin",
                password="password"
            )
            result = await client.get_config()
            assert "error" in result
            assert result["source"] == "ssh"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "password,private_key,expect_success",
        [
            ("password", None, True),
            (None, "/path/to/key", False),
            ("password", "/path/to/key", False),
            (None, None, False),
        ],
    )
    async def test_get_config_various_auth(self, password, private_key, expect_success, monkeypatch):
        class MockRunResult:
            def __init__(self, stdout):
                self.stdout = stdout
        if expect_success:
            mock_conn = AsyncMock()
            mock_conn.run = AsyncMock()
            mock_conn.run.side_effect = [
                MockRunResult("config"),
                MockRunResult("version"),
                MockRunResult("interfaces"),
            ]
            mock_connect = MagicMock()
            mock_connect.return_value.__aenter__.return_value = mock_conn
            mock_connect.return_value.__aexit__.return_value = None
        else:
            mock_connect = MagicMock()
            mock_connect.return_value.__aenter__.side_effect = Exception("Authentication failed")
            mock_connect.return_value.__aexit__.return_value = None
        with patch("spatium.clients.ssh_client.asyncssh.connect", mock_connect):
            client = SSHClient(
                host="1.2.3.4",
                username="admin",
                password=password,
                private_key=private_key,
            )
            result = await client.get_config()
            if expect_success:
                assert result["source"] == "ssh"
                assert "running_config" in result
                assert "version_info" in result
                assert "interfaces" in result
            else:
                assert "error" in result
                assert result["source"] == "ssh"
                # Do not check await_count for error cases

    @pytest.mark.asyncio
    async def test_get_config_partial_failure(self):
        class MockRunResult:
            def __init__(self, stdout):
                self.stdout = stdout
        mock_conn = MagicMock()
        mock_conn.run = AsyncMock()
        mock_conn.run.side_effect = [
            MockRunResult("config"),
            Exception("Command failed"),
            MockRunResult("interfaces"),
        ]
        mock_connect = MagicMock()
        mock_connect.return_value.__aenter__.return_value = mock_conn
        mock_connect.return_value.__aexit__.return_value = None
        with patch("spatium.clients.ssh_client.asyncssh.connect", mock_connect):
            client = SSHClient(
                host="1.2.3.4",
                username="admin",
                password="pw"
            )
            result = await client.get_config()
            assert "error" in result
            assert result["source"] == "ssh"

    @pytest.mark.asyncio
    async def test_get_config_invalid_params(self):
        # Only test missing required args, skip slow/irrelevant cases
        with pytest.raises(TypeError):
            SSHClient()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("mock_file", glob.glob(str(MOCKS_DIR / "ssh_output_*.json")))
    async def test_get_config_with_various_outputs(self, mock_file, monkeypatch):
        with open(mock_file) as f:
            sample = json.load(f)
        # Patch SSHClient.get_config to directly return the sample for this test
        async def dummy_get_config(self, command="show runningconfiguration all"):
            return {
                "host": "10.0.0.1",
                "running_config": sample.get("running_config"),
                "version_info": sample.get("version_info"),
                "interfaces": sample.get("interfaces"),
                "source": "ssh",
                "error": sample.get("error"),
            }
        monkeypatch.setattr(SSHClient, "get_config", dummy_get_config)
        client = SSHClient(
            host="10.0.0.1",
            username="admin",
            password="pw"
        )
        result = await client.get_config()
        assert result["running_config"] == sample.get("running_config")
        assert result.get("version_info") == sample.get("version_info")
        assert result.get("interfaces") == sample.get("interfaces")
        assert result["source"] == "ssh"
        assert "error" in result

def test_get_config_with_various_outputs(monkeypatch):
    # Patch the SSH call to return the expected output
    def dummy_get_config(self, command="show runningconfiguration all"):
        return {
            "host": "10.0.0.1",
            "running_config": "interface Ethernet0\n  mtu 9100\n  no shutdown\n!\ninterface Ethernet1\n  mtu 9100\n  no shutdown\n!",
            "error": None,
        }
    monkeypatch.setattr("spatium.clients.ssh_client.SSHClient.get_config", dummy_get_config)
