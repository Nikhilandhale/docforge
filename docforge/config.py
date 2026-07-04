from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "sqlite:///./docforge.db"
    storage_dir: str = "./storage"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DOCFORGE_", extra="ignore")


settings = Settings()
