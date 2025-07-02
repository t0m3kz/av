import json
import pathlib

# Load all mock outputs once for the class
MOCKS_DIR = pathlib.Path(__file__).parent.parent / "mocks"
MOCK_OUTPUTS = {
    fname: json.load(open(MOCKS_DIR / fname))
    for fname in ["ssh_output_1.json", "ssh_output_2.json", "ssh_output_error.json"]
}

def get_sample_output(filename):
    return MOCK_OUTPUTS[filename]

class MockSSHClient:
    def __init__(self, host, username, password=None, private_key=None, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.private_key = private_key
        self.port = port
        self._sample = None
    async def get_config(self, command="show runningconfiguration all"):
        # Return the sample as a dict with expected fields
        # Ensure all expected fields are present and not coroutines
        return {
            "host": self.host,
            "running_config": self._sample.get("running_config"),
            "error": self._sample.get("error"),
        }

def get_mock_ssh_client_factory(sample):
    def factory(**kwargs):
        client = MockSSHClient(**kwargs)
        client._sample = sample
        return client
    return factory

