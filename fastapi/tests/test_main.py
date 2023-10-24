from datetime import datetime
import uuid
import asyncio
import pytest

from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from app.main import app
from app.core.database import Base, get_db
from app.endpoints.user.util import ResponseUserModel, UserRole
from app.endpoints.user.security import verify_jwt

db_url_test = f"postgresql+asyncpg://test_user:test_password@localhost:5431/test_db"

engine_test: AsyncEngine = create_async_engine(
    db_url_test,
    echo=True,
    pool_pre_ping=False,
    pool_recycle=300,  # seconds
    pool_size=5,
    max_overflow=0,
    connect_args={"server_settings": {"jit": "off"}},
)

async_session_test: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine_test, autoflush=False, expire_on_commit=False
)


async def create_tables():
    async with engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


asyncio.run(create_tables())


async def get_db_mock():
    async with async_session_test() as session_local_test:
        try:
            yield session_local_test
            await session_local_test.commit()
        except Exception as e:
            await session_local_test.rollback()
            raise


async def verify_jwt_mock() -> ResponseUserModel:
    return ResponseUserModel(
        id=uuid.uuid4(),
        name="test",
        email="test@fastapi.com",
        role=UserRole.super_admin,
        created_on=datetime.now(),
        updated_on=datetime.now(),
        is_disabled=False,
        items=[],
    )


app.dependency_overrides[get_db] = get_db_mock
app.dependency_overrides[verify_jwt] = verify_jwt_mock


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
