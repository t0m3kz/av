# API Architecture

## Overview

The Spatium API follows FastAPI best practices with a clean, modular architecture that separates concerns into distinct layers:

- **API Layer**: FastAPI routers and endpoints
- **Service Layer**: Business logic and data processing
- **Models Layer**: Pydantic data models and validation
- **Core Layer**: Configuration and constants

## Architecture Components

### 1. API Layer (`spatium/api/`)

#### Main Router (`device.py`)
The main device router that combines all device-related functionality:
- Inventory management (via `/topology/inventory/*`)
- Device configuration retrieval (via `/configs/*`)
- Includes containerlab integration

#### Sub-routers (`routers/`)

**Inventory Router** (`routers/inventory.py`)
- `POST /inventory/add` - Add devices to inventory
- `GET /inventory/list` - List devices in inventory
- `POST /inventory/remove` - Remove devices from inventory
- `POST /inventory/clear` - Clear inventory
- `GET /inventory/names` - List inventory names
- `GET /inventory/stats` - Get inventory statistics

**Device Config Router** (`routers/device_config.py`)
- `POST /configs/get` - Fetch device configurations
- `POST /configs/save` - Fetch and save configurations to files

#### Exception Handling (`exceptions.py`)
Centralized exception classes and HTTP error handling:
- `SpatiumException` - Base exception class
- `DeviceNotFoundError`, `DeviceConnectionError`, etc.
- `create_http_exception()` - Standardized HTTP exceptions

#### Response Models (`responses.py`)
Standardized Pydantic response models:
- `BaseResponse` - Common response structure
- `InventoryResponse` - Inventory operation responses
- `ConfigResponse` - Configuration retrieval responses
- `ConfigSaveResponse` - Configuration save responses

#### Dependencies (`dependencies.py`)
FastAPI dependency injection:
- `get_settings()` - Application settings (cached)
- `get_ssh_client_factory()` - SSH client factory
- `get_inventory_service()` - Inventory service (singleton)
- `get_device_config_service()` - Device config service

### 2. Service Layer (`spatium/services/`)

#### Inventory Service (`inventory.py`)
Manages device inventories with in-memory storage:
- Add/remove devices with duplicate prevention
- Filter devices by host
- Get inventory statistics
- Support for multiple named inventories

#### Device Configuration Service (`device_config.py`)
Handles device configuration retrieval:
- SSH and REST API support
- Concurrent configuration fetching
- Device-specific command mapping
- Configuration file saving

### 3. Core Layer (`spatium/core/`)

#### Configuration (`config.py`)
Application settings using Pydantic Settings:
- Environment variable support
- Default values for development

#### Device Constants (`device_constants.py`)
Device-specific configurations:
- Command mappings for different device types
- REST API endpoints
- Default settings and timeouts

### 4. Models Layer (`spatium/models/`)

#### Device Models (`device.py`)
- `DeviceConfigRequest` - Device connection parameters
- `DeviceConfigResponse` - Configuration retrieval results

## Key Design Principles

### 1. Separation of Concerns
- **Controllers** (routers) handle HTTP requests/responses
- **Services** contain business logic
- **Models** define data structures
- **Dependencies** manage object creation

### 2. Dependency Injection
- Services are injected via FastAPI's dependency system
- Singletons for stateful services (inventory)
- Factory pattern for stateless services (SSH clients)

### 3. Error Handling
- Centralized exception classes
- Consistent error response format
- Proper HTTP status codes

### 4. Configuration Management
- Environment-based configuration
- Centralized constants
- Type-safe settings

### 5. Testability
- Dependency injection enables easy mocking
- Service layer is framework-independent
- Clear separation makes unit testing straightforward

## API Endpoints

### Inventory Management
```
POST /topology/inventory/add?inventory={name}
GET  /topology/inventory/list?inventory={name}
POST /topology/inventory/remove?inventory={name}
POST /topology/inventory/clear?inventory={name}
GET  /topology/inventory/names
GET  /topology/inventory/stats?inventory={name}
```

### Device Configuration
```
POST /configs/get?inventory={name}&host={host}
POST /configs/save?inventory={name}&host={host}&output_folder={folder}
```

## Response Format

All API responses follow a consistent structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "inventory": "inventory_name",
  "results": [...],
  "affected_hosts": [...]
}
```

## Error Handling

Errors are returned in a standardized format:

```json
{
  "success": false,
  "error": "Error message",
  "details": {
    "additional": "context"
  }
}
```

## Future Enhancements

1. **Database Integration**: Replace in-memory storage with persistent database
2. **Authentication**: Add API key or OAuth2 authentication
3. **Rate Limiting**: Implement request rate limiting
4. **Caching**: Add Redis for configuration caching
5. **WebSocket Support**: Real-time device status updates
6. **Plugin System**: Extensible device type support
