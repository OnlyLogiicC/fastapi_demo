from typing import Sequence
from uuid import UUID

from sqlalchemy import func
from sqlalchemy import select

from app.core.database import AsyncSession
from app.core.logger import logger_factory
from app.endpoints.user.util import UserSchema, CreateUserModel, UpdateUserModel

logger = logger_factory(__name__)


async def get_users(db: AsyncSession) -> Sequence[UserSchema]:
    """
    Repository layer function to retreive users stored in the database.

    Args:
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        A sequence of :class:`UserSchema`.
    """
    statement = select(UserSchema)
    result = (await db.scalars(statement)).unique().all()
    logger.debug(f"get_users() -> {result}")
    return result


async def get_users_count(db: AsyncSession) -> int:
    """
    Repository layer function to get the number of users stored in the database.

    Args:
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The number of users stored in the database as an integer.
    """
    statement = select(func.count()).select_from(UserSchema)
    result = await db.scalar(statement)
    logger.debug(f"get_users_count() -> {result}")
    return result if result else 0


async def get_user_by_email(email: str, db: AsyncSession) -> UserSchema | None:
    """
    Repository layer function to query a user by his email.

    Args:
        email: the string variable to make the query
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The user correspondinge to the email as a :class:`UserSchema` instance, if present in the database, else None.
    """
    statement = select(UserSchema).where(UserSchema.email == email)
    result = await db.scalar(statement)
    logger.debug(f"get_user_by_email({email}) -> {result}")
    return result


async def get_user_by_uuid(uuid: UUID, db: AsyncSession) -> UserSchema | None:
    """
    Repository layer function to query a user by his primary key.

    Args:
        uuid: the uuid variable to make the query
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The user correspondinge to the uuid as a :class:`UserSchema` instance, if present in the database, else None.
    """
    result = await db.get(UserSchema, uuid)
    logger.debug(f"get_user_by_uuid({uuid}) -> {result}")
    return result


async def create_user(user: CreateUserModel, db: AsyncSession) -> UserSchema:
    """
    Repository layer function to add a new user to the database

    Args:
        user: The :class:`CreateUserModel` instance to add to the database.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a :class:`UserSchema` instance corresponding to the user added to the database.
    """
    schema: UserSchema = UserSchema(**user.model_dump())
    db.add(schema)
    await db.flush()
    await schema.awaitable_attrs.items
    logger.debug(f"create_user({user!r}) -> {schema}")
    return schema


async def update_user(user: UpdateUserModel, db: AsyncSession) -> UserSchema | None:
    """
    Repository layer function to update a user from the database

    Args:
        user: The :class:`UpdateUserModel` instance to update from the database.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a :class:`UserSchema` instance corresponding to the user updated to the database or None if the user was not found.
    """
    schema: UserSchema | None = await db.get(UserSchema, user.id)
    if schema is None:
        return None
    schema.update_from_model(user)
    await db.flush()
    await db.refresh(schema)
    logger.debug(f"update_user({user!r}) -> {schema}")
    return schema


async def delete_user_by_uuid(uuid: UUID, db: AsyncSession) -> bool:
    """
    Repository layer function to delete a user from the database.

    Args:
        uuid: the uuid primary key variable to make the query.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a `bool` to indicate the success or failure of the operation.
    """
    schema: UserSchema | None = await db.get(UserSchema, uuid)
    logger.debug(f"delete_user_by_uuid({uuid}) -> {schema}")
    if schema is None:
        return False
    await db.delete(schema)
    return True
