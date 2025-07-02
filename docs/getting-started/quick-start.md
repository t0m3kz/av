# Quick Start Guide

Get up and running with Spatium in just a few minutes! This guide walks you through the essential operations to start managing your network devices.

## Prerequisites

Before starting, ensure you have:
- ✅ [Installed Spatium](installation.md)
- ✅ Access to at least one SONiC device
- ✅ Network connectivity to your devices

## Step 1: Start the API Server

Launch the Spatium API server:

```bash
# Navigate to your Spatium directory
cd /path/to/spatium

# Start the server (development mode with auto-reload)
uvicorn spatium.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output similar to:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

🎉 **Your API is now running!**
- **API Endpoint**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc

## Step 2: Create Your First Inventory

Inventories help you organize devices by environment, role, or project. Let's create a "lab" inventory:

```bash
# Add your first device to the lab inventory
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.10",
    "device_model": "sonic",
    "username": "admin",
    "password": "admin"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully added 1 device(s) to inventory",
  "inventory": "lab",
  "affected_hosts": ["192.168.1.10"]
}
```

### Add Multiple Devices at Once

You can also add multiple devices in a single request:

```bash
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "host": "192.168.1.10",
      "device_model": "sonic",
      "username": "admin",
      "password": "admin"
    },
    {
      "host": "192.168.1.11",
      "device_model": "sonic",
      "username": "admin",
      "password": "admin"
    }
  ]'
```

## Step 3: Verify Your Inventory

Check that your devices were added successfully:

```bash
# List all devices in the lab inventory
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab"
```

**Expected Response:**
```json
[
  {
    "host": "192.168.1.10",
    "username": "admin",
    "password": "admin",
    "port": 22,
    "private_key": null,
    "device_model": "sonic",
    "method": "ssh",
    "rest_url": null
  }
]
```

## Step 4: Retrieve Device Configurations

Now let's fetch configurations from your devices:

```bash
# Get configurations from all devices in the lab inventory
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**What happens here:**
- Spatium connects to each device via SSH
- Executes the appropriate command for SONiC devices
- Retrieves the running configuration
- Returns structured JSON data

**Sample Response:**
```json
{
  "success": true,
  "message": "Retrieved configurations for 1 device(s)",
  "inventory": "lab",
  "results": [
    {
      "host": "192.168.1.10",
      "running_config": "{\n  \"DEVICE_METADATA\": {\n    \"localhost\": {\n      \"hostname\": \"sonic-switch\",\n      \"platform\": \"x86_64-kvm_x86_64-r0\"\n    }\n  }\n}",
      "source": "ssh",
      "error": null
    }
  ]
}
```

### Get Configuration from Specific Devices

You can also target specific devices:

```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab" \
  -H "Content-Type: application/json" \
  -d '{
    "device_ips": ["192.168.1.10"]
  }'
```

## Step 5: Save Configurations to Files

Save the retrieved configurations as backup files:

```bash
# Save configurations to the default outputs directory
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Saved configurations for 1/1 device(s)",
  "inventory": "lab",
  "results": [
    {
      "host": "192.168.1.10",
      "source": "ssh",
      "error": null,
      "message": "Configuration for host 192.168.1.10 saved to outputs/192.168.1.10_config.txt",
      "file_path": "outputs/192.168.1.10_config.txt"
    }
  ]
}
```

### Check Your Saved Files

```bash
# List the saved configuration files
ls -la outputs/

# View a configuration file
head -20 outputs/192.168.1.10_config.txt
```

## Step 6: Explore the Web Interface

Open your browser and visit http://localhost:8000/docs to explore the interactive API documentation. You can:

- 📋 Browse all available endpoints
- 🧪 Test API calls directly in the browser
- 📖 Read detailed parameter descriptions
- 💡 See example requests and responses

## Common Operations

### Managing Inventories

```bash
# List all inventory names
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/names"

# Get inventory statistics
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/stats?inventory=lab"

# Clear an inventory (remove all devices)
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/clear?inventory=lab"
```

### Device Management

```bash
# Remove a specific device
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/remove?inventory=lab" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.10",
    "device_model": "sonic",
    "username": "admin",
    "password": "admin"
  }'

# Remove multiple devices
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/remove?inventory=lab" \
  -H "Content-Type: application/json" \
  -d '[
    {"host": "192.168.1.10", "device_model": "sonic", "username": "admin", "password": "admin"},
    {"host": "192.168.1.11", "device_model": "sonic", "username": "admin", "password": "admin"}
  ]'
```

## Troubleshooting

### Connection Issues

If you can't connect to devices:

```bash
# Test SSH connectivity manually
ssh admin@192.168.1.10

# Check if the device is reachable
ping 192.168.1.10

# Verify credentials are correct
```

### API Issues

If the API isn't responding:

```bash
# Check if the server is running
curl http://localhost:8000/docs

# Check server logs in the terminal where you started uvicorn
```

### Common Error Responses

- **404 Not Found**: Check your endpoint URL
- **422 Validation Error**: Check your request body format
- **500 Internal Server Error**: Check device connectivity and credentials

## Next Steps

Congratulations! You've successfully:
- ✅ Started the Spatium API server
- ✅ Created your first device inventory
- ✅ Retrieved device configurations
- ✅ Saved configuration backups

### What's Next?

1. **[Explore Advanced Features](../user-guide/overview.md)** - Learn about digital twins and analysis
2. **[Complete API Reference](../usage.md)** - Comprehensive examples and scenarios
3. **[Configuration Management](../user-guide/device-config.md)** - Advanced device management
4. **[Integration Guide](../development/api-architecture.md)** - Integrate with your existing tools

### Pro Tips

- 💡 Use different inventory names for different environments (dev, staging, prod)
- 🔄 Set up scheduled configuration backups using cron jobs
- 📊 Monitor your API with the built-in logging
- 🛡️ Always use secure credentials in production environments

Ready to dive deeper? Check out the [comprehensive usage guide](../usage.md) for advanced scenarios and automation examples!

Use the `/analysis/config` endpoint to analyze a configuration:

```bash
curl -X POST http://localhost:8000/analysis/config \
  -H "Content-Type: application/json" \
  -d '{
    "config": "interface Ethernet0\n  ip address 192.168.1.1/24\n  no shutdown"
  }'
```

## Deploying a Digital Twin

Use the `/deployment/deploy` endpoint to deploy a digital twin:

```bash
curl -X POST http://localhost:8000/deployment/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sonic-test",
    "nodes": [
      {
        "name": "sonic1",
        "type": "sonic-vs",
        "image": "docker-sonic-vs:latest"
      },
      {
        "name": "sonic2",
        "type": "sonic-vs",
        "image": "docker-sonic-vs:latest"
      }
    ],
    "links": [
      {
        "node1": "sonic1",
        "interface1": "eth1",
        "node2": "sonic2",
        "interface2": "eth1"
      }
    ]
  }'
```

## Next Steps

- Learn more about [configuration analysis](../user-guide/config-analysis.md)
- Explore [digital twins](../user-guide/digital-twins.md)
- Check out the [API reference](../api/device-api.md)