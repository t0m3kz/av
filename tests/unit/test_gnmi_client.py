from unittest.mock import patch, MagicMock
from spatium.device_config.gnmi_client import SonicGNMIClient

class TestSonicGNMIClient:
    def test_get_config_success(self):
        # Mock for the gNMIclient context manager
        mock_client = MagicMock()
        mock_client.get.return_value = {
            "notification": [
                {
                    "update": [
                        {
                            "path": "openconfig-interfaces:interfaces",
                            "val": {"interfaces": {}}
                        }
                    ]
                }
            ]
        }
        
        # Mock for the gNMIclient constructor
        with patch("spatium.device_config.gnmi_client.gNMIclient") as mock_gnmi:
            mock_gnmi.return_value.__enter__.return_value = mock_client
            
            # Create client and call get_config
            client = SonicGNMIClient()
            result = client.get_config(
                host="192.168.1.1",
                username="admin",
                password="password"
            )
            
            # Check that gNMIclient was called with the correct arguments
            mock_gnmi.assert_called_once_with(
                target=("192.168.1.1", 8080),
                username="admin",
                password="password",
                insecure=True
            )
            
            # Check that the get method was called with the default paths
            default_paths = [
                "/openconfig-interfaces:interfaces",
                "/sonic-device-metadata:sonic-device-metadata",
                "/sonic-port:sonic-port"
            ]
            mock_client.get.assert_called_once_with(path=default_paths)
            
            # Check the result
            assert result["source"] == "gnmi"
            assert "gnmi_data" in result
    
    def test_get_config_with_custom_paths(self):
        # Mock for the gNMIclient context manager
        mock_client = MagicMock()
        mock_client.get.return_value = {"notification": []}
        
        # Mock for the gNMIclient constructor
        with patch("spatium.device_config.gnmi_client.gNMIclient") as mock_gnmi:
            mock_gnmi.return_value.__enter__.return_value = mock_client
            
            # Custom paths
            custom_paths = ["/custom/path"]
            
            # Create client and call get_config with custom paths
            client = SonicGNMIClient()
            result = client.get_config(
                host="192.168.1.1",
                username="admin",
                password="password",
                paths=custom_paths
            )
            
            # Check that the get method was called with the custom paths
            mock_client.get.assert_called_once_with(path=custom_paths)
            
            # Check the result
            assert result["source"] == "gnmi"
    
    def test_get_config_error(self):
        # Mock for the gNMIclient constructor that raises an error
        with patch("spatium.device_config.gnmi_client.gNMIclient") as mock_gnmi:
            mock_gnmi.side_effect = Exception("Connection failed")
            
            # Create client and call get_config
            client = SonicGNMIClient()
            result = client.get_config(
                host="192.168.1.1",
                username="admin",
                password="password"
            )
            
            # Check the result contains the error
            assert result["error"] == "Connection failed"
            assert result["source"] == "gnmi"