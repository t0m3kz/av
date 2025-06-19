from pygnmi.client import gNMIclient
from typing import Dict, Any, List, Optional

class SonicGNMIClient:
    """Client for retrieving configuration from SONiC devices via gNMI."""
    
    def get_config(self, 
                  host: str, 
                  username: str, 
                  password: str, 
                  port: int = 8080,
                  insecure: bool = True,
                  paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Retrieve configuration from a SONiC device using gNMI.
        
        Args:
            host: Device hostname or IP address
            username: gNMI username
            password: gNMI password
            port: gNMI port (default: 8080)
            insecure: Skip TLS verification (default: True)
            paths: List of gNMI paths to query (default: basic paths)
            
        Returns:
            Dictionary containing the device configuration
        """
        if paths is None:
            paths = [
                "/openconfig-interfaces:interfaces",
                "/sonic-device-metadata:sonic-device-metadata",
                "/sonic-port:sonic-port"
            ]
            
        try:
            with gNMIclient(
                target=(host, port),
                username=username,
                password=password,
                insecure=insecure
            ) as client:
                # Get configuration using gNMI get
                response = client.get(path=paths)
                
                return {
                    "gnmi_data": response,
                    "source": "gnmi"
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "source": "gnmi"
            }