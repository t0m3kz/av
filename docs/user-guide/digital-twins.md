# Digital Twins

This guide explains how to use Spatium's digital twin capabilities to create and test network configurations.

## What are Digital Twins?

Digital twins are virtual replicas of network devices and topologies that allow you to test configurations and changes in a safe, isolated environment before deploying to production.

## ContainerLab

Spatium uses [ContainerLab](https://containerlab.dev/) to create and manage digital twins. ContainerLab is a tool that allows you to create containerized network topologies.

## Creating a Digital Twin

You can create a digital twin using the `/deployment/deploy` endpoint:

```json
{
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
  ],
  "mgmt_network": "spatium-mgmt"
}
```

## Node Configuration

Each node in a digital twin has these properties:

| Property | Description | Default |
|----------|-------------|---------|
| name | Node name | Required |
| type | Node type/kind | sonic-vs |
| image | Container image | docker-sonic-vs:latest |
| ports | Port mappings | [] |

## Link Configuration

Links connect nodes in the topology:

| Property | Description | Default |
|----------|-------------|---------|
| node1 | First node name | Required |
| interface1 | First node interface | "" |
| node2 | Second node name | Required |
| interface2 | Second node interface | "" |

## Managing Digital Twins

### Listing Deployments

You can list all deployed digital twins:

```bash
curl -X GET http://localhost:8000/deployment/list
```

### Destroying a Deployment

You can destroy a digital twin when you're done with it:

```bash
curl -X DELETE http://localhost:8000/deployment/destroy/sonic-test
```

## Testing with Digital Twins

Once a digital twin is deployed, you can:

1. Connect to the devices using SSH:
   ```bash
   ssh admin@sonic1
   ```

2. Apply configurations to test changes

3. Verify connectivity between devices:
   ```bash
   ping 192.168.1.2
   ```

4. Use Spatium's analysis capabilities to analyze the configuration

## Best Practices

- Create topologies that match your production environment
- Use the same SONiC version as your production devices
- Test configuration changes in the digital twin before applying to production
- Destroy digital twins when you're done to free up resources
- Use meaningful names for topologies and nodes
