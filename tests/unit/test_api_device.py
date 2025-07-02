from fastapi.testclient import TestClient

from spatium.main import app

client = TestClient(app)


def test_add_and_list_device():
    topology = "testtopo1"
    device = {
        "host": "10.0.0.1",
        "username": "admin",
        "password": "pass",
        "port": 22,
        "device_model": "sonic",
    }
    # Clear topology
    client.post(f"/topology/inventory/clear?inventory={topology}")
    resp = client.post(f"/topology/inventory/add?inventory={topology}", json=device)
    assert resp.status_code == 200
    assert resp.json()["success"]
    resp = client.get(f"/topology/inventory/list?inventory={topology}")
    assert resp.status_code == 200
    assert any(d["host"] == "10.0.0.1" for d in resp.json())


def test_remove_and_clear_device():
    topology = "testtopo2"
    client.post(f"/topology/inventory/clear?inventory={topology}")
    device1 = {
        "host": "10.0.0.2",
        "username": "admin",
        "password": "pass",
        "port": 22,
        "device_model": "arista",
    }
    device2 = {
        "host": "10.0.0.3",
        "username": "admin",
        "password": "pass",
        "port": 22,
        "device_model": "sonic",
    }
    # Add two devices
    client.post(f"/topology/inventory/add?inventory={topology}", json=[device1, device2])
    # Remove both in a single call
    resp = client.post(f"/topology/inventory/remove?inventory={topology}", json=[device1, device2])
    assert resp.status_code == 200
    assert resp.json()["success"]
    # Add again and clear
    client.post(f"/topology/inventory/add?inventory={topology}", json=[device1, device2])
    resp = client.post(f"/topology/inventory/clear?inventory={topology}")
    assert resp.status_code == 200
    assert resp.json()["success"]


def test_bulk_add_devices():
    topology = "testtopo3"
    client.post(f"/topology/inventory/clear?inventory={topology}")
    devices = [
        {
            "host": f"10.0.0.{i}",
            "username": "admin",
            "password": "pass",
            "port": 22,
            "device_model": "sonic",
        }
        for i in range(1, 4)
    ]
    resp = client.post(f"/topology/inventory/add?inventory={topology}", json=devices)
    assert resp.status_code == 200
    assert resp.json()["success"]
    resp = client.get(f"/topology/inventory/list?inventory={topology}")
    assert resp.status_code == 200
    hosts = [d["host"] for d in resp.json()]
    for i in range(1, 4):
        assert f"10.0.0.{i}" in hosts


def test_multiple_inventories_isolation():
    # Devices in different inventories should not overlap
    inv_a = "invA"
    inv_b = "invB"
    client.post(f"/topology/inventory/clear?inventory={inv_a}")
    client.post(f"/topology/inventory/clear?inventory={inv_b}")
    dev_a = {
        "host": "1.1.1.1",
        "username": "a",
        "password": "a",
        "port": 22,
        "device_model": "sonic",
    }
    dev_b = {
        "host": "2.2.2.2",
        "username": "b",
        "password": "b",
        "port": 22,
        "device_model": "arista",
    }
    client.post(f"/topology/inventory/add?inventory={inv_a}", json=dev_a)
    client.post(f"/topology/inventory/add?inventory={inv_b}", json=dev_b)
    resp_a = client.get(f"/topology/inventory/list?inventory={inv_a}")
    resp_b = client.get(f"/topology/inventory/list?inventory={inv_b}")
    assert any(d["host"] == "1.1.1.1" for d in resp_a.json())
    assert any(d["host"] == "2.2.2.2" for d in resp_b.json())
    assert not any(d["host"] == "2.2.2.2" for d in resp_a.json())
    assert not any(d["host"] == "1.1.1.1" for d in resp_b.json())
