# Device Configuration

This guide explains how to retrieve configurations from network devices using Spatium.

## Supported Methods

Spatium supports two methods for retrieving device configurations:

1. **SSH** - Traditional CLI-based configuration retrieval
2. **gNMI** - Model-based configuration retrieval using gNMI (gRPC Network Management Interface)

## SSH Configuration Retrieval

SSH retrieval works by connecting to the device's CLI and executing show commands.

### Example Request

```json
{
  "host": "192.168.1.1",
  "username": "admin",
  "password": "password",
  "method": "ssh",
  "ssh_port": 22
}
```

### SSH Authentication Options

- **Password authentication**: Provide `username` and `password`
- **Key-based authentication**: Provide `username` and `private_key_path`

### SSH Commands

Spatium executes these commands on SONiC devices:

- `show running-configuration` - Get running config
- `show version` - Get version information
- `show interfaces status` - Get interface status

## gNMI Configuration Retrieval

gNMI retrieval uses the gRPC Network Management Interface to retrieve structured data.

### Example Request

```json
{
  "host": "192.168.1.1",
  "username": "admin",
  "password": "password",
  "method": "gnmi",
  "gnmi_port": 8080,
  "gnmi_paths": [
    "/openconfig-interfaces:interfaces",
    "/sonic-device-metadata:sonic-device-metadata"
  ]
}
```

### Default gNMI Paths

If no paths are specified, these default paths are used:

- `/openconfig-interfaces:interfaces`
- `/sonic-device-metadata:sonic-device-metadata`
- `/sonic-port:sonic-port`

## Using Both Methods

You can retrieve configurations using both methods simultaneously:

```json
{
  "host": "192.168.1.1",
  "username": "admin",
  "password": "password",
  "method": "both",
  "ssh_port": 22,
  "gnmi_port": 8080
}
```

## Error Handling

If a connection fails, the response will include an error message:

```json
{
  "ssh": {
    "error": "Connection failed: Connection refused",
    "source": "ssh"
  }
}
```

## Best Practices

- Use SSH for text-based configurations and quick checks
- Use gNMI for structured data and programmatic configuration management
- Store credentials securely and consider using environment variables
- Use key-based authentication when possible