import pytest


class TestDeploymentAPI:
    def test_deploy_topology(self, client):
        response = client.post("/deployment/deploy", json={})
        assert response.status_code == 404

    def test_destroy_topology(self, client):
        response = client.delete("/deployment/destroy/test-topo")
        assert response.status_code == 404

    def test_list_deployments(self, client):
        response = client.get("/deployment/list")
        assert response.status_code == 404
