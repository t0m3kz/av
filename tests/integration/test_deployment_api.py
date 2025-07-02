

class TestDeploymentAPI:
    def test_deploy_topology(self, client):
        # Empty JSON should return 422 (validation error) since TopologyConfig is required
        response = client.post("/deployment/deploy", json={})
        assert response.status_code == 422

    def test_destroy_topology(self, client):
        # Destroying a non-existent topology should return 200 (deployment service handles gracefully)
        response = client.delete("/deployment/destroy/test-topo")
        assert response.status_code == 200

    def test_list_deployments(self, client):
        # List deployments should return 200 even if no deployments exist
        response = client.get("/deployment/list")
        assert response.status_code == 200
