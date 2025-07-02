"""
Unit tests for REST client functionality.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from spatium.clients.rest_client import RestClient, DeviceSpecificRestClient


class TestRestClient:
    """Test the generic REST client."""
    
    @pytest.fixture
    def rest_client(self):
        """Create a test REST client."""
        return RestClient(
            host="test-device",
            username="admin",
            password="password",
            port=8080,
            timeout=10
        )
    
    @pytest.mark.asyncio
    async def test_get_config_success(self, rest_client):
        """Test successful get_config request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"config": "test"}
        mock_response.text = '{"config": "test"}'

        with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
            result = await rest_client.get_config("/api/config")

            assert result["running_config"] == '{\n  "config": "test"\n}'
            assert result["host"] == "test-device"
            assert result["source"] == "rest"
            assert result["error"] is None
            mock_get.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_config_http_error(self, rest_client):
        """Test get_config request with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_response
            )
            
            result = await rest_client.get_config("/api/nonexistent")
            
            assert result["error"] is not None
            assert "HTTP 404" in result["error"]
            assert result["running_config"] is None
    
    @pytest.mark.asyncio
    async def test_get_config_connection_error(self, rest_client):
        """Test get_config request with connection error."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            
            result = await rest_client.get_config("/api/config")
            
            assert result["error"] is not None
            assert "Connection failed" in result["error"]
            assert result["running_config"] is None
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, rest_client):
        """Test successful connection test."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await rest_client.test_connection()
            assert result["success"] is True
            assert result["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, rest_client):
        """Test failed connection test."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            
            result = await rest_client.test_connection()
            assert result["success"] is False
            assert "error" in result


class TestDeviceSpecificRestClient:
    """Test the device-specific REST client."""
    
    @pytest.fixture
    def device_client(self):
        """Create a test device REST client."""
        return DeviceSpecificRestClient(
            device_type="sonic",
            host="sonic-device",
            username="admin",
            password="password",
            port=8080
        )
    
    @pytest.mark.asyncio
    async def test_get_config_sonic(self, device_client):
        """Test getting configuration from SONiC device."""
        mock_config = {"PORT": {"Ethernet0": {"alias": "eth0"}}}
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_config
            mock_response.text = '{"PORT": {"Ethernet0": {"alias": "eth0"}}}'
            mock_get.return_value = mock_response
            
            result = await device_client.get_config()
            
            assert result["host"] == "sonic-device"
            assert '"PORT"' in result["running_config"]
            assert result["source"] == "rest"
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_get_config_arista(self):
        """Test getting configuration from Arista device."""
        client = DeviceSpecificRestClient(
            device_type="arista",
            host="arista-device",
            username="admin", 
            password="password",
            port=8080
        )
        
        mock_response_data = {
            "result": [{"output": "version 4.20.1F"}]
        }
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = await client.get_config()
            
            assert result["host"] == "arista-device"
            assert result["running_config"] == "version 4.20.1F"
            assert result["source"] == "rest"
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_get_config_cisco(self):
        """Test getting configuration from Cisco device."""
        client = DeviceSpecificRestClient(
            device_type="cisco",
            host="cisco-device",
            username="admin",
            password="password",
            port=8080
        )
        
        mock_config = {"cisco-ios:native": {}}
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_config
            mock_response.text = '{"cisco-ios:native": {}}'
            mock_get.return_value = mock_response
            
            result = await client.get_config()
            
            assert result["host"] == "cisco-device"
            assert '"cisco-ios:native"' in result["running_config"]
            assert result["source"] == "rest"
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_get_config_juniper(self):
        """Test getting configuration from Juniper device."""
        client = DeviceSpecificRestClient(
            device_type="juniper",
            host="juniper-device",
            username="admin",
            password="password",
            port=8080
        )
        
        mock_config = {"configuration": {}}
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_config
            mock_response.text = '{"configuration": {}}'
            mock_get.return_value = mock_response
            
            result = await client.get_config()
            
            assert result["host"] == "juniper-device"
            assert '"configuration"' in result["running_config"]
            assert result["source"] == "rest"
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_get_config_unknown_device(self):
        """Test getting configuration from unknown device type."""
        client = DeviceSpecificRestClient(
            device_type="unknown",
            host="unknown-device",
            username="admin",
            password="password",
            port=8080
        )
        
        mock_config = {"config": "data"}
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_config
            mock_response.text = '{"config": "data"}'
            mock_get.return_value = mock_response
            
            result = await client.get_config()
            
            assert result["host"] == "unknown-device"
            assert '"config"' in result["running_config"]
            assert result["source"] == "rest"
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_get_config_custom_url(self, device_client):
        """Test getting configuration with custom URL."""
        mock_config = {"custom": "config"}
        custom_url = "/api/v1/custom-config"
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_config
            mock_response.text = '{"custom": "config"}'
            mock_get.return_value = mock_response
            
            result = await device_client.get_config_custom(custom_url)
            
            assert result == mock_config
    
    @pytest.mark.asyncio
    async def test_auth_with_token(self):
        """Test authentication with API token."""
        client = DeviceSpecificRestClient(
            device_type="sonic",
            host="device",
            username="admin",
            password="password",
            port=8080,
            api_token="secret-token"
        )
        
        mock_config = {"config": "data"}
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_config
            mock_response.text = '{"config": "data"}'
            mock_get.return_value = mock_response
            
            result = await client.get_config()
            
            assert result["host"] == "device"
            assert '"config"' in result["running_config"]
            assert result["source"] == "rest"
            assert result["error"] is None
