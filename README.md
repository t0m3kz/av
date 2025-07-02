# Spatium

**Spatium** is a powerful network configuration analyzer and digital twin platform designed for SONiC-based network devices. It provides a comprehensive API for device configuration management, traffic analysis, and network digital twin deployment.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

## 🚀 Features

- **🔧 Device Configuration Management**
  - Retrieve configurations from SONiC devices via SSH
  - Support for multiple device inventories
  - Bulk configuration operations
  - Configuration backup and versioning

- **🌐 Network Digital Twins**
  - Deploy network topologies using ContainerLab
  - Test configurations in isolated environments
  - Validation before production deployment

- **📊 Traffic Analysis**
  - Analyze reachability between devices using Batfish
  - Network verification and validation
  - Configuration impact analysis

- **🔌 REST API**
  - Comprehensive API for automation
  - OpenAPI/Swagger documentation
  - Device inventory management
  - Configuration retrieval and storage

## 📋 Prerequisites

- **Python 3.10+** - Core runtime
- **Docker** - For ContainerLab and network digital twins
- **ContainerLab** - Network topology deployment (optional)
- **SONiC devices** - Or containerized SONiC instances for testing

## ⚡ Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/spatium.git
cd spatium

# Install dependencies using UV
uv pip install -e .

# For development (includes testing tools)
uv pip install -e ".[dev]"
```

### 2. Start the API Server

```bash
# Development mode with auto-reload
uvicorn spatium.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn spatium.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### 3. Basic Usage

```bash
# Add devices to inventory
curl -X POST "http://localhost:8000/topology/inventory/add?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.10",
    "device_model": "sonic",
    "username": "admin",
    "password": "admin"
  }'

# Retrieve configurations
curl -X POST "http://localhost:8000/configs/get?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{}'

# Save configurations to files
curl -X POST "http://localhost:8000/configs/save?inventory=lab1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 📚 Documentation

Complete documentation is available at: `http://localhost:5000`

To serve documentation locally:

```bash
mkdocs serve --dev-addr 0.0.0.0:5000
```

### Key Documentation Sections

- **[Getting Started](docs/getting-started/installation.md)** - Installation and setup
- **[API Usage Guide](docs/usage.md)** - Comprehensive API examples
- **[User Guide](docs/user-guide/overview.md)** - Feature documentation
- **[Development](docs/development/api-architecture.md)** - Architecture and contributing

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=spatium --cov-report=html

# Run specific test category
uv run pytest tests/unit/
uv run pytest tests/integration/
```

## 🛠️ Development

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy spatium/
```

### Project Structure

```
spatium/
├── spatium/                 # Main application package
│   ├── api/                # FastAPI routes and endpoints
│   ├── services/           # Business logic services
│   ├── models/             # Pydantic data models
│   ├── clients/             # Device communication clients
│   └── core/              # Core utilities and config
├── docs/                  # Documentation
├── tests/                 # Test suite
└── topologies/           # ContainerLab topologies
```

## 🔧 Configuration

Environment variables can be configured in `.env` file:

```bash
# API Configuration
SPATIUM_HOST=0.0.0.0
SPATIUM_PORT=8000
SPATIUM_LOG_LEVEL=INFO

# Device Configuration
DEFAULT_SSH_TIMEOUT=30
MAX_CONCURRENT_CONNECTIONS=10

# Storage Configuration
CONFIG_OUTPUT_DIR=outputs
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development/contributing.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.spatium.io](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/spatium/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/spatium/discussions)

---

**Built with ❤️ for network engineers and automation enthusiasts**

## API Usage

### Retrieve Device Configurations

```bash
curl -X POST "http://localhost:8000/devices/configs?save_txt=true" \
  -H "Content-Type: application/json" \
  -d '[{"host": "172.20.0.65", "username": "admin", "password": "admin", "port": 22, "device_model": "sonic"}]'
```
- The `device_model` parameter lets you specify the device type (e.g., `sonic`, `cisco`, `arista`, etc.) so Spatium can use the correct command to fetch the running configuration.

### Analyze Traffic Reachability with Batfish

```bash
curl -X POST "http://localhost:8000/devices/analyze-traffic" \
  -H "Content-Type: application/json" \
  -d '{"src_device": "leaf1", "src_ip": "10.0.0.1", "dst_device": "leaf2", "dst_ip": "10.0.0.2"}'
```

### Query Perle Device TTY Ports via REST API

```bash
curl -X POST "http://localhost:8000/devices/perle-tty" \
  -H "Content-Type: application/json" \
  -d '{"host": "perle-device.local", "username": "admin", "password": "admin", "port": 8080}'
```
- This endpoint now uses the Perle device's REST API (not SSH).
- The Perle device must expose a REST endpoint at `/api/tty_ports` on the specified port.

---

# Removed Batfish/config analysis support. Only SSH/gNMI config retrieval and digital twin deployment remain.

# Example config retrieval payload

```json
[
  {
    "host": "172.20.0.65",
    "username": "admin",
    "password": "admin",
    "port": 22
  }
]
```
