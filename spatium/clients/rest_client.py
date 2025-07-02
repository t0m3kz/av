"""REST API client for retrieving configuration from network devices via HTTP/HTTPS."""

import json
import logging
from typing import Any
from urllib.parse import urljoin

import httpx
from httpx._types import AuthTypes

logger = logging.getLogger(__name__)


class RestClient:
    """Generic REST client for retrieving configuration from network devices via REST API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str | None = None,
        port: int = 443,
        use_https: bool = True,
        custom_headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize REST client with connection parameters."""
        self.host = host
        self.username = username
        self.password = password
        self.port = port or (443 if use_https else 80)
        self.use_https = use_https
        self.verify_ssl = kwargs.get("verify_ssl", False)
        self.timeout = kwargs.get("timeout", 30)
        self.api_token = kwargs.get("api_token")
        self.custom_headers = custom_headers or {}

        # Build base URL
        protocol = "https" if use_https else "http"
        if (use_https and port != 443) or (not use_https and port != 80):
            self.base_url = f"{protocol}://{host}:{port}"
        else:
            self.base_url = f"{protocol}://{host}"

        logger.debug(f"Initialized REST client for {self.base_url}")

    async def get_config(self, endpoint: str = "/api/config") -> dict[str, Any]:
        """Retrieve configuration from a network device using REST API.

        Args:
            endpoint: REST API endpoint to call for configuration

        Returns:
            Dictionary containing the device host, configuration, and error if any.
        """
        try:
            headers = self._build_headers()
            auth = self._build_auth()

            async with httpx.AsyncClient(
                verify=self.verify_ssl, timeout=self.timeout, headers=headers
            ) as client:
                url = urljoin(self.base_url, endpoint)
                logger.debug(f"Making REST request to {url}")

                response = await client.get(url, auth=auth)
                response.raise_for_status()

                # Try to parse as JSON first
                try:
                    config_data = response.json()
                    running_config = json.dumps(config_data, indent=2)
                except json.JSONDecodeError:
                    # If not JSON, use raw text
                    running_config = response.text

                # Try to get additional information if available
                version_info = await self._get_version_info(client, auth)
                interfaces = await self._get_interface_info(client, auth)

                return {
                    "host": self.host,
                    "running_config": running_config,
                    "version_info": version_info,
                    "interfaces": interfaces,
                    "source": "rest",
                    "error": None,
                }

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"REST API error for {self.host}: {error_msg}")
            return self._error_response(error_msg)
        except httpx.ConnectError as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(f"Connection error for {self.host}: {error_msg}")
            return self._error_response(error_msg)
        except httpx.TimeoutException:
            error_msg = f"Request timeout after {self.timeout}s"
            logger.error(f"Timeout error for {self.host}: {error_msg}")
            return self._error_response(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error for {self.host}: {error_msg}")
            return self._error_response(error_msg)

    async def get_config_custom(self, custom_url: str) -> Any:
        """Retrieve configuration using a custom URL.

        Args:
            custom_url: Custom URL to retrieve configuration from

        Returns:
            Configuration data as string
        """
        try:
            headers = self._build_headers()
            auth = self._build_auth()

            async with httpx.AsyncClient(
                verify=self.verify_ssl, timeout=self.timeout, headers=headers
            ) as client:
                logger.debug(f"Making REST request to custom URL: {custom_url}")

                response = await client.get(custom_url, auth=auth)
                response.raise_for_status()

                # Return the response text
                return response.text

        except Exception as e:
            logger.error(f"Custom URL config retrieval failed: {e}")
            raise

    def _build_headers(self) -> dict[str, str]:
        """Build HTTP headers for the request."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Spatium-REST-Client/1.0",
        }

        # Add API token if provided
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        # Add custom headers
        headers.update(self.custom_headers)

        return headers

    def _build_auth(self) -> AuthTypes | None:
        """Build authentication for the request."""
        if self.username and self.password and not self.api_token:
            return httpx.BasicAuth(self.username, self.password)
        return None

    async def _get_version_info(
        self, client: httpx.AsyncClient, auth: AuthTypes | None
    ) -> str | None:
        """Try to get version information from the device."""
        version_endpoints = [
            "/api/version",
            "/api/system/version",
            "/rest/version",
            "/restconf/data/system-state/platform",
        ]

        for endpoint in version_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = await client.get(url, auth=auth)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        return json.dumps(data, indent=2)
                    except json.JSONDecodeError:
                        return str(response.text)
            except Exception as e:
                logger.debug(f"Version endpoint {endpoint} failed: {e}")
                continue

        return None

    async def _get_interface_info(
        self, client: httpx.AsyncClient, auth: AuthTypes | None
    ) -> str | None:
        """Try to get interface information from the device."""
        interface_endpoints = [
            "/api/interfaces",
            "/api/system/interfaces",
            "/rest/interfaces",
            "/restconf/data/interfaces",
        ]

        for endpoint in interface_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = await client.get(url, auth=auth)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        return json.dumps(data, indent=2)
                    except json.JSONDecodeError:
                        return str(response.text)
            except Exception as e:
                logger.debug(f"Interface endpoint {endpoint} failed: {e}")
                continue

        return None

    def _error_response(self, error_msg: str) -> dict[str, Any]:
        """Create a standardized error response."""
        return {
            "host": self.host,
            "running_config": None,
            "version_info": None,
            "interfaces": None,
            "source": "rest",
            "error": error_msg,
        }

    async def test_connection(self) -> dict[str, Any]:
        """Test the REST API connection without retrieving full configuration.

        Returns:
            Dictionary with connection test results
        """
        try:
            headers = self._build_headers()
            auth = self._build_auth()

            async with httpx.AsyncClient(
                verify=self.verify_ssl,
                timeout=10,  # Shorter timeout for connection test
                headers=headers,
            ) as client:
                # Try common health/status endpoints
                test_endpoints = ["/api/health", "/api/status", "/health", "/status", "/"]

                for endpoint in test_endpoints:
                    try:
                        url = urljoin(self.base_url, endpoint)
                        response = await client.get(url, auth=auth)
                        if (
                            response.status_code < 500
                        ):  # Any non-server error is considered reachable
                            return {
                                "success": True,
                                "status_code": response.status_code,
                                "endpoint": endpoint,
                                "message": "Connection successful",
                            }
                    except Exception as e:
                        logger.debug(f"Exception during endpoint test {endpoint}: {e}")
                        continue

                return {
                    "success": False,
                    "error": "No reachable endpoints found",
                    "tested_endpoints": test_endpoints,
                }

        except Exception as e:
            return {"success": False, "error": str(e)}


class DeviceSpecificRestClient(RestClient):
    """Device-specific REST client with predefined endpoints for common network devices."""

    DEVICE_ENDPOINTS = {
        "sonic": {
            "config": "/restconf/data/sonic-device:sonic-device",
            "version": "/restconf/data/sonic-system:sonic-system/DEVICE_METADATA",
            "interfaces": "/restconf/data/sonic-port:sonic-port",
        },
        "arista": {
            "config": "/command-api",
            "version": "/command-api",
            "interfaces": "/command-api",
        },
        "cisco": {
            "config": "/restconf/data/Cisco-IOS-XE-native:native",
            "version": "/restconf/data/Cisco-IOS-XE-device-hardware-oper:device-hardware-oper-data",
            "interfaces": "/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces",
        },
        "juniper": {
            "config": "/rpc/get-configuration",
            "version": "/rpc/get-software-information",
            "interfaces": "/rpc/get-interface-information",
        },
    }

    def __init__(self, device_type: str, **kwargs: Any) -> None:
        """Initialize REST client for a specific device type."""
        super().__init__(**kwargs)
        self.device_type = device_type.lower()
        self.endpoints = self.DEVICE_ENDPOINTS.get(self.device_type, {})

    async def get_config(self, endpoint: str | None = None) -> dict[str, Any]:
        """Get configuration using device-specific endpoint."""
        if endpoint is None:
            endpoint = self.endpoints.get("config", "/api/config")

        # Handle special cases for specific devices
        if self.device_type == "arista":
            return await self._get_arista_config(endpoint)

        return await super().get_config(endpoint)

    async def get_config_custom(self, custom_url: str) -> dict[str, Any]:
        """Get configuration using a custom URL."""
        try:
            headers = self._build_headers()
            auth = self._build_auth()

            async with httpx.AsyncClient(
                verify=self.verify_ssl, timeout=self.timeout, headers=headers
            ) as client:
                response = await client.get(custom_url, auth=auth)
                response.raise_for_status()

                # Try to parse as JSON, fallback to text
                try:
                    config_data = response.json()
                except Exception:
                    config_data = response.text

                return config_data  # type: ignore[no-any-return]

        except Exception as e:
            logger.error(f"Custom URL config retrieval failed: {e}")
            raise

    async def _get_arista_config(self, endpoint: str) -> dict[str, Any]:
        """Handle Arista EOS API specific format."""
        try:
            headers = self._build_headers()
            auth = self._build_auth()

            # Arista EOS API expects JSON-RPC format
            payload = {
                "jsonrpc": "2.0",
                "method": "runCmds",
                "params": {"version": 1, "cmds": ["show running-config"]},
                "id": "1",
            }

            async with httpx.AsyncClient(
                verify=self.verify_ssl, timeout=self.timeout, headers=headers
            ) as client:
                url = urljoin(self.base_url, endpoint)
                response = await client.post(
                    url, json=payload, auth=auth or httpx.USE_CLIENT_DEFAULT
                )
                response.raise_for_status()

                data = response.json()
                if "result" in data and data["result"]:
                    running_config = data["result"][0].get("output", "")
                else:
                    running_config = json.dumps(data, indent=2)

                return {
                    "host": self.host,
                    "running_config": running_config,
                    "version_info": None,  # Could be enhanced to get version
                    "interfaces": None,  # Could be enhanced to get interfaces
                    "source": "rest",
                    "error": None,
                }

        except Exception as e:
            return self._error_response(str(e))
