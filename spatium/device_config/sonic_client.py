from typing import Dict, Any, Optional, List, Literal
from .ssh_client import SonicSSHClient
from .gnmi_client import SonicGNMIClient

class SonicClient:
    """
    Client for retrieving configuration from SONiC devices using multiple methods.
    """
    
    def __init__(self):
        self.ssh_client = SonicSSHClient()
        self.gnmi_client = SonicGNMIClient()
        
    async def get_config(self,
                        host: str,
                        username: str,
                        password: str,
                        method: Literal["ssh", "gnmi", "both"] = "both",
                        ssh_port: int = 22,
                        gnmi_port: int = 8080,
                        private_key: Optional[str] = None,
                        gnmi_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Retrieve configuration from a SONiC device using the specified method(s).
        
        Args:
            host: Device hostname or IP address
            username: Username for authentication
            password: Password for authentication
            method: "ssh", "gnmi", or "both" (default)
            ssh_port: SSH port (default: 22)
            gnmi_port: gNMI port (default: 8080)
            private_key: Path to SSH private key file
            gnmi_paths: List of gNMI paths to query
            
        Returns:
            Dictionary containing the device configuration retrieved using the specified method(s)
        """
        result = {}
        
        if method in ["ssh", "both"]:
            ssh_config = await self.ssh_client.get_config(
                host=host,
                username=username,
                password=password,
                port=ssh_port,
                private_key=private_key
            )
            result["ssh"] = ssh_config
            
        if method in ["gnmi", "both"]:
            gnmi_config = self.gnmi_client.get_config(
                host=host,
                username=username,
                password=password,
                port=gnmi_port,
                paths=gnmi_paths
            )
            result["gnmi"] = gnmi_config
            
        return result