import asyncssh
from typing import Dict, Any, Optional

class SonicSSHClient:
    """Client for retrieving configuration from SONiC devices via SSH."""
    
    async def get_config(self, 
                         host: str, 
                         username: str, 
                         password: Optional[str] = None, 
                         port: int = 22, 
                         private_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve configuration from a SONiC device using SSH.
        
        Args:
            host: Device hostname or IP address
            username: SSH username
            password: SSH password (if not using key-based auth)
            port: SSH port (default: 22)
            private_key: Path to private key file (if using key-based auth)
            
        Returns:
            Dictionary containing the device configuration
        """
        try:
            connect_kwargs = {
                "username": username,
                "port": port,
            }
            
            if password:
                connect_kwargs["password"] = password
            if private_key:
                connect_kwargs["client_keys"] = [private_key]
                
            async with asyncssh.connect(host, **connect_kwargs) as conn:
                # Get running configuration
                running_config_result = await conn.run("show running-configuration")
                
                # Get version information
                version_result = await conn.run("show version")
                
                # Get interface status
                interfaces_result = await conn.run("show interfaces status")
                
                return {
                    "running_config": running_config_result.stdout,
                    "version_info": version_result.stdout,
                    "interfaces": interfaces_result.stdout,
                    "source": "ssh"
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "source": "ssh"
            }