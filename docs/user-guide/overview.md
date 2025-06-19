# User Guide Overview

This guide provides detailed information on how to use Spatium's features.

## Key Components

Spatium consists of three main components:

1. **Device Configuration Retrieval** - Get device configurations via SSH or gNMI
2. **Configuration Analysis** - Analyze configurations using Batfish
3. **Digital Twin Deployment** - Deploy and test network configurations in a containerized environment

## Typical Workflow

A typical workflow using Spatium involves these steps:

1. Retrieve configuration from existing devices
2. Analyze the configuration to identify issues
3. Deploy a digital twin to test changes
4. Validate the changes in the digital twin
5. Apply the validated changes to production devices

## Authentication

Spatium supports both password-based and key-based authentication for SSH connections.

## Data Format

Configurations can be retrieved and analyzed in various formats:

- Raw text (running configuration)
- YANG-modeled data (via gNMI)
- Structured JSON (for API responses)

## Next Steps

- Learn about [Device Configuration](device-config.md)
- Explore [Configuration Analysis](config-analysis.md)
- Understand [Digital Twins](digital-twins.md)