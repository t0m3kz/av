# Installation Guide

This comprehensive guide will help you install and set up Spatium on your system step by step.

## System Requirements

### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+, RHEL 8+, or similar)
- **Python**: 3.10 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 10GB free disk space
- **Network**: Internet access for downloading dependencies

### Optional Components
- **Docker**: Required for Batfish analysis and ContainerLab digital twins
- **ContainerLab**: For network topology deployment and testing
- **Git**: For version control and development

## Step 1: System Preparation

### Update System Packages
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# RHEL/CentOS/Fedora
sudo dnf update -y
```

### Install Python 3.10+
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv -y

# RHEL/CentOS/Fedora
sudo dnf install python3 python3-pip -y

# Verify installation
python3 --version
```

### Install UV (Python Package Manager)
```bash
# Install UV for faster dependency management
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Verify installation
uv --version
```

## Step 2: Install Spatium

### Clone the Repository
```bash
# Clone from your repository
git clone https://github.com/yourusername/spatium.git
cd spatium

# Or if working locally
cd /path/to/spatium
```

### Install Python Dependencies
```bash
# Install base package
uv pip install -e .

# For development and testing (recommended)
uv pip install -e ".[dev]"

# Verify installation
python3 -c "import spatium; print('Spatium installed successfully!')"
```

## Step 3: Optional Components

### Install Docker (Recommended)
Docker is required for Batfish analysis and ContainerLab digital twins.

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# RHEL/CentOS/Fedora
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker run hello-world
```

### Install Batfish (Network Analysis)
Batfish provides network configuration analysis capabilities.

```bash
# Pull and run Batfish container
docker run -d \
  --name batfish \
  --restart unless-stopped \
  -p 9997:9997 \
  -p 9996:9996 \
  batfish/allinone

# Verify Batfish is running
docker ps | grep batfish
curl -s http://localhost:9997 && echo "Batfish is running!"
```

### Install ContainerLab (Digital Twins)
ContainerLab enables network topology deployment and testing.

```bash
# Install ContainerLab
bash -c "$(curl -sL https://get.containerlab.dev)"

# Verify installation
containerlab version

# Install additional container images for SONiC testing
docker pull ghcr.io/azure/sonic-vs:latest
```

## Step 4: Configuration

### Create Environment Configuration
Create a `.env` file in the project root directory:

```bash
cat > .env << 'EOF'
# Application Configuration
APP_NAME=Spatium
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000

# API Configuration
API_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Database Configuration (if using persistent storage)
# DATABASE_URL=sqlite:///./spatium.db

# External Services
BATFISH_HOST=localhost
BATFISH_PORT=9997
BATFISH_TIMEOUT=30

# Device Configuration
DEFAULT_SSH_PORT=22
DEFAULT_SSH_TIMEOUT=30
DEFAULT_GNMI_PORT=8080
MAX_CONCURRENT_CONNECTIONS=10

# Storage Configuration
CONFIG_OUTPUT_DIR=outputs
BACKUP_RETENTION_DAYS=30

# Security Configuration
SECRET_KEY=your-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
```

### Create Output Directory
```bash
# Create directory for configuration backups
mkdir -p outputs
chmod 755 outputs
```

### Set Permissions
```bash
# Ensure proper permissions
chmod 600 .env
chmod +x scripts/* 2>/dev/null || true
```

## Step 5: Verification

### Start Spatium API Server
```bash
# Start in development mode with auto-reload
uvicorn spatium.main:app --reload --host 0.0.0.0 --port 8000

# Or for production
uvicorn spatium.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Installation
```bash
# Check API health
curl -s http://localhost:8000/docs | grep -q "Spatium" && echo "✅ API Documentation available"

# Test basic functionality
curl -s -X GET "http://localhost:8000/topology/inventory/list?inventory=test" && echo "✅ Inventory API working"

# Check if Batfish integration works (if installed)
curl -s http://localhost:9997 && echo "✅ Batfish integration ready"
```

### Access Web Interface
Open your browser and navigate to:
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill $(sudo lsof -t -i:8000)
```

#### Permission Denied
```bash
# Fix permissions
sudo chown -R $USER:$USER ./spatium
chmod -R 755 ./spatium
```

#### Python Import Errors
```bash
# Reinstall dependencies
uv pip install --force-reinstall -e .

# Clear Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

#### Docker Issues
```bash
# Restart Docker daemon
sudo systemctl restart docker

# Check Docker logs
docker logs batfish
```

### Getting Help

If you encounter issues:

1. **Check the logs**: Look at terminal output for error messages
2. **Verify prerequisites**: Ensure all required software is installed
3. **Check documentation**: Review the [API documentation](../api/device-api-new.md)
4. **Search issues**: Look at [GitHub Issues](https://github.com/yourusername/spatium/issues)
5. **Ask for help**: Create a new issue with detailed error information

## Next Steps

Now that Spatium is installed, you can:

1. **[Complete the Quick Start](quick-start.md)** - Learn basic operations
2. **[Configure your environment](configuration.md)** - Customize settings
3. **[Explore the API](../usage.md)** - Try comprehensive examples
4. **[Set up your first inventory](../user-guide/device-config.md)** - Add your devices

Congratulations! You've successfully installed Spatium. 🎉