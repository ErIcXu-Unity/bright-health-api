from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = "default-dev-key"
    google_cloud_project: str = "bright-assessment"
    google_application_credentials: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
