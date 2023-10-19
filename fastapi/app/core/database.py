from datetime import datetime
from urllib.parse import quote

from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from app.core.config import get_settings
from app.core.logger import logger_factory

logger = logger_factory(__name__)
settings = get_settings()
db_url: str = f"postgresql+asyncpg://{settings.DB_USER}:{quote(settings.DB_PASSWORD.get_secret_value())}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
# server_settings pour améliorer la gestion d'énumérations de la DB (voir https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#disabling-the-postgresql-jit-to-improve-enum-datatype-handling)
engine: AsyncEngine = create_async_engine(
    db_url,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_pre_ping=False,
    pool_recycle=300,  # seconds
    pool_size=5,
    max_overflow=0,
    connect_args={"server_settings": {"jit": "off"}},
)

async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, expire_on_commit=False)  # type: ignore


# MappedAsDataclass details : https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#orm-declarative-native-dataclasses
class Base(DeclarativeBase, MappedAsDataclass, AsyncAttrs):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }


async def get_db():
    """
    A function for dependency injection of an :class:`AsyncSession` instance. This function also commits and rollbacks the transaction on error.

    Return:
        yields a :class:`AsyncSession` instance to connect to the database for a transaction.
    """
    async with async_session() as session_local:  # type: ignore
        try:
            yield session_local
            await session_local.commit()
        except Exception as e:
            await session_local.rollback()
            raise
