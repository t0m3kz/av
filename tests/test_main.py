import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()

    # More flexible assertion to handle different response formats
    assert isinstance(data, dict), "Response is not a dictionary"

    # Check for name or message
    assert any(key in data for key in ["name", "message"]), (
        "Response missing 'name' or 'message' field"
    )

    # Check for version or other fields if present
    if "version" in data:
        assert isinstance(data["version"], str), "Version is not a string"


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "Spatium"
    assert "version" in data
    assert "description" in data


def test_about_route(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Spatium"
    assert data["version"] == "0.1.0"
    assert "SSH-only" in data["description"]
