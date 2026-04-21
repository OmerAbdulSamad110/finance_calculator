from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices, computed_field
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
    base_url: str = Field(env="BASE_URL")
    frontend_url: str = Field(env="FRONTEND_URL")

    # JWT
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

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
    redis_username: str = Field(..., env="REDIS_USERNAME")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = Field(..., env="REDIS_DB")

    # mail
    mail_mailer: str = Field(..., env="MAIL_MAILER")
    mail_host: str = Field(..., env="MAIL_HOST")
    mail_port: int = Field(..., env="MAIL_PORT")
    mail_username: str = Field(..., env="MAIL_USERNAME")
    mail_password: str = Field(..., env="MAIL_PASSWORD")
    mail_encryption: str = Field(..., env="MAIL_ENCRYPTION")
    mail_from: str = Field(..., env="MAIL_FROM")
    mail_from_name: str = Field(
        validation_alias=AliasChoices("MAIL_FROM_NAME", "APP_NAME")
    )


_configs = Config()


def config(key: str):
    if key not in _configs.model_dump():
        raise ValueError(f"Key {key} not found in config")
    return _configs.model_dump()[key]
