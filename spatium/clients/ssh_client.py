"""
SSH client for retrieving configurations from network devices.
"""
import asyncssh
import json
import logging
from typing import Dict, Any, Optional

from spatium.api.exceptions import DeviceConnectionError, ConfigurationError

logger = logging.getLogger(__name__)


class SSHClient:
    """Generic SSH client for retrieving configuration from network devices via SSH."""

    def __init__(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        port: int = 22,
        private_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.private_key = private_key
        self.timeout = timeout
    
    async def test_connection(self) -> bool:
        """Test SSH connection to the device."""
        try:
            conn = await asyncssh.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                client_keys=[self.private_key] if self.private_key else None,
                known_hosts=None,
                connect_timeout=self.timeout
            )
            conn.close()
            return True
        except Exception as e:
            logger.error(f"SSH connection test failed for {self.host}: {e}")
            return False

    async def execute_command(self, command: str) -> str:
        """Execute a single command and return the output."""
        try:
            conn = await asyncssh.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                client_keys=[self.private_key] if self.private_key else None,
                known_hosts=None,
                connect_timeout=self.timeout
            )
            try:
                result = await conn.run(command, timeout=self.timeout)
                return result.stdout.strip()
            finally:
                conn.close()
        except asyncssh.Error as e:
            raise DeviceConnectionError(f"SSH command execution failed: {e}")
        except Exception as e:
            raise ConfigurationError(f"Command execution error: {e}")

    async def get_config(self, command: str = "show running-configuration") -> Dict[str, Any]:
        """
        Retrieve configuration from a network device using SSH.

        Args:
            command: Configuration command to execute

        Returns:
            Dictionary containing the device host, configuration, and error if any.
        """
        try:
            # Try primary configuration command
            running_config = await self.execute_command(command)
            
            # If primary command returns empty, try alternative for SONiC devices
            if not running_config:
                try:
                    running_config = await self.execute_command("cat /etc/sonic/config_db.json")
                except Exception:
                    pass  # Continue with empty config if alternative fails
            
            # Try to parse as JSON and format it
            try:
                config_json = json.loads(running_config)
                running_config = json.dumps(config_json, indent=2)
            except (json.JSONDecodeError, TypeError):
                # Keep as string if not valid JSON
                pass
            
            # Get additional device information
            version_info = await self._get_version_info()
            interfaces = await self._get_interfaces_info()
            
            return {
                "host": self.host,
                "running_config": running_config,
                "version_info": version_info,
                "interfaces": interfaces,
                "source": "ssh",
                "error": None,
            }
        except Exception as e:
            logger.error(f"SSH config retrieval failed for {self.host}: {e}")
            return {
                "host": self.host,
                "running_config": None,
                "version_info": None,
                "interfaces": None,
                "source": "ssh",
                "error": str(e),
            }
    
    async def _get_version_info(self) -> Optional[str]:
        """Get device version information."""
        try:
            return await self.execute_command("show version")
        except Exception:
            logger.debug(f"Could not retrieve version info for {self.host}")
            return None
    
    async def _get_interfaces_info(self) -> Optional[str]:
        """Get device interfaces information."""
        try:
            return await self.execute_command("show interfaces status")
        except Exception:
            logger.debug(f"Could not retrieve interfaces info for {self.host}")
            return None
