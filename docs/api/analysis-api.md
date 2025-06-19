# Analysis API

The Analysis API allows you to analyze network configurations using Batfish.

## Endpoints

### Analyze Configuration

Analyze a network configuration.

**Endpoint:** `POST /analysis/config`

**Request Body:**

```json
{
  "config": "interface Ethernet0\n  ip address 192.168.1.1/24\n  no shutdown"
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| config | string | Yes | Configuration to analyze |

**Response:**

```json
{
  "status": "success",
  "analysis": {
    "interfaces": [
      {
        "Interface": "Ethernet0",
        "VRF": "default",
        "Primary_Address": "192.168.1.1/24",
        "Access_VLAN": null,
        "Active": true
      }
    ],
    "ip_owners": [
      {
        "IP": "192.168.1.1",
        "Interface": "Ethernet0",
        "Node": "device1"
      }
    ],
    "routes": [],
    "layer3_topology": [],
    "undefined_references": []
  }
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 500 | Server error |

### Analyze Device Configuration

Retrieve and analyze a device's configuration.

**Endpoint:** `POST /analysis/device`

**Request Body:**

```json
{
  "host": "192.168.1.1",
  "username": "admin",
  "password": "password",
  "method": "ssh",
  "ssh_port": 22
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| host | string | Yes | Device hostname or IP address |
| username | string | Yes | Username for authentication |
| password | string | Yes | Password for authentication |
| method | string | No | Configuration retrieval method: "ssh", "gnmi", or "both" (default: "ssh") |
| ssh_port | integer | No | SSH port (default: 22) |
| private_key_path | string | No | Path to SSH private key file for key-based authentication |

**Response:**

```json
{
  "status": "success",
  "config": {
    "ssh": {
      "running_config": "interface Ethernet0\n  mtu 9100\n  no shutdown",
      "version_info": "SONiC 4.0.0",
      "interfaces": "Ethernet0 up",
      "source": "ssh"
    }
  },
  "analysis": {
    "interfaces": [
      {
        "Interface": "Ethernet0",
        "VRF": "default"
      }
    ],
    "ip_owners": [],
    "routes": [],
    "layer3_topology": [],
    "undefined_references": []
  }
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 500 | Server error |