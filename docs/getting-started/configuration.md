# Configuration

Spatium can be configured using environment variables or a `.env` file in the project root directory.

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | Spatium |
| APP_VERSION | Application version | 0.1.0 |
| DEBUG | Enable debug mode | True |
| API_PREFIX | API prefix | /api/v1 |
| BATFISH_HOST | Batfish host | localhost |
| BATFISH_PORT | Batfish port | 9997 |
| DEFAULT_SSH_PORT | Default SSH port | 22 |
| DEFAULT_GNMI_PORT | Default gNMI port | 8080 |

## Environment Variables

You can set these variables in your environment:

```bash
export BATFISH_HOST=192.168.1.100
export BATFISH_PORT=9997
```

## .env File

Alternatively, create a `.env` file in the project root:

```
APP_NAME=Spatium
APP_VERSION=0.1.0
DEBUG=true
BATFISH_HOST=localhost
BATFISH_PORT=9997
```

## Using Settings in Code

The settings are accessible through the `settings` object:

```python
from src.core.config import settings

# Use settings
host = settings.BATFISH_HOST
port = settings.BATFISH_PORT
```

## Overriding Settings for Testing

For testing, you can override settings:

```python
from src.core.config import Settings

test_settings = Settings(
    BATFISH_HOST="test-host",
    BATFISH_PORT=1234
)
```