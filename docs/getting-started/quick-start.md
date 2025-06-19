# Quick Start

This guide will help you get started with Spatium quickly.

## Running the Application

Start the application:

```bash
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).
API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Getting a Device Configuration

Use the `/device/config` endpoint to retrieve configuration from a SONiC device:

```bash
curl -X POST http://localhost:8000/device/config \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.1",
    "username": "admin",
    "password": "password",
    "method": "ssh"
  }'
```

## Analyzing a Configuration

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