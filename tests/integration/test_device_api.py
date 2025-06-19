class TestDeviceAPI:
    def test_get_device_config(self, client, mock_ssh_client, mock_gnmi_client):
        # Prepare request data
        data = {
            "host": "192.168.1.1",
            "username": "admin",
            "password": "password",
            "method": "both",
            "ssh_port": 22,
            "gnmi_port": 8080,
        }

        # Make request
        response = client.post("/device/config", json=data)

        # Check response
        assert response.status_code == 200
        response_data = response.json()

        # Verify SSH data is in response
        assert "ssh" in response_data
        assert response_data["ssh"]["source"] == "ssh"

        # Verify gNMI data is in response
        assert "gnmi" in response_data
        assert response_data["gnmi"]["source"] == "gnmi"
