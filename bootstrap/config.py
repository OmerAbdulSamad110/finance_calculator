from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from typing import Optional


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App info
    app_name: str = Field("FastAPI", env="APP_NAME")
    version: str = Field("1.0.0", env="VERSION")
    debug: bool = Field(True, env="DEBUG")
    secret_key: str = Field(env="SECRET_KEY")

    # Database
    db_connection: str = Field("mysql", env="DB_CONNECTION")
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(..., env="DB_PORT")
    db_username: str = Field(..., env="DB_USERNAME")
    db_password: Optional[str] = Field(None, env="DB_PASSWORD")
    db_database: str = Field(..., env="DB_DATABASE")

    # Redis
    redis_prefix: str = Field("ad_searcher_database_", env="REDIS_PREFIX")
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(..., env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = Field(..., env="REDIS_DB")

    # JWT / Auth
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


_configs = Config()


def config(key: str):
    if key not in _configs.model_dump():
        raise ValueError(f"Key {key} not found in config")
    return _configs.model_dump()[key]
