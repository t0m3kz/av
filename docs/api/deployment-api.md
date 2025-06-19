# Deployment API

The Deployment API allows you to create, manage, and destroy network digital twins using ContainerLab.

## Endpoints

### Deploy Topology

Deploy a network topology as a digital twin.

**Endpoint:** `POST /deployment/deploy`

**Request Body:**

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

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Topology name |
| nodes | array | Yes | List of nodes |
| links | array | Yes | List of links |
| mgmt_network | string | No | Management network name (default: "spatium-mgmt") |

**Response:**

```json
{
  "success": true,
  "topology_name": "sonic-test",
  "topology_file": "/path/to/topologies/sonic-test.yaml",
  "output": "Deployed topology successfully"
}
```

### Destroy Topology

Destroy a deployed topology.

**Endpoint:** `DELETE /deployment/destroy/{topology_name}`

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| topology_name | string | Yes | Name of the topology to destroy |

**Response:**

```json
{
  "success": true,
  "topology_name": "sonic-test",
  "output": "Destroyed topology successfully"
}
```

### List Deployments

List all deployed topologies.

**Endpoint:** `GET /deployment/list`

**Response:**

```json
{
  "success": true,
  "output": "List of deployed topologies"
}
```