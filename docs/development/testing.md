# Testing Guide

This guide explains how to write and run tests for Spatium.

For comprehensive API usage examples with curl commands and device management scenarios, see the [Usage Guide](../usage.md).

## Testing Framework

Spatium uses [pytest](https://docs.pytest.org/) as its testing framework, along with [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) for testing asynchronous code.

## Test Structure

Tests are organized into three categories:

1. **Unit Tests**: Test individual components in isolation
   - Located in `tests/unit/`
   - Mock all external dependencies

2. **Integration Tests**: Test interactions between components
   - Located in `tests/integration/`
   - May use real dependencies or mocks

3. **End-to-End Tests**: Test the entire application
   - Located in `tests/`
   - Use the FastAPI TestClient

## Running Tests

### Run all tests:

```bash
pytest
```

### Run specific test categories:

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run a specific test file
pytest tests/unit/test_ssh_client.py

# Run a specific test
pytest tests/unit/test_ssh_client.py::TestSonicSSHClient::test_get_config_success
```

### Run with code coverage:

```bash
pytest --cov=src
```

## Writing Tests

### Unit Tests

Example unit test for a function:

```python
# tests/unit/test_batfish_analyzer.py
import pytest
from unittest.mock import patch, MagicMock
from src.analysis.batfish_analyzer import analyze_config_with_batfish

def test_analyze_config_with_batfish():
    # Mock dependencies
    with patch("src.analysis.batfish_analyzer.bf_set_network") as mock_set_network:
        # Set up mocks

        # Call the function
        result = analyze_config_with_batfish("config data")

        # Assert expectations
        assert "interfaces" in result
```

### Integration Tests

Example integration test for an API endpoint:

```python
# tests/integration/test_device_api.py
def test_get_device_config(client, mock_ssh_client):
    # Prepare request data
    data = {
        "host": "192.168.1.1",
        "username": "admin",
        "password": "password",
        "method": "ssh"
    }

    # Make request
    response = client.post("/device/config", json=data)

    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert "ssh" in response_data
```

### Testing Async Functions

Use the `pytest.mark.asyncio` decorator for testing async functions:

```python
# tests/unit/test_ssh_client.py
import pytest
from unittest.mock import AsyncMock, patch
from spatium.clients.ssh_client import SonicSSHClient

@pytest.mark.asyncio
async def test_get_config_success():
    # Mock asyncssh
    with patch("asyncssh.connect") as mock_connect:
        # Setup mock

        # Call async function
        client = SonicSSHClient()
        result = await client.get_config(
            host="192.168.1.1",
            username="admin",
            password="password"
        )

        # Assert expectations
```

## Fixtures

Common test fixtures are defined in `tests/conftest.py`:

```python
# Example fixtures
@pytest.fixture
def client():
    """Test client for the FastAPI application"""
    return TestClient(app)

@pytest.fixture
def mock_ssh_client():
    """Mock for the SSH client"""
    with patch("spatium.clients.ssh_client.SonicSSHClient") as mock:
        # Setup mock
        yield mock
```

## Mocking

Use `unittest.mock` for mocking dependencies:

```python
# Mocking a function
with patch("module.function") as mock_function:
    mock_function.return_value = "expected result"

# Mocking a class
with patch("module.Class") as MockClass:
    instance = MockClass.return_value
    instance.method.return_value = "expected result"

# Mocking async functions
with patch("module.async_function") as mock_async:
    mock_async.return_value = AsyncMock(return_value="expected result")
```

## Best Practices

1. Write tests before or alongside code (TDD)
2. Keep tests small and focused
3. Use descriptive test names that explain what is being tested
4. Use fixtures for common setup
5. Mock external dependencies
6. Test error conditions, not just happy paths
7. Aim for high code coverage, but focus on testing behavior
8. Regularly run the full test suite

## Manual API Testing with curl

This section provides sample curl commands for testing the Spatium API endpoints manually.

### Prerequisites

Make sure the Spatium API server is running:

```bash
cd /home/clab/tomek/av
uvicorn spatium.main:app --reload --host 0.0.0.0 --port 8000
```

### Lab1 Inventory Sample Commands

#### Add Multiple Devices to lab1 Inventory (Bulk Operation)

```bash
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "host": "172.20.0.61",
      "username": "admin",
      "password": "admin",
      "port": 22,
      "device_model": "sonic"
    },
    {
      "host": "172.20.0.62",
      "username": "admin",
      "password": "admin",
      "port": 22,
      "device_model": "sonic"
    },
    {
      "host": "172.20.0.65",
      "username": "admin",
      "password": "admin",
      "port": 22,
      "device_model": "sonic"
    },
    {
      "host": "172.20.0.66",
      "username": "admin",
      "password": "admin",
      "port": 22,
      "device_model": "sonic"
    },
    {
      "host": "172.20.0.67",
      "username": "admin",
      "password": "admin",
      "port": 22,
      "device_model": "sonic"
    },
    {
      "host": "172.20.0.68",
      "username": "admin",
      "password": "admin",
      "port": 22,
      "device_model": "sonic"
    }
  ]'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully added 6 device(s) to inventory",
  "inventory": "lab1",
  "affected_hosts": [
    "172.20.0.61",
    "172.20.0.62",
    "172.20.0.65",
    "172.20.0.66",
    "172.20.0.67",
    "172.20.0.68"
  ]
}
```

#### Add Single Device to lab1 Inventory

```bash
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "172.20.0.61",
    "username": "admin",
    "password": "admin",
    "port": 22,
    "device_model": "sonic"
  }'
```

#### List All Devices in lab1 Inventory

```bash
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
[
  {
    "host": "172.20.0.61",
    "username": "admin",
    "password": "admin",
    "port": 22,
    "device_model": "sonic"
  },
  {
    "host": "172.20.0.62",
    "username": "admin",
    "password": "admin",
    "port": 22,
    "device_model": "sonic"
  }
  // ... additional devices
]
```

#### Get Configurations from lab1 Inventory

Retrieve configurations from all devices in the lab1 inventory:

```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully retrieved configurations from 6 device(s)",
  "inventory": "lab1",
  "configs": {
    "172.20.0.61": {
      "status": "success",
      "config": "!\n! Configuration for device 172.20.0.61\n! Device: sonic\n...",
      "timestamp": "2025-07-01T10:30:00Z"
    },
    "172.20.0.62": {
      "status": "success",
      "config": "!\n! Configuration for device 172.20.0.62\n! Device: sonic\n...",
      "timestamp": "2025-07-01T10:30:15Z"
    },
    "172.20.0.65": {
      "status": "error",
      "error": "Connection timeout",
      "timestamp": "2025-07-01T10:30:30Z"
    }
    // ... additional devices
  },
  "summary": {
    "total_devices": 6,
    "successful": 5,
    "failed": 1
  }
}
```

#### Get Configuration from Specific Devices in lab1

Retrieve configuration from specific devices (subset of lab1 inventory):

```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "hosts": ["172.20.0.61", "172.20.0.62"]
  }'
```

#### Save Configurations from lab1 Inventory

Save all configurations from lab1 inventory to the `lab1` folder:

```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully saved configurations for 6 device(s) to lab1 folder",
  "inventory": "lab1",
  "save_location": "./configs/lab1/",
  "saved_files": {
    "172.20.0.61": {
      "status": "saved",
      "filename": "172.20.0.61_sonic_config.txt",
      "path": "./configs/lab1/172.20.0.61_sonic_config.txt",
      "size_bytes": 15420
    },
    "172.20.0.62": {
      "status": "saved",
      "filename": "172.20.0.62_sonic_config.txt",
      "path": "./configs/lab1/172.20.0.62_sonic_config.txt",
      "size_bytes": 15380
    },
    "172.20.0.65": {
      "status": "error",
      "error": "No configuration available to save"
    }
    // ... additional devices
  },
  "summary": {
    "total_devices": 6,
    "files_saved": 5,
    "failed": 1
  }
}
```

#### Save Configurations with Custom Format

Save configurations with specific filename format:

```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "filename_format": "{host}_{device_model}_{timestamp}",
    "file_extension": "cfg",
    "include_timestamp": true
  }'
```

#### Save Configurations to Custom Directory

Save configurations to a specific subdirectory within lab1:

```bash
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "subdirectory": "backup_2025_07_01",
    "create_subdirectory": true
  }'
```

This will save files to: `./configs/lab1/backup_2025_07_01/`

#### Get and Save Configurations in One Operation

Chain operations to get and immediately save configurations:

```bash
# Get configurations and save them
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" && \
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json"
```

#### Remove Device from lab1 Inventory

```bash
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/remove?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "172.20.0.61",
    "username": "admin",
    "password": "admin",
    "port": 22,
    "device_model": "sonic"
  }'
```

#### Clear All Devices from lab1 Inventory

```bash
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/clear?inventory=lab1" \
  -H "Content-Type: application/json"
```

### Other Inventory Operations

#### Test with Default Inventory

```bash
# Add device to default inventory (no inventory parameter)
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.1",
    "username": "admin",
    "password": "admin",
    "port": 22,
    "device_model": "cisco"
  }'

# List devices in default inventory
curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list" \
  -H "Content-Type: application/json"
```

#### Test Error Scenarios

```bash
# Test invalid device model
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "172.20.0.61",
    "username": "admin",
    "password": "admin",
    "port": 22,
    "device_model": "invalid_model"
  }'

# Test missing required fields
curl --noproxy localhost -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin",
    "port": 22,
    "device_model": "sonic"
  }'
```

### Testing Tips

1. **Check Response Status**: Use `-w "%{http_code}"` to see HTTP status codes:
   ```bash
   curl --noproxy localhost -w "%{http_code}" -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1"
   ```

2. **Pretty Print JSON**: Use `jq` for readable JSON output:
   ```bash
   curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1" | jq .
   ```

3. **Save Response to File**: Use `-o` to save responses:
   ```bash
   curl --noproxy localhost -X GET "http://localhost:8000/topology/inventory/list?inventory=lab1" -o lab1_devices.json
   ```

4. **Verbose Output**: Use `-v` for detailed request/response information:
   ```bash
   curl --noproxy localhost -v -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
     -H "Content-Type: application/json" \
     -d '{"host": "172.20.0.61", "username": "admin", "password": "admin", "port": 22, "device_model": "sonic"}'
   ```

### Configuration Management Examples

#### Verify Saved Configuration Files

After saving configurations, you can verify the files were created:

```bash
# List files in the lab1 configuration directory
ls -la ./configs/lab1/

# Check file contents
cat ./configs/lab1/172.20.0.61_sonic_config.txt

# Count lines in configuration file
wc -l ./configs/lab1/172.20.0.61_sonic_config.txt
```

#### Compare Configurations

Get configurations at different times and compare:

```bash
# Save current configurations with timestamp
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "subdirectory": "baseline_$(date +%Y%m%d_%H%M%S)",
    "create_subdirectory": true
  }'

# Later, save again for comparison
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "subdirectory": "current_$(date +%Y%m%d_%H%M%S)",
    "create_subdirectory": true
  }'
```

#### Bulk Configuration Operations

```bash
# Get configurations from multiple inventories
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" && \
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=lab2" \
  -H "Content-Type: application/json"

# Save configurations from multiple inventories
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" && \
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=lab2" \
  -H "Content-Type: application/json"
```

#### Configuration Validation

Check if configurations were retrieved successfully:

```bash
# Get configurations and check response
response=$(curl --noproxy localhost -s -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json")

# Extract success status using jq
echo $response | jq '.success'

# Count successful configurations
echo $response | jq '.summary.successful'

# List failed devices
echo $response | jq -r '.configs | to_entries[] | select(.value.status == "error") | .key'
```

#### Error Handling Examples

Test various error scenarios:

```bash
# Test with non-existent inventory
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=nonexistent" \
  -H "Content-Type: application/json"

# Test with empty inventory
curl --noproxy localhost -X POST "http://localhost:8000/configs/get?inventory=empty_lab" \
  -H "Content-Type: application/json"

# Test save without prior configuration retrieval
curl --noproxy localhost -X POST "http://localhost:8000/configs/save?inventory=new_lab" \
  -H "Content-Type: application/json"
```

### Environment Variables

You can set environment variables to make testing easier:

```bash
export SPATIUM_BASE_URL="http://localhost:8000"
export LAB1_INVENTORY="lab1"

# Then use in curl commands
curl --noproxy localhost -X GET "${SPATIUM_BASE_URL}/topology/inventory/list?inventory=${LAB1_INVENTORY}"
```
