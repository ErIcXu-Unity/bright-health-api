from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_key: str = "default-dev-key"
    google_cloud_project: str = "bright-assessment"
    google_application_credentials: Optional[str] = "service-account.json"


settings = Settings()
