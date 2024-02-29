from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv(override=True)


class DotEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class BotSettings(DotEnvSettings):
    model_config = SettingsConfigDict(env_prefix="bot_")

    token: str = Field(default=...)
    local_server_url: Optional[str] = Field(default=None)
    local_server_port: Optional[int] = Field(default=None)
    webhook_path: str = Field(default=...)


class AppSettings(DotEnvSettings):
    model_config = SettingsConfigDict(env_prefix="app_")

    base_url: str = Field(default=...)
    base_port: int = Field(default=...)


class DBSettings(DotEnvSettings):
    model_config = SettingsConfigDict(env_prefix="db_")

    host: str = Field(default=...)
    name: str = Field(default=...)
    user: str = Field(default=...)
    password: str = Field(default=...)


class Settings(DotEnvSettings):
    bot: BotSettings = BotSettings()
    db: DBSettings = DBSettings()
    app: AppSettings = AppSettings()
    admin_ids: list[int] = Field(default=...)