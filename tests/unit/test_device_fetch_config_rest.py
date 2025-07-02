import pytest
import httpx
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
async def test_fetch_config_rest_success(monkeypatch):
    class DummyResponse:
        def __init__(self, text):
            self.text = text
        def raise_for_status(self):
            pass
        def json(self):
            # Return JSON parseable data so REST client gets structured response
            return {"config": self.text}
    class DummyAsyncClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def get(self, url, auth=None, timeout=None):
            assert url == "http://1.1.1.1:8080/api/config"
            return DummyResponse("rest config")
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: DummyAsyncClient())
    req = DeviceConfigRequest(
        host="1.1.1.1", username="u", password="p", port=8080, method="rest"
    )
    service = DeviceConfigService(dummy_factory)
    result = await service.fetch_config(req)
    assert result.host == "1.1.1.1"
    assert result.running_config == '{\n  "config": "rest config"\n}'  # JSON formatted response
    assert result.source == "rest"
    assert result.error is None

@pytest.mark.asyncio
async def test_fetch_config_rest_custom_url(monkeypatch):
    class DummyResponse:
        def __init__(self, text):
            self.text = text
        def raise_for_status(self):
            pass
        def json(self):
            return {"config": self.text}
    class DummyAsyncClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def get(self, url, auth=None, timeout=None):
            assert url == "http://custom-url"
            return DummyResponse("custom rest config")
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: DummyAsyncClient())
    req = DeviceConfigRequest(
        host="irrelevant", username="u", password="p", port=80, method="rest", rest_url="http://custom-url"
    )
    service = DeviceConfigService(dummy_factory)
    result = await service.fetch_config(req)
    assert result.running_config == "custom rest config"  # get_config_custom returns string directly
    assert result.source == "rest"
    assert result.error is None

@pytest.mark.asyncio
async def test_fetch_config_rest_error(monkeypatch):
    class DummyAsyncClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def get(self, url, auth=None, timeout=None):
            raise httpx.ConnectError("fail rest connect")
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: DummyAsyncClient())
    req = DeviceConfigRequest(
        host="3.3.3.3", username="u", password="p", port=80, method="rest"
    )
    service = DeviceConfigService(dummy_factory)
    result = await service.fetch_config(req)
    assert result.host == "3.3.3.3"
    assert result.running_config is None
    assert result.source == "rest"
    assert "fail rest connect" in result.error
