# Installation

This guide will help you install and set up Spatium on your system.

## Prerequisites

- Python 3.10 or higher
- Docker (for running Batfish and containerized network devices)
- ContainerLab (for deploying digital twins)

## Install Python Dependencies

1. Clone the repository:

```bash
git clone https://github.com/yourusername/spatium.git
cd spatium
```

2. Install using UV:

```bash
# Install base package
uv pip install -e .

# Install development dependencies (optional)
uv pip install -e ".[dev]"
```

## Install Batfish

Batfish is used for network configuration analysis. The easiest way to run it is using Docker:

```bash
docker run -d -p 9997:9997 -p 9996:9996 batfish/allinone
```

## Install ContainerLab

ContainerLab is used for deploying network digital twins. Install it following the [official instructions](https://containerlab.dev/install/):

```bash
bash -c "$(curl -sL https://get.containerlab.dev)"
```

## Configuration

Create a `.env` file in the project root directory to configure Spatium:

```
APP_NAME=Spatium
APP_VERSION=0.1.0
DEBUG=true

BATFISH_HOST=localhost
BATFISH_PORT=9997

DEFAULT_SSH_PORT=22
DEFAULT_GNMI_PORT=8080
```

## Verify Installation

Start the application:

```bash
uvicorn main:app --reload
```

Open your browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to see the Swagger UI documentation.