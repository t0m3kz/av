# Spatium API Usage Guide

This document provides comprehensive examples of using the Spatium API with curl commands for device configuration management, inventory operations, and topology management.

## Prerequisites

- Spatium API server running on `http://localhost:8000`
- Access to network devices (e.g., SONiC switches)
- Proper network connectivity to target devices

## API Base URL

All examples use the base URL: `http://localhost:8000`

**Important**: All curl commands include `--noproxy localhost` to bypass proxy settings that might interfere with local API calls.

## Inventory Management

### 1. Adding Devices to Inventory

#### Add Single Device
```bash
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.61",
    "device_model": "sonic",
    "username": "admin",
    "password": "admin"
  }'
```

#### Add Multiple Devices (Bulk Operation)
```bash
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "ip_address": "172.20.0.61",
        "device_model": "sonic",
        "username": "admin",
        "password": "admin"
      },
      {
        "ip_address": "172.20.0.62",
        "device_model": "sonic",
        "username": "admin",
        "password": "admin"
      }
    ]
  }'
```

#### Add Device with Custom SSH Port
```bash
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.65",
    "device_model": "sonic",
    "username": "admin",
    "password": "admin",
    "ssh_port": 2022
  }'
```

### 2. Listing Inventory Devices

#### List All Devices in Inventory
```bash
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1"
```

#### List Devices with Filtering
```bash
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1&device_model=sonic"
```

### 3. Removing Devices from Inventory

#### Remove Single Device by IP Address
```bash
curl --noproxy localhost -X DELETE "http://localhost:8000/topology/inventory/remove?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.65"
  }'
```

#### Remove Multiple Devices (Bulk Operation)
```bash
curl --noproxy localhost -X DELETE "http://localhost:8000/topology/inventory/remove?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {"ip_address": "172.20.0.65"},
      {"ip_address": "172.20.0.66"},
      {"ip_address": "172.20.0.67"}
    ]
  }'
```

#### Remove Device by ID
```bash
curl --noproxy localhost -X DELETE "http://localhost:8000/topology/inventory/remove?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device-uuid-here"
  }'
```

### 4. Updating Device Information

#### Update Device Credentials
```bash
curl --noproxy localhost -X PUT "http://localhost:8000/topology/inventory/update?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.61",
    "username": "newuser",
    "password": "newpassword"
  }'
```

#### Update Device Model
```bash
curl --noproxy localhost -X PUT "http://localhost:8000/topology/inventory/update?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.62",
    "device_model": "sonic",
    "description": "Updated SONiC spine switch"
  }'
```

## Configuration Management

### 1. Retrieving Device Configurations

#### Get Configurations from All Devices in Inventory
```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### Get Configuration from Specific Devices
```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "device_ips": ["172.20.0.61", "172.20.0.62"]
  }'
```

#### Get Configuration with Custom Timeout
```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "timeout": 60,
    "device_ips": ["172.20.0.61"]
  }'
```

### 2. Saving Configurations

#### Save Configurations to Default Location
```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### Save Configurations to Custom Directory
```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "output_dir": "/custom/backup/path",
    "include_timestamp": true
  }'
```

#### Save Specific Device Configurations
```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "device_ips": ["172.20.0.61", "172.20.0.62"],
    "format": "json"
  }'
```

## Device Health and Status

### 1. Check Device Connectivity
```bash
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/health?inventory=lab1"
```

### 2. Test SSH Connection to Specific Device
```bash
curl --noproxy localhost -X POST "http://localhost:8000/device/test-connection" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.61",
    "username": "admin",
    "password": "admin"
  }'
```

## Common Scenarios

### Scenario 1: Initial Lab Setup

1. **Create inventory and add devices:**
```bash
# Add first two devices
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "ip_address": "172.20.0.61",
        "device_model": "sonic",
        "username": "admin",
        "password": "admin"
      },
      {
        "ip_address": "172.20.0.62",
        "device_model": "sonic",
        "username": "admin",
        "password": "admin"
      }
    ]
  }'

# Verify devices were added
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1"
```

2. **Get initial configurations:**
```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

3. **Save configurations:**
```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Scenario 2: Scaling Up Lab (Adding More Devices)

```bash
# Add additional devices to existing lab
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "ip_address": "172.20.0.65",
        "device_model": "sonic",
        "username": "admin",
        "password": "admin"
      },
      {
        "ip_address": "172.20.0.66",
        "device_model": "sonic",
        "username": "admin",
        "password": "admin"
      },
      {
        "ip_address": "172.20.0.67",
        "device_model": "sonic",
        "username": "admin",
        "password": "admin"
      },
      {
        "ip_address": "172.20.0.68",
        "device_model": "sonic",
        "username": "admin",
        "password": "admin"
      }
    ]
  }'

# Verify all devices are present
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1"

# Get configurations from all devices
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Scenario 3: Scaling Down Lab (Removing Devices)

#### Remove Single Device (e.g., device failure)
```bash
# Remove a single failed device
curl --noproxy localhost -X DELETE "http://localhost:8000/topology/inventory/remove?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.68"
  }'

# Verify device was removed
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1"
```

#### Remove Multiple Devices (topology downsizing)
```bash
# Remove multiple devices at once
curl --noproxy localhost -X DELETE "http://localhost:8000/topology/inventory/remove?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {"ip_address": "172.20.0.65"},
      {"ip_address": "172.20.0.66"},
      {"ip_address": "172.20.0.67"}
    ]
  }'

# Verify devices were removed
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1"

# Get configurations from remaining devices
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Scenario 4: Device Maintenance (Temporary Removal)

#### Mark Device for Maintenance
```bash
# Update device status to maintenance mode
curl --noproxy localhost -X PUT "http://localhost:8000/topology/inventory/update?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.61",
    "status": "maintenance",
    "description": "Under maintenance - scheduled reboot"
  }'

# Get configurations from non-maintenance devices only
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "exclude_maintenance": true
  }'
```

#### Return Device from Maintenance
```bash
# Update device status back to active
curl --noproxy localhost -X PUT "http://localhost:8000/topology/inventory/update?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.61",
    "status": "active",
    "description": "Back online after maintenance"
  }'
```

### Scenario 5: Lab Migration (Moving Devices Between Inventories)

#### Step 1: Export device from source inventory
```bash
# Get device details from source inventory
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1" | \
  jq '.devices[] | select(.ip_address=="172.20.0.62")'
```

#### Step 2: Add device to destination inventory
```bash
# Add device to new inventory
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab2" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.62",
    "device_model": "sonic",
    "username": "admin",
    "password": "admin"
  }'
```

#### Step 3: Remove device from source inventory
```bash
# Remove device from old inventory
curl --noproxy localhost -X DELETE "http://localhost:8000/topology/inventory/remove?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "172.20.0.62"
  }'
```

## Error Handling Examples

### Handle Connection Failures
```bash
# Try to get configs with error handling
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "timeout": 30,
    "retry_count": 3,
    "continue_on_error": true
  }'
```

### Check API Status
```bash
# Check if API is running
curl --noproxy localhost -X GET "http://localhost:8000/health"

# Get API version info
curl --noproxy localhost -X GET "http://localhost:8000/version"
```

## Response Examples

### Successful Device Addition Response
```json
{
  "status": "success",
  "message": "Device added successfully",
  "device_id": "uuid-12345",
  "ip_address": "172.20.0.61"
}
```

### Configuration Retrieval Response
```json
{
  "status": "success",
  "results": [
    {
      "device_ip": "172.20.0.61",
      "hostname": "sonic-spine1-61",
      "status": "success",
      "config_size": 28456,
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ]
}
```

### Error Response Example
```json
{
  "status": "error",
  "message": "Device not reachable",
  "device_ip": "172.20.0.99",
  "error_code": "CONNECTION_TIMEOUT"
}
```

## Best Practices

1. **Always use `--noproxy localhost`** to avoid proxy issues with local API calls
2. **Check device connectivity** before adding to inventory
3. **Use bulk operations** when managing multiple devices
4. **Save configurations regularly** as backups
5. **Remove unreachable devices** to keep inventory clean
6. **Use descriptive names** for inventories (e.g., `lab1`, `production`, `staging`)
7. **Test API endpoints** with small requests before bulk operations
8. **Monitor response times** and adjust timeouts accordingly

## Troubleshooting

### Common Issues

1. **API not responding**: Check if server is running on port 8000
2. **Connection timeout**: Verify device IP addresses and network connectivity
3. **Authentication failure**: Check username/password credentials
4. **SSH connection refused**: Verify SSH service is running on target devices
5. **Configuration too large**: Increase timeout values for large configurations

### Debug Commands

```bash
# Check API server status
curl --noproxy localhost -X GET "http://localhost:8000/health"

# Test device connectivity
ping 172.20.0.61

# Test SSH connection manually
ssh admin@172.20.0.61

# Check API logs (if available)
tail -f /var/log/spatium-api.log
```
