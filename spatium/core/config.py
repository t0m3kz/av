from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Spatium"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API settings
    API_PREFIX: str = "/api/v1"

    # Batfish settings
    BATFISH_HOST: str = os.getenv("BATFISH_HOST", "localhost")
    BATFISH_PORT: int = int(os.getenv("BATFISH_PORT", "9997"))

    # Default credentials (for development only)
    DEFAULT_SSH_PORT: int = 22
    DEFAULT_GNMI_PORT: int = 8080

    # Update this from class Config to model_config
    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
