from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Spatium"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API settings
    API_PREFIX: str = "/api/v1"

    # Default credentials (for development only)
    DEFAULT_SSH_PORT: int = 22

    # ContainerLab settings
    CONTAINERLAB_API_URL: str = "http://localhost:8081"
    CONTAINERLAB_TIMEOUT: int = 30
    
    # REST client settings
    REST_CLIENT_TIMEOUT: int = 30
    REST_CLIENT_RETRIES: int = 3
    REST_CLIENT_VERIFY_SSL: bool = False

    # Update this from class Config to model_config
    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
