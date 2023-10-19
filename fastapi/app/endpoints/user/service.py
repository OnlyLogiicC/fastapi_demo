from uuid import UUID
from dataclasses import asdict

from app.core.database import AsyncSession
from app.endpoints.user.util import ResponseUserModel, CreateUserModel, UserSchema, UpdateUserModel
import app.endpoints.user.repository as repository


async def get_users(db: AsyncSession) -> list[ResponseUserModel]:
    """
    Service layer function to get the users stored in the database.

    Args:
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        A list of :class:`ResponseUserModel`.
    """
    result = await repository.get_users(db)
    return [ResponseUserModel.model_validate(s) for s in result]


async def get_users_count(db: AsyncSession) -> int:
    """
    Service layer function to get the number of users stored in the database.

    Args:
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The number of users stored in the database as an integer.
    """
    return await repository.get_users_count(db)


async def get_user_with_password_by_email(email: str, db: AsyncSession) -> tuple[ResponseUserModel | None, str | None]:
    """
    Service layer function to query a user by his email and return the hashed password separately to be able to authenticate the user.

    Args:
        email: the string variable to make the query
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The user correspondinge to the email as a :class:`ResponseUserModel` instance, if present in the database, else None.
        The user password as a `str` if the user is present else None.
    """
    result = await repository.get_user_by_email(email=email, db=db)
    return ResponseUserModel(**asdict(result)) if result else None, result.password if result else None


async def get_user_by_uuid(uuid: UUID, db: AsyncSession) -> ResponseUserModel | None:
    """
    Service layer function to query a user by his uuid primary key.

    Args:
        uuid: the uuid primary key variable to make the query
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The user correspondinge to the uuid as a :class:`ResponseUserModel` instance, if present in the database, else None.
    """
    result = await repository.get_user_by_uuid(uuid=uuid, db=db)
    return ResponseUserModel.model_validate(result) if result else None


async def create_user(user: CreateUserModel, db: AsyncSession) -> ResponseUserModel:
    """
    Service layer function to add a user to the database.

    Args:
        user: The :class:`UserRequestModel` instance to add to the database.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a :class:`ResponseUserModel` instance corresponding to the user added to the database.
    """
    result: UserSchema = await repository.create_user(user=user, db=db)
    return ResponseUserModel.model_validate(result)


async def update_user(user: UpdateUserModel, db: AsyncSession) -> ResponseUserModel | None:
    """
    Service layer function to update a user from the database.

    Args:
        user: The :class:`UpdateUserModel` instance to update from the database.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a :class:`ResponseUserModel` instance corresponding to the user updated to the database or None if the user was not found.
    """
    result = await repository.update_user(user=user, db=db)
    return ResponseUserModel.model_validate(result) if result else None


async def delete_user_by_uuid(uuid: UUID, db: AsyncSession) -> bool:
    """
    Service layer function to delete a user from the database.

    Args:
        uuid: the uuid primary key variable to make the query.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a `bool` to indicate the success or failure of the operation.
    """
    return await repository.delete_user_by_uuid(uuid=uuid, db=db)
