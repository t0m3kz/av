import pytest
from spatium.services.device_config import DeviceConfigService
from spatium.models.device import DeviceConfigRequest

class DummySSHClient:
    def __init__(self, **kwargs):
        self.host = kwargs["host"]
    async def get_config(self, command="show running-config"):
        return {"host": self.host, "running_config": "dummy config", "error": None}

def dummy_factory(**kwargs):
    return DummySSHClient(**kwargs)

@pytest.mark.asyncio
async def test_fetch_config_success():
    req = DeviceConfigRequest(
        host="1.2.3.4", username="u", password="p", port=22, device_model="sonic"
    )
    service = DeviceConfigService(dummy_factory)
    result = await service.fetch_config(req)
    assert result.host == "1.2.3.4"
    assert result.running_config == "dummy config"
    assert result.error is None

@pytest.mark.asyncio
async def test_fetch_config_error():
    class ErrorClient:
        def __init__(self, **kwargs):
            self.host = kwargs["host"]
        async def get_config(self, command="show running-config"):
            raise Exception("fail connect")
    def error_factory(**kwargs):
        return ErrorClient(**kwargs)
    req = DeviceConfigRequest(
        host="2.2.2.2", username="u", password="p", port=22, device_model="arista"
    )
    service = DeviceConfigService(error_factory)
    result = await service.fetch_config(req)
    assert result.host == "2.2.2.2"
    assert result.running_config is None
    assert "fail connect" in result.error
