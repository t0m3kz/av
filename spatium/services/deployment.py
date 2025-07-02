"""Deployment service for managing network topology deployments.

Handles ContainerLab topology operations including deploy, destroy, and list.
"""

import asyncio
import json
import logging
from pathlib import Path
import re
import shutil
from typing import Any

import yaml

from spatium.api.exceptions import DeploymentError
from spatium.core.config import get_settings
from spatium.models.deployment import DeploymentResponse, LinkConfig, NodeConfig, TopologyConfig

logger = logging.getLogger(__name__)


class ContainerLabDeploymentService:
    """Service for managing ContainerLab deployments."""

    def __init__(self, working_directory: str = "./topologies"):
        """Initialize deployment service with working directory."""
        self.working_directory = Path(working_directory)
        self.working_directory.mkdir(exist_ok=True)
        self.settings = get_settings()

        # Validate ContainerLab is available
        self._validate_containerlab_availability()

    def _validate_containerlab_availability(self) -> None:
        """Check if ContainerLab is installed and available."""
        if not shutil.which("containerlab"):
            raise DeploymentError(
                "ContainerLab is not installed or not available in PATH. "
                "Please install ContainerLab before using deployment features."
            )

    async def deploy_topology(self, config: TopologyConfig) -> DeploymentResponse:
        """Deploy a topology using ContainerLab.

        Args:
            config: Topology configuration

        Returns:
            DeploymentResponse: Result of the deployment operation
        """
        try:
            # Validate configuration
            self._validate_config(config)

            # Create topology file
            topology_file = self._create_topology_file(config)

            # Deploy using containerlab
            cmd = ["containerlab", "deploy", "-t", str(topology_file)]
            if hasattr(self.settings, "CONTAINERLAB_TIMEOUT"):
                timeout_value = str(self.settings.CONTAINERLAB_TIMEOUT)
                # Add time unit if not present
                if timeout_value.isdigit():
                    timeout_value += "s"
                cmd.extend(["--timeout", timeout_value])

            result = await self._run_command(cmd)

            logger.info(f"Successfully deployed topology '{config.name}'")

            return DeploymentResponse(
                success=True,
                topology_name=config.name,
                topology_file=str(topology_file),
                output=str(result.get("stdout", "")),
                error=None,
            )

        except DeploymentError as e:
            error_msg = f"Failed to deploy topology '{config.name}': {e}"
            logger.error(error_msg)
            return DeploymentResponse(
                success=False,
                topology_name=config.name,
                topology_file=None,
                output=None,
                error=error_msg,
            )
        except Exception as e:
            error_msg = f"Unexpected error deploying topology '{config.name}': {e}"
            logger.error(error_msg)
            return DeploymentResponse(
                success=False,
                topology_name=config.name,
                topology_file=None,
                output=None,
                error=error_msg,
            )

    async def destroy_topology(self, topology_name: str) -> DeploymentResponse:
        """Destroy a deployed topology.

        Args:
            topology_name: Name of the topology to destroy

        Returns:
            DeploymentResponse: Result of the destroy operation
        """
        try:
            # Find topology file
            topology_file = self.working_directory / f"{topology_name}.yaml"

            if not topology_file.exists():
                raise DeploymentError(f"Topology file not found: {topology_file}")

            # Destroy using containerlab
            cmd = ["containerlab", "destroy", "-t", str(topology_file)]
            result = await self._run_command(cmd)

            logger.info(f"Successfully destroyed topology '{topology_name}'")

            return DeploymentResponse(
                success=True,
                topology_name=topology_name,
                topology_file=str(topology_file),
                output=str(result.get("stdout", "")),
                error=None,
            )

        except Exception as e:
            error_msg = f"Failed to destroy topology '{topology_name}': {e}"
            logger.error(error_msg)
            return DeploymentResponse(
                success=False,
                topology_name=topology_name,
                topology_file=None,
                output=None,
                error=error_msg,
            )

    async def list_deployments(self) -> dict[str, Any]:
        """List all deployed topologies.

        Returns:
            Dict containing list of deployed topologies
        """
        try:
            cmd = ["containerlab", "inspect", "--all"]
            result = await self._run_command(cmd)

            # Parse containerlab output
            stdout_output = str(result.get("stdout", ""))
            deployments = self._parse_deployments(stdout_output)

            return {"success": True, "deployments": deployments, "count": len(deployments)}

        except Exception as e:
            error_msg = f"Failed to list deployments: {e}"
            logger.error(error_msg)
            return {"success": False, "deployments": [], "count": 0, "error": error_msg}

    async def get_topology_status(self, topology_name: str) -> dict[str, Any]:
        """Get the status of a specific topology.

        Args:
            topology_name: Name of the topology to check

        Returns:
            Dict containing topology status information
        """
        try:
            cmd = ["containerlab", "inspect", "-t", f"{topology_name}.yaml"]
            result = await self._run_command(cmd)

            # Parse the output for this specific topology
            deployments = self._parse_deployments(str(result.get("stdout", "")))

            if deployments:
                return {
                    "success": True,
                    "topology_name": topology_name,
                    "status": deployments[0],
                    "found": True,
                }
            else:
                return {
                    "success": True,
                    "topology_name": topology_name,
                    "status": {"name": topology_name, "status": "not_deployed"},
                    "found": False,
                }

        except Exception as e:
            logger.error(f"Failed to get status for topology '{topology_name}': {e}")
            return {
                "success": False,
                "topology_name": topology_name,
                "error": str(e),
                "found": False,
            }

    def list_topology_files(self) -> list[dict[str, Any]]:
        """List all topology files in the working directory.

        Returns:
            List of topology file information
        """
        topology_files = []

        try:
            for file_path in self.working_directory.glob("*.yaml"):
                try:
                    with file_path.open(encoding="utf-8") as f:
                        data = yaml.safe_load(f)

                    topology_files.append(
                        {
                            "filename": file_path.name,
                            "path": str(file_path),
                            "name": data.get("name", "unknown") if data else "unknown",
                            "size": file_path.stat().st_size,
                            "modified": file_path.stat().st_mtime,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to parse topology file {file_path}: {e}")
                    topology_files.append(
                        {
                            "filename": file_path.name,
                            "path": str(file_path),
                            "name": "parse_error",
                            "size": file_path.stat().st_size,
                            "modified": file_path.stat().st_mtime,
                            "error": str(e),
                        }
                    )

        except Exception as e:
            logger.error(f"Failed to list topology files: {e}")

        return topology_files

    def delete_topology_file(self, topology_name: str) -> bool:
        """Delete a topology file from the working directory.

        Args:
            topology_name: Name of the topology file to delete

        Returns:
            bool: True if file was deleted, False otherwise
        """
        try:
            topology_file = self.working_directory / f"{topology_name}.yaml"
            if topology_file.exists():
                topology_file.unlink()
                logger.info(f"Deleted topology file: {topology_file}")
                return True
            else:
                logger.warning(f"Topology file not found: {topology_file}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete topology file '{topology_name}': {e}")
            return False

    def _validate_config(self, config: TopologyConfig) -> None:
        """Validate topology configuration."""
        _validate_topology_name(config.name)
        node_names = _validate_nodes(config.nodes)
        _validate_links_exist(config.links, node_names)

    def _create_topology_file(self, config: TopologyConfig) -> Path:
        """Create a ContainerLab topology file from the configuration."""
        # Build the prefix - use config name but ensure it's valid
        prefix = re.sub(r"[^a-zA-Z0-9_-]", "-", config.name)

        topology_data = {
            "name": config.name,
            "prefix": prefix,
            "mgmt": {
                "network": config.mgmt_network or "spatium-mgmt",
                "ipv4-subnet": "172.20.0.0/23",
            },
            "topology": {
                "nodes": self._build_nodes(config.nodes),
                "links": self._build_links(config.links),
            },
        }

        topology_file = self.working_directory / f"{config.name}.yaml"

        # Ensure we don't overwrite existing files without warning
        if topology_file.exists():
            logger.warning(f"Overwriting existing topology file: {topology_file}")

        # Write YAML file with proper formatting
        try:
            with topology_file.open("w", encoding="utf-8") as f:
                yaml.dump(topology_data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise DeploymentError(f"Failed to create topology file {topology_file}: {e}") from e

        logger.info(f"Created topology file: {topology_file}")
        return topology_file

    def _build_nodes(self, nodes: list[NodeConfig]) -> dict[str, Any]:
        """Build nodes configuration for ContainerLab."""
        result = {}
        for node in nodes:
            result[node.name] = {"kind": node.type, "image": node.image}
            if node.ports is not None:
                result[node.name]["ports"] = node.ports  # type: ignore[assignment]
        return result

    def _build_links(self, links: list[LinkConfig]) -> list[dict[str, Any]]:
        """Build links configuration for ContainerLab."""
        result = []
        for link in links:
            endpoints = []
            if link.interface1:
                endpoints.append(f"{link.node1}:{link.interface1}")
            else:
                endpoints.append(link.node1)

            if link.interface2:
                endpoints.append(f"{link.node2}:{link.interface2}")
            else:
                endpoints.append(link.node2)

            result.append({"endpoints": endpoints})
        return result

    async def _run_command(self, cmd: list[str]) -> dict[str, str | int]:
        """Run a shell command and return the result. Raises DeploymentError on failure."""
        try:
            logger.debug(f"Running command: {' '.join(cmd)} in {self.working_directory}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_directory,
            )
            stdout, stderr = await process.communicate()
            result: dict[str, str | int] = {
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
                "returncode": process.returncode or 0,
            }
            if process.returncode != 0:
                logger.error(f"Command failed: {' '.join(cmd)}\nSTDERR: {result['stderr']}")
                raise DeploymentError(f"Command failed: {' '.join(cmd)}\n{result['stderr']}")
            logger.debug(f"Command output: {result['stdout']}")
            return result
        except FileNotFoundError as e:
            logger.error(f"Command not found: {cmd[0]}")
            raise DeploymentError(f"Command not found: {cmd[0]}") from e
        except Exception as e:
            logger.error(f"Failed to run command {' '.join(cmd)}: {e}")
            raise DeploymentError(f"Failed to run command {' '.join(cmd)}: {e}") from e

    def _parse_deployments(self, output: str) -> list[dict[str, Any]]:
        """Parse containerlab inspect output to extract deployment information."""
        deployments = []
        try:
            data = json.loads(output)
            deployments = self._parse_json_deployments(data)
        except (json.JSONDecodeError, TypeError):
            try:
                deployments = self._parse_text_deployments(output)
            except Exception as e:
                logger.warning(f"Failed to parse deployments output as text: {e}")
        except Exception as e:
            logger.warning(f"Failed to parse deployments output: {e}")
        return deployments

    def _parse_json_deployments(self, data: Any) -> list[dict[str, Any]]:
        deployments = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "name" in item:
                    deployments.append(
                        {
                            "name": item.get("name", "unknown"),
                            "status": item.get("state", "unknown"),
                            "lab_path": item.get("lab-path", ""),
                            "containers": item.get("containers", {}),
                        }
                    )
        elif isinstance(data, dict) and "containers" in data:
            deployments.append(
                {
                    "name": data.get("name", "unknown"),
                    "status": "running" if data.get("containers") else "unknown",
                    "lab_path": data.get("lab-path", ""),
                    "containers": data.get("containers", {}),
                }
            )
        return deployments

    def _parse_text_deployments(self, output: str) -> list[dict[str, Any]]:
        deployments = []
        lines = output.strip().split("\n")
        for line in lines:
            if line.strip() and not line.startswith("+") and not line.startswith("|"):
                parts = line.split()
                if len(parts) >= 2:
                    deployments.append(
                        {
                            "name": parts[0],
                            "status": parts[1] if len(parts) > 1 else "unknown",
                        }
                    )
        return deployments


def _validate_topology_name(name: str) -> None:
    if not name:
        raise DeploymentError("Topology name is required")
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        raise DeploymentError(
            "Topology name must contain only alphanumeric characters, hyphens, and underscores"
        )


def _validate_nodes(nodes: list) -> list[str]:
    if not nodes:
        raise DeploymentError("At least one node is required")
    node_names = [node.name for node in nodes]
    if len(node_names) != len(set(node_names)):
        duplicates = [name for name in node_names if node_names.count(name) > 1]
        raise DeploymentError(f"Node names must be unique. Duplicates found: {set(duplicates)}")
    for node in nodes:
        if not node.name:
            raise DeploymentError("All nodes must have a name")
        if not node.type:
            raise DeploymentError(f"Node '{node.name}' must have a type/kind specified")
        if not node.image:
            raise DeploymentError(f"Node '{node.name}' must have an image specified")
    return node_names


def _validate_links_exist(links: list[LinkConfig] | None, node_names: list[str]) -> None:
    if links:
        for i, link in enumerate(links):
            if link.node1 not in node_names:
                raise DeploymentError(f"Link {i + 1} references unknown node: {link.node1}")
            if link.node2 not in node_names:
                raise DeploymentError(f"Link {i + 1} references unknown node: {link.node2}")
            if link.node1 == link.node2:
                raise DeploymentError(f"Link {i + 1} cannot connect a node to itself: {link.node1}")
