import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
from spatium.device_config.ssh_client import SonicSSHClient
# Mock asyncssh module
sys.modules['asyncssh'] = MagicMock()



class TestSonicSSHClient:
    @pytest.mark.asyncio
    async def test_get_config_success(self):
        # Create a simple mock that mimics the behavior we need
        class MockRunResult:
            def __init__(self, stdout):
                self.stdout = stdout
        
        # Create a mock connection
        mock_conn = MagicMock()
        # Use AsyncMock for async methods
        mock_conn.run = AsyncMock()
        
        # Set up different return values for each call
        mock_conn.run.side_effect = [
            MockRunResult("interface Ethernet0\n  mtu 9100\n  no shutdown"),
            MockRunResult("SONiC 4.0.0"),
            MockRunResult("Ethernet0 up")
        ]
        
        # Mock context manager for asyncssh.connect
        mock_connect = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_conn
        
        # Mock the asyncssh.connect function
        with patch('asyncssh.connect', mock_connect):
            # Create client and call get_config
            client = SonicSSHClient()
            result = await client.get_config(
                host="192.168.1.1",
                username="admin",
                password="password"
            )
            
            # Basic assertions
            assert isinstance(result, dict), "Result should be a dictionary"
            assert "source" in result, "Result missing 'source' key"
            assert result["source"] == "ssh", "Source should be 'ssh'"
    
    @pytest.mark.asyncio
    async def test_get_config_with_private_key(self):
        # Same mock setup as above but simplified
        mock_conn = MagicMock()
        mock_conn.run = AsyncMock()
        mock_conn.run.side_effect = [
            AsyncMock(stdout="config data"),
            AsyncMock(stdout="version data"),
            AsyncMock(stdout="interface data")
        ]
        
        mock_connect = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_conn
        
        with patch('asyncssh.connect', mock_connect):
            client = SonicSSHClient()
            result = await client.get_config(
                host="192.168.1.1",
                username="admin",
                private_key="/path/to/key"
            )
            
            # Basic assertion
            assert "source" in result, "Result missing 'source' key"
            assert result["source"] == "ssh", "Source should be 'ssh'"
    
    @pytest.mark.asyncio
    async def test_get_config_error(self):
        # Mock for asyncssh.connect that raises an error
        mock_connect = AsyncMock(side_effect=Exception("Connection failed"))
        
        with patch('asyncssh.connect', mock_connect):
            # Create client and call get_config
            client = SonicSSHClient()
            result = await client.get_config(
                host="192.168.1.1",
                username="admin",
                password="password"
            )
            
            # Check the result contains the error
            assert "error" in result, "Result missing 'error' key"
            assert "source" in result, "Result missing 'source' key"
            assert result["source"] == "ssh", "Source should be 'ssh'"