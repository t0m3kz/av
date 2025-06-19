# Configuration Analysis

This guide explains how to analyze network configurations using Spatium and Batfish.

## Analysis Capabilities

Spatium uses Batfish to analyze network configurations and identify:

- Interface properties
- IP address assignments
- Routing tables
- Layer 3 topology
- Undefined references
- Configuration compliance issues

## Analyzing a Configuration

You can analyze a configuration using the `/analysis/config` endpoint:

```json
{
  "config": "interface Ethernet0\n  ip address 192.168.1.1/24\n  no shutdown"
}
```

## Analysis Output

The analysis output includes several sections:

### Interface Properties

This section lists all interfaces and their properties:

```json
"interfaces": [
  {
    "Interface": "Ethernet0",
    "VRF": "default",
    "Primary_Address": "192.168.1.1/24",
    "Access_VLAN": null,
    "Active": true
  }
]
```

### IP Owners

This section shows IP addresses assigned to interfaces:

```json
"ip_owners": [
  {
    "IP": "192.168.1.1",
    "Interface": "Ethernet0",
    "Node": "device1"
  }
]
```

### Routes

This section shows routing table entries:

```json
"routes": [
  {
    "Network": "192.168.1.0/24",
    "NextHop": "Ethernet0",
    "NextHopIP": null,
    "Protocol": "CONNECTED"
  }
]
```

### Layer 3 Topology

This section shows Layer 3 connections between devices:

```json
"layer3_topology": [
  {
    "Node1": "device1",
    "Interface1": "Ethernet0",
    "Node2": "device2",
    "Interface2": "Ethernet1"
  }
]
```

### Undefined References

This section shows references to undefined objects:

```json
"undefined_references": [
  {
    "Structure_Type": "ACL",
    "Structure_Name": "acl1",
    "File_Name": "configs/device1.cfg",
    "Line_Text": "permit ip any any"
  }
]
```

## Analyzing a Device Configuration

You can also retrieve and analyze a device configuration in one step using the `/analysis/device` endpoint:

```json
{
  "host": "192.168.1.1",
  "username": "admin",
  "password": "password",
  "method": "ssh"
}
```

## Best Practices

- Run analysis before deploying changes to production
- Focus on specific sections of the analysis relevant to your changes
- Compare analysis results before and after changes
- Use the analysis to identify potential issues with routing, addressing, and ACLs