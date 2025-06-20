import asyncssh
from typing import Dict, Any, Optional


class SSHClient:
    """Generic SSH client for retrieving configuration from network devices via SSH."""

    def __init__(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        port: int = 22,
        private_key: Optional[str] = None,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.private_key = private_key

    async def get_config(self) -> Dict[str, Any]:
        """
        Retrieve configuration from a network device using SSH.

        Returns:
            Dictionary containing the device configuration
        """
        try:
            connect_kwargs = {
                "username": self.username,
                "port": self.port,
            }
            if self.password:
                connect_kwargs["password"] = self.password
            if self.private_key:
                connect_kwargs["client_keys"] = [self.private_key]

            async with asyncssh.connect(self.host, **connect_kwargs) as conn:
                running_config_result = await conn.run("show running-configuration")
                version_result = await conn.run("show version")
                interfaces_result = await conn.run("show interfaces status")
                return {
                    "running_config": running_config_result.stdout,
                    "version_info": version_result.stdout,
                    "interfaces": interfaces_result.stdout,
                    "source": "ssh",
                }
        except Exception as e:
            return {
                "error": str(e),
                "source": "ssh",
                "running_config": None,
                "version_info": None,
                "interfaces": None,
            }
