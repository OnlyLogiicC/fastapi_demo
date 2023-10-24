from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

from app.core.logger import LogLevel, set_log_level, logger_factory

env_file = Path("../.env")  # Not necessary when deployed in a Docker container. Path valid when running from /fastapi


class EnvSettings(BaseSettings):
    """Pydantic BaseSettings class to store environment variables"""

    model_config = SettingsConfigDict(env_file=env_file if env_file.exists() else None, env_file_encoding="utf-8")

    # Locale and timezone
    TIMEZONE: str = "Europe/Paris"
    LOCALE: str = "en_US.utf8"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Database
    DB_NAME: str = "demo"
    DB_USER: str = "demo"
    DB_PASSWORD: SecretStr = SecretStr("demo*123")
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"

    # JWT
    JWT_SECRET: SecretStr = SecretStr("secretdemo")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


@lru_cache()
def get_settings() -> EnvSettings:
    """
    Returns the environment variables in an instance of :class:`EnvSettings`
    """
    return EnvSettings()


set_log_level(LogLevel[get_settings().LOG_LEVEL])
logger = logger_factory(__name__)


def initialize_app() -> None:
    """Init function executed on start up"""
    logger.debug("Initializing...")
    logger.debug(repr(get_settings()))
    return


def cleanup_app() -> None:
    """Clean Up function executed on shutdown"""
    logger.debug("Cleaning up resources...")
    return
