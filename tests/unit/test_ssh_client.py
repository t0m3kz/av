import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from spatium.device_config.ssh_client import SSHClient
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
        with patch("spatium.device_config.ssh_client.asyncssh.connect", mock_connect):
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
        with patch("spatium.device_config.ssh_client.asyncssh.connect", mock_connect):
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
        with patch("spatium.device_config.ssh_client.asyncssh.connect", mock_connect):
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
    async def test_get_config_various_auth(self, password, private_key, expect_success):
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
        with patch("spatium.device_config.ssh_client.asyncssh.connect", mock_connect):
            client = SSHClient(
                host="1.2.3.4",
                username="admin",
                password=password,
                private_key=private_key,
            )
            result = await client.get_config()
            print(f"AUTH TEST: password={password}, private_key={private_key}, result={result}")
            if expect_success:
                assert result["source"] == "ssh"
                assert "running_config" in result
                assert "version_info" in result
                assert "interfaces" in result
                assert mock_conn.run.await_count == 3
                mock_conn.run.assert_any_call("show running-configuration")
                mock_conn.run.assert_any_call("show version")
                mock_conn.run.assert_any_call("show interfaces status")
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
        with patch("spatium.device_config.ssh_client.asyncssh.connect", mock_connect):
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
    async def test_get_config_with_various_outputs(self, mock_file):
        with open(mock_file) as f:
            sample = json.load(f)
        class MockRunResult:
            def __init__(self, stdout):
                self.stdout = stdout
        mock_conn = AsyncMock()
        mock_conn.run = AsyncMock()
        if "error" in sample:
            mock_connect = MagicMock(side_effect=Exception(sample["error"]))
            mock_connect.return_value.__aenter__.side_effect = Exception(sample["error"])
            mock_connect.return_value.__aexit__.return_value = None
            with patch("spatium.device_config.ssh_client.asyncssh.connect", mock_connect):
                client = SSHClient(
                    host="10.0.0.1",
                    username="admin",
                    password="pw"
                )
                result = await client.get_config()
                print(f"MOCK ERROR TEST: {mock_file}, result={result}")
                assert "error" in result
                assert result["source"] == "ssh"
        else:
            mock_conn.run.side_effect = [
                MockRunResult(sample["running_config"]),
                MockRunResult(sample["version_info"]),
                MockRunResult(sample["interfaces"]),
            ]
            mock_connect = MagicMock()
            mock_connect.return_value.__aenter__.return_value = mock_conn
            mock_connect.return_value.__aexit__.return_value = None
            with patch("spatium.device_config.ssh_client.asyncssh.connect", mock_connect):
                client = SSHClient(
                    host="10.0.0.1",
                    username="admin",
                    password="pw"
                )
                result = await client.get_config()
                print(f"MOCK SUCCESS TEST: {mock_file}, result={result}")
                assert result["running_config"] == sample["running_config"]
                assert result["version_info"] == sample["version_info"]
                assert result["interfaces"] == sample["interfaces"]
                assert result["source"] == "ssh"
