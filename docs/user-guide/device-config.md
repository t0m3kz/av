# Device Configuration

This guide explains how to retrieve configurations from network devices using Spatium.

## Supported Methods

Spatium supports only SSH for retrieving device configurations.

1. **SSH** - Traditional CLI-based configuration retrieval

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

## Device Model Selection

You can specify the `device_model` parameter to tell Spatium which command to use for retrieving the configuration.
Supported values include: `sonic`, `cisco`, `arista`, `juniper`, `huawei`, `linux`, and more.

### Example Request with Device Model

```json
{
  "host": "192.168.1.1",
  "username": "admin",
  "password": "password",
  "device_model": "cisco",
  "port": 22
}
```

## Example: Retrieving Config from Multiple Devices

You can retrieve the configuration from multiple devices in parallel using the `/device/config` endpoint.

```bash
curl -X POST "http://localhost:8000/device/config" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "host": "172.20.0.65",
      "username": "admin",
      "password": "password",
      "method": "ssh",
      "ssh_port": 22
    },
    {
      "host": "172.20.0.66",
      "username": "admin",
      "password": "admin",
      "method": "ssh",
      "ssh_port": 22
    },
    {
      "host": "172.20.0.67",
      "username": "admin",
      "password": "admin",
      "method": "ssh",
      "ssh_port": 22
    },
    {
      "host": "172.20.0.68",
      "username": "admin",
      "password": "admin",
      "method": "ssh",
      "ssh_port": 22
    }
  ]'
```

### Save the Output to a File

To save the response to a file (e.g., `configs.json`):

```bash
curl -X POST "http://localhost:8000/device/config" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "host": "172.20.0.65",
      "username": "admin",
      "password": "admin",
      "method": "ssh",
      "ssh_port": 22
    },
    {
      "host": "172.20.0.66",
      "username": "admin",
      "password": "admin",
      "method": "ssh",
      "ssh_port": 22
    },
    {
      "host": "172.20.0.67",
      "username": "admin",
      "password": "admin",
      "method": "ssh",
      "ssh_port": 22
    },
    {
      "host": "172.20.0.68",
      "username": "admin",
      "password": "admin",
      "method": "ssh",
      "ssh_port": 22
    }
  ]' -o configs.json
```

The response will be saved in `configs.json`.

## Error Handling

If a connection fails, the response will include an error message:

```json
{
  "host": "172.20.0.65",
  "error": "Failed to get device configuration: Connection refused"
}
```

## Best Practices

- Use SSH for text-based configurations and quick checks
- Store credentials securely and consider using environment variables
- Use key-based authentication when possible
