import os
import yaml
from typing import Dict, Any, List
import asyncio
import logging

logger = logging.getLogger(__name__)

class ContainerLabDeployer:
    """
    Manages deployment of network digital twins using ContainerLab.
    """
    
    def __init__(self, topology_dir: str = "topologies"):
        """
        Initialize the ContainerLab deployer.
        
        Args:
            topology_dir: Directory to store topology files
        """
        self.topology_dir = topology_dir
        os.makedirs(topology_dir, exist_ok=True)
    
    async def deploy_topology(self, topology_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a network topology using ContainerLab.
        
        Args:
            topology_config: Topology configuration
            
        Returns:
            Deployment result details
        """
        topology_name = topology_config.get("name", f"spatium-{os.urandom(4).hex()}")
        topology_file = os.path.join(self.topology_dir, f"{topology_name}.yaml")
        
        # Write topology config to file
        with open(topology_file, "w") as f:
            yaml.dump(topology_config, f)
        
        # Deploy using ContainerLab
        try:
            process = await asyncio.create_subprocess_exec(
                "containerlab", "deploy", "-t", topology_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"ContainerLab deployment failed: {error_msg}")
                return {
                    "success": False,
                    "topology_name": topology_name,
                    "error": error_msg
                }
            
            # Parse the output to get deployed nodes info
            output = stdout.decode()
            
            return {
                "success": True,
                "topology_name": topology_name,
                "topology_file": topology_file,
                "output": output
            }
            
        except Exception as e:
            logger.exception("Failed to deploy ContainerLab topology")
            return {
                "success": False,
                "topology_name": topology_name,
                "error": str(e)
            }
    
    async def destroy_topology(self, topology_name: str) -> Dict[str, Any]:
        """
        Destroy a deployed topology.
        
        Args:
            topology_name: Name of the topology to destroy
            
        Returns:
            Result of the destroy operation
        """
        topology_file = os.path.join(self.topology_dir, f"{topology_name}.yaml")
        
        if not os.path.exists(topology_file):
            return {
                "success": False,
                "error": f"Topology file not found: {topology_file}"
            }
        
        try:
            process = await asyncio.create_subprocess_exec(
                "containerlab", "destroy", "-t", topology_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return {
                    "success": False,
                    "topology_name": topology_name,
                    "error": error_msg
                }
            
            return {
                "success": True,
                "topology_name": topology_name,
                "output": stdout.decode()
            }
            
        except Exception as e:
            return {
                "success": False,
                "topology_name": topology_name,
                "error": str(e)
            }
    
    async def list_deployments(self) -> Dict[str, Any]:
        """
        List all deployed topologies.
        
        Returns:
            List of deployed topologies
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "containerlab", "inspect", "--all",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return {
                    "success": False,
                    "error": error_msg
                }
            
            return {
                "success": True,
                "output": stdout.decode()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_sonic_topology(
        self, 
        name: str, 
        nodes: List[Dict[str, Any]], 
        links: List[Dict[str, Any]],
        mgmt_network: str = "spatium-mgmt"
    ) -> Dict[str, Any]:
        """
        Create a topology configuration for SONiC devices.
        
        Args:
            name: Topology name
            nodes: List of node configurations
            links: List of link configurations
            mgmt_network: Management network name
            
        Returns:
            ContainerLab topology configuration
        """
        topology = {
            "name": name,
            "prefix": f"spatium-{name}",
            "mgmt": {
                "network": mgmt_network,
                "ipv4-subnet": "172.20.20.0/24",
                "ipv6-subnet": "2001:172:20:20::/64"
            },
            "topology": {
                "nodes": {},
                "links": []
            }
        }
        
        # Add nodes
        for i, node in enumerate(nodes):
            node_name = node.get("name", f"sonic{i+1}")
            node_type = node.get("type", "sonic-vs")
            node_image = node.get("image", "docker-sonic-vs:latest")
            
            topology["topology"]["nodes"][node_name] = {
                "kind": node_type,
                "image": node_image,
                "ports": node.get("ports", [])
            }
        
        # Add links
        for link in links:
            endpoints = [
                f"{link.get('node1')}{link.get('interface1', '')}",
                f"{link.get('node2')}{link.get('interface2', '')}"
            ]
            topology["topology"]["links"].append(endpoints)
        
        return topology