# Testing Guide

This guide explains how to write and run tests for Spatium.

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
from src.device_config.ssh_client import SonicSSHClient

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
    with patch("src.device_config.ssh_client.SonicSSHClient") as mock:
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