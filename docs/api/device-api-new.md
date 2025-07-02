# Device API

The Device API provides comprehensive device inventory management and configuration retrieval capabilities.

## Base URL Structure

All device-related endpoints are available under the main router with the following structure:
- Inventory management: `/topology/inventory/*`
- Configuration retrieval: `/configs/*`

## Inventory Management

### Add Devices to Inventory

**POST** `/topology/inventory/add`

Add one or more devices to a named inventory.

**Query Parameters:**
- `inventory` (string, optional): Inventory name (default: "default")

**Request Body:**
```json
{
  "host": "192.168.1.1",
  "username": "admin",
  "password": "admin123",
  "port": 22,
  "device_model": "sonic",
  "method": "ssh",
  "private_key": null,
  "rest_url": null
}
```

Or an array of device objects for bulk operations.

**Response:**
```json
{
  "success": true,
  "message": "Successfully added 1 device(s) to inventory",
  "inventory": "default",
  "affected_hosts": ["192.168.1.1"]
}
```

### List Devices in Inventory

**GET** `/topology/inventory/list`

List all devices in a specific inventory.

**Query Parameters:**
- `inventory` (string, optional): Inventory name (default: "default")

**Response:**
```json
[
  {
    "host": "192.168.1.1",
    "username": "admin",
    "password": "admin123",
    "port": 22,
    "device_model": "sonic",
    "method": "ssh",
    "private_key": null,
    "rest_url": null
  }
]
```

### Remove Devices from Inventory

**POST** `/topology/inventory/remove`

Remove one or more devices from a named inventory.

**Query Parameters:**
- `inventory` (string, optional): Inventory name (default: "default")

**Request Body:**
Same format as add operation - devices with matching hosts will be removed.

**Response:**
```json
{
  "success": true,
  "message": "Successfully removed 1 device(s) from inventory",
  "inventory": "default",
  "affected_hosts": ["192.168.1.1"]
}
```

### Clear Inventory

**POST** `/topology/inventory/clear`

Remove all devices from a specific inventory.

**Query Parameters:**
- `inventory` (string, optional): Inventory name (default: "default")

**Response:**
```json
{
  "success": true,
  "message": "Successfully cleared 5 device(s) from inventory",
  "inventory": "default",
  "affected_hosts": []
}
```

### List Inventory Names

**GET** `/topology/inventory/names`

Get a list of all configured inventory names.

**Response:**
```json
["default", "production", "staging", "development"]
```

### Get Inventory Statistics

**GET** `/topology/inventory/stats`

Get statistics for a specific inventory.

**Query Parameters:**
- `inventory` (string, optional): Inventory name (default: "default")

**Response:**
```json
{
  "total_devices": 10,
  "device_models": {
    "sonic": 5,
    "cisco": 3,
    "arista": 2
  }
}
```

## Configuration Retrieval

### Get Device Configurations

**POST** `/configs/get`

Fetch running configurations from devices in an inventory.

**Query Parameters:**
- `inventory` (string, optional): Inventory name (default: "default")
- `host` (string, optional): Filter by specific host IP

**Response:**
```json
{
  "success": true,
  "message": "Retrieved configurations for 3 device(s)",
  "inventory": "default",
  "results": [
    {
      "host": "192.168.1.1",
      "running_config": "! Configuration data...",
      "source": "ssh",
      "error": null
    }
  ],
  "messages": [
    "Configuration fetched for 192.168.1.1"
  ]
}
```

### Save Device Configurations

**POST** `/configs/save`

Fetch configurations and save them to files.

**Query Parameters:**
- `inventory` (string, optional): Inventory name (default: "default")
- `host` (string, optional): Filter by specific host IP
- `output_folder` (string, optional): Output directory (default: "outputs")

**Response:**
```json
{
  "success": true,
  "message": "Saved configurations for 3/3 device(s)",
  "inventory": "default",
  "results": [
    {
      "host": "192.168.1.1",
      "source": "ssh",
      "error": null,
      "message": "Configuration for host 192.168.1.1 saved to outputs/192.168.1.1_config.txt",
      "file_path": "outputs/192.168.1.1_config.txt"
    }
  ]
}
```

## Supported Device Types

The API supports the following device types with appropriate configuration commands:

- **SONiC**: `show runningconfiguration all`
- **Cisco IOS/XE/NXOS**: `show running-config`
- **Arista EOS**: `show running-config`
- **Juniper**: `show configuration`
- **Nokia SR OS**: `show running-configuration`
- **Huawei**: `display current-configuration`
- **VyOS**: `show configuration`
- **Cumulus Linux**: `show running-config`
- **Linux variants**: Various network config file commands

## Connection Methods

### SSH (Default)
Uses SSH to connect to devices and execute configuration commands.

### REST API
For devices supporting REST APIs, specify `"method": "rest"` in the device configuration.

Custom REST URLs can be provided via the `rest_url` field, otherwise default endpoints are used based on device model.

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Device connection failed",
  "details": {
    "host": "192.168.1.1",
    "reason": "Authentication failed"
  }
}
```

Common error scenarios:
- Device unreachable
- Authentication failures
- Unsupported device types
- Configuration retrieval timeouts

## Examples

### Python Client Example

```python
import requests

base_url = "http://localhost:8000"

# Add a device
device = {
    "host": "192.168.1.1",
    "username": "admin",
    "password": "admin123",
    "device_model": "sonic"
}

response = requests.post(f"{base_url}/topology/inventory/add", json=device)
print(response.json())

# Get configurations
response = requests.post(f"{base_url}/configs/get")
configs = response.json()

for result in configs["results"]:
    if result["error"]:
        print(f"Error for {result['host']}: {result['error']}")
    else:
        print(f"Config for {result['host']}: {len(result['running_config'])} characters")
```

### cURL Examples

```bash
# Add device to inventory
curl -X POST "http://localhost:8000/topology/inventory/add" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.1",
    "username": "admin",
    "password": "admin123",
    "device_model": "sonic"
  }'

# List devices
curl "http://localhost:8000/topology/inventory/list"

# Get configurations
curl -X POST "http://localhost:8000/configs/get"

# Save configurations to files
curl -X POST "http://localhost:8000/configs/save?output_folder=my_configs"
```

### Bulk Operations

```bash
# Add multiple devices
curl -X POST "http://localhost:8000/topology/inventory/add" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "host": "192.168.1.1",
      "username": "admin",
      "password": "admin123",
      "device_model": "sonic"
    },
    {
      "host": "192.168.1.2",
      "username": "admin",
      "password": "admin123",
      "device_model": "arista"
    }
  ]'

# Get configs for specific host
curl -X POST "http://localhost:8000/configs/get?host=192.168.1.1"

# Save configs to custom folder
curl -X POST "http://localhost:8000/configs/save?output_folder=backup_configs"
```

### Multiple Inventories

```bash
# Add device to custom inventory
curl -X POST "http://localhost:8000/topology/inventory/add?inventory=production" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "10.0.1.1",
    "username": "admin",
    "password": "secure123",
    "device_model": "cisco"
  }'

# List devices in specific inventory
curl "http://localhost:8000/topology/inventory/list?inventory=production"

# Get configs from specific inventory
curl -X POST "http://localhost:8000/configs/get?inventory=production"
```
