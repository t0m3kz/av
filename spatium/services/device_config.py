"""
Device configuration service for retrieving configurations from network devices.
"""
import asyncio
import json
import logging
import os
from typing import Callable, Dict, List, Optional

from spatium.api.exceptions import ConfigurationError, DeviceConnectionError
from spatium.clients.rest_client import RestClient
from spatium.core.device_constants import (
    DEVICE_CONFIG_COMMANDS,
    DEVICE_REST_ENDPOINTS,
    DEFAULT_DEVICE_MODEL,
    DEFAULT_CONFIG_TIMEOUT
)
from spatium.models.device import DeviceConfigRequest
from spatium.api.responses import DeviceConfigResult, ConfigSaveResult

logger = logging.getLogger(__name__)


class DeviceConfigService:
    """Service for retrieving device configurations."""
    
    def __init__(self, ssh_client_factory: Callable, rest_client_factory: Optional[Callable] = None):
        self.ssh_client_factory = ssh_client_factory
        self.rest_client_factory = rest_client_factory or RestClient
    
    def get_config_command(self, device_model: Optional[str] = None) -> str:
        """Get the configuration command for a device model."""
        return DEVICE_CONFIG_COMMANDS.get(
            (device_model or "").lower(), 
            DEVICE_CONFIG_COMMANDS[DEFAULT_DEVICE_MODEL]
        )
    
    async def fetch_config_via_rest(self, device: DeviceConfigRequest) -> DeviceConfigResult:
        """Fetch configuration via REST API."""
        try:
            # Create REST client instance
            rest_client = self.rest_client_factory(
                host=device.host,
                username=device.username,
                password=device.password,
                port=device.port or 80,
                use_https=False,  # Default to HTTP for testing
                timeout=DEFAULT_CONFIG_TIMEOUT
            )
            
            # Use custom URL if provided, otherwise use device-specific endpoint
            if device.rest_url:
                config_data = await rest_client.get_config_custom(device.rest_url)
                # get_config_custom may return a string or dict depending on implementation/mocking
                if isinstance(config_data, dict):
                    running_config = json.dumps(config_data, indent=2)
                else:
                    running_config = str(config_data)
                return DeviceConfigResult(
                    host=device.host,
                    running_config=running_config,
                    source="rest",
                    error=None
                )
            else:
                config_result = await rest_client.get_config()
                # get_config returns a dict which may contain error information
                if isinstance(config_result, dict):
                    # Check if this is an error response
                    if config_result.get("error"):
                        return DeviceConfigResult(
                            host=device.host,
                            running_config=None,
                            source="rest",
                            error=config_result["error"]
                        )
                    # Check if this is the structured response from real REST client
                    elif "running_config" in config_result:
                        running_config = config_result["running_config"]
                    else:
                        # This is likely a test mock returning config data directly
                        running_config = json.dumps(config_result, indent=2) if config_result else ""
                else:
                    running_config = str(config_result)
                
                return DeviceConfigResult(
                    host=device.host,
                    running_config=running_config,
                    source="rest",
                    error=None
                )
        except Exception as e:
            logger.error(f"REST API config retrieval failed for {device.host}: {e}")
            return DeviceConfigResult(
                host=device.host,
                running_config=None,
                source="rest",
                error=str(e)
            )
    
    async def fetch_config_via_ssh(self, device: DeviceConfigRequest) -> DeviceConfigResult:
        """Fetch configuration via SSH."""
        try:
            ssh_client = self.ssh_client_factory(
                host=device.host,
                username=device.username,
                password=device.password,
                private_key=device.private_key,
                port=device.port,
            )
            
            command = self.get_config_command(device.device_model)
            result = await ssh_client.get_config(command=command)
            
            return DeviceConfigResult(
                host=device.host,
                running_config=result.get("running_config"),
                source="ssh",
                error=result.get("error")
            )
        except Exception as e:
            logger.error(f"SSH config retrieval failed for {device.host}: {e}")
            return DeviceConfigResult(
                host=device.host,
                running_config=None,
                source="ssh",
                error=str(e)
            )
    
    async def fetch_config(self, device: DeviceConfigRequest) -> DeviceConfigResult:
        """Fetch configuration from a device using the specified method."""
        method = (device.method or "ssh").lower()
        
        if method == "rest":
            return await self.fetch_config_via_rest(device)
        else:
            return await self.fetch_config_via_ssh(device)
    
    async def fetch_configs_bulk(self, devices: List[DeviceConfigRequest]) -> List[DeviceConfigResult]:
        """Fetch configurations from multiple devices concurrently."""
        if not devices:
            return []
        
        tasks = [self.fetch_config(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions from gather
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Exception while fetching config for device {devices[i].host}: {result}")
                processed_results.append(DeviceConfigResult(
                    host=devices[i].host,
                    running_config=None,
                    source=devices[i].method or "ssh",
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def save_configs_to_files(
        self, 
        devices: List[DeviceConfigRequest], 
        output_folder: str = "outputs"
    ) -> List[ConfigSaveResult]:
        """Fetch configurations and save them to files."""
        os.makedirs(output_folder, exist_ok=True)
        
        # Fetch configurations
        config_results = await self.fetch_configs_bulk(devices)
        
        save_results = []
        for result in config_results:
            save_result = ConfigSaveResult(
                host=result.host,
                source=result.source,
                error=result.error,
                message="",
                file_path=None
            )
            
            if result.running_config and not result.error:
                try:
                    filename = f"{output_folder}/{result.host}_config.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        if isinstance(result.running_config, dict):
                            f.write(json.dumps(result.running_config, indent=2))
                        else:
                            f.write(str(result.running_config))
                    
                    save_result.message = f"Configuration for host {result.host} saved to {filename}"
                    save_result.file_path = filename
                except Exception as e:
                    save_result.error = f"Failed to save config to file: {e}"
                    save_result.message = f"Failed to save configuration for host {result.host}"
            else:
                save_result.message = f"No configuration retrieved for host {result.host}"
                if result.error:
                    save_result.error = result.error
            
            save_results.append(save_result)
        
        return save_results
