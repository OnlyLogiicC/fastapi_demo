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
    JWT_SECRET: SecretStr = SecretStr("709d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


_settings_instance = None


def get_settings() -> EnvSettings:
    """
    Returns the environment variables in an instance of :class:`EnvSettings`
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = EnvSettings()
    return _settings_instance


set_log_level(LogLevel[get_settings().LOG_LEVEL])
logger = logger_factory(__name__)


def initialize_app() -> None:
    """Initialize function on start up"""
    logger.debug("Initializing...")
    logger.debug(repr(get_settings()))
    return


def cleanup_app() -> None:
    """Clean Up function executed on shutdown"""
    logger.debug("Cleaning up resources...")
    return
