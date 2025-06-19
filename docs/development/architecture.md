# Architecture

This document describes the architecture of Spatium.

## High-Level Architecture

Spatium follows a modular architecture with clean separation of concerns:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   API Layer │     │  Business   │     │    Data     │
│  (FastAPI)  │────►│    Logic    │────►│   Access    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Models    │     │   External  │     │ Configuration│
│  (Pydantic) │     │   Services  │     │              │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Component Overview

### API Layer

The API layer is built with FastAPI and handles HTTP requests, input validation, and response formatting.

**Key Components:**
- API routers (`src/api/`)
- Request/response models (`src/models/`)
- Authentication middleware

### Business Logic

The business logic layer contains the core functionality of the application.

**Key Components:**
- Device configuration management (`src/device_config/`)
- Configuration analysis (`src/analysis/`)
- Digital twin deployment (`src/deployment/`)

### Data Access

The data access layer handles interactions with external data sources.

**Key Components:**
- SSH clients
- gNMI clients
- Batfish integration
- ContainerLab integration

### Models

Pydantic models define the data structures used throughout the application.

**Key Components:**
- API request/response models
- Internal data models
- Configuration models

### External Services

External services used by the application.

**Key Components:**
- Batfish (for configuration analysis)
- ContainerLab (for digital twin deployment)

### Configuration

Application configuration management.

**Key Components:**
- Settings management (`src/core/config.py`)
- Environment variables
- Configuration files

## Directory Structure

```
spatium/
├── main.py                  # Application entry point
├── src/                     # Source code
│   ├── api/                 # API routers
│   │   ├── device.py        # Device API
│   │   ├── analysis.py      # Analysis API
│   │   └── deployment.py    # Deployment API
│   ├── core/                # Core functionality
│   │   └── config.py        # Configuration management
│   ├── models/              # Pydantic models
│   │   ├── device.py        # Device models
│   │   ├── analysis.py      # Analysis models
│   │   └── deployment.py    # Deployment models
│   ├── device_config/       # Device configuration management
│   │   ├── sonic_client.py  # SONiC client
│   │   ├── ssh_client.py    # SSH client
│   │   └── gnmi_client.py   # gNMI client
│   ├── analysis/            # Configuration analysis
│   │   └── batfish_analyzer.py # Batfish integration
│   └── deployment/          # Digital twin deployment
│       └── containerlab.py  # ContainerLab integration
├── tests/                   # Tests
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Test fixtures
└── docs/                    # Documentation
```

## Request Flow

1. Client sends a request to the API
2. FastAPI routes the request to the appropriate endpoint
3. Request data is validated using Pydantic models
4. Endpoint handler processes the request, calling business logic
5. Business logic performs operations, interacting with external services
6. Response is generated and returned to the client

## Dependencies

External dependencies used by Spatium:

- **FastAPI**: Web framework
- **Pydantic**: Data validation and settings management
- **AsyncSSH**: SSH connections
- **pyGNMI**: gNMI connections
- **Batfish**: Network configuration analysis
- **ContainerLab**: Digital twin deployment

## Design Principles

Spatium follows these design principles:

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Dependencies are injected rather than created directly
3. **Async-First**: Asynchronous programming for better scalability
4. **Type Safety**: Extensive use of type hints and Pydantic models
5. **Testability**: Code is designed to be easily testable
6. **Configuration over Convention**: Explicit configuration for clarity