# Device API

The Device API allows you to retrieve configuration from network devices running SONiC OS.

## Endpoints

### Get Device Configuration

Retrieve configuration from a SONiC device using SSH, gNMI, or both methods.

**Endpoint:** `POST /device/config`

**Request Body:**

```json
{
  "host": "192.168.1.1",
  "username": "admin",
  "password": "password",
  "method": "both",
  "ssh_port": 22,
  "gnmi_port": 8080,
  "private_key_path": null,
  "gnmi_paths": null
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| host | string | Yes | Device hostname or IP address |
| username | string | Yes | Username for authentication |
| password | string | Yes | Password for authentication |
| method | string | No | Configuration retrieval method: "ssh", "gnmi", or "both" (default: "both") |
| ssh_port | integer | No | SSH port (default: 22) |
| gnmi_port | integer | No | gNMI port (default: 8080) |
| private_key_path | string | No | Path to SSH private key file for key-based authentication |
| gnmi_paths | array | No | List of gNMI paths to query |

**Response:**

```json
{
  "ssh": {
    "running_config": "interface Ethernet0\n  mtu 9100\n  no shutdown",
    "version_info": "SONiC 4.0.0",
    "interfaces": "Ethernet0 up",
    "source": "ssh"
  },
  "gnmi": {
    "gnmi_data": {
      "path": "openconfig-interfaces:interfaces",
      "data": {}
    },
    "source": "gnmi"
  }
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 500 | Server error |