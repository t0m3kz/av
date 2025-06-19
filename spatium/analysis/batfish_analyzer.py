# from pybatfish.question import b
# from pybatfish.client.session import Session
# import tempfile
# import os
# import shutil
# from typing import Dict, Any

# def analyze_config_with_batfish(config_text: str) -> Dict[str, Any]:
#     """
#     Analyze network device configuration using Batfish.

#     Args:
#         config_text: Device configuration as text

#     Returns:
#         Dictionary containing analysis results
#     """
#     temp_dir = tempfile.mkdtemp()
#     try:
#         # Write config to a file
#         config_path = os.path.join(temp_dir, "device.conf")
#         with open(config_path, "w") as f:
#             f.write(config_text)

#         # Initialize Batfish session, network, and snapshot
#         bf = Session()
#         bf.set_network("spatium-analysis")
#         bf.init_snapshot(temp_dir, name="snapshot1", overwrite=True)

#         # Analyze the configuration
#         result = {}

#         # Interface properties
#         interface_props = bfq.interfaceProperties().answer().frame()
#         result["interfaces"] = interface_props.to_dict(orient="records")

#         # IP owners
#         ip_owners = bfq.ipOwners().answer().frame()
#         result["ip_owners"] = ip_owners.to_dict(orient="records")

#         # Routing tables
#         routes = bfq.routes().answer().frame()
#         result["routes"] = routes.to_dict(orient="records")

#         # Layer 3 topology
#         layer3_topology = bfq.layer3Edges().answer().frame()
#         result["layer3_topology"] = layer3_topology.to_dict(orient="records")

#         # Undefined references
#         undefined_refs = bfq.undefinedReferences().answer().frame()
#         result["undefined_references"] = undefined_refs.to_dict(orient="records")

#         return result
#     finally:
#         # Clean up temporary directory
#         shutil.rmtree(temp_dir)
