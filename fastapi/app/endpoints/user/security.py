from typing import Annotated
from datetime import datetime, timedelta, timezone
from uuid import UUID

from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel, ValidationError, EmailStr
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes, OAuth2PasswordBearer

from app.core.logger import logger_factory
from app.core.database import AsyncSession, get_db
from app.core.config import get_settings
from app.core.scopes import scopes_description, scopes
from app.endpoints.user.util import ResponseUserModel
import app.endpoints.user.service as user_service

logger = logger_factory(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=scopes_description)  # type: ignore
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    """Stores an access_token and his type."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Stores the data decoded from a token"""

    uuid: UUID
    scopes: list[str] = []
    epoch_expire: datetime


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain_password against the hashed_password.

    Args:
        plain_password: the string to verify against the hashed password.
        hashed_password: the hashed password.

    Returns:
        Returns a `bool` to tell if the plain_password corresponds to the hashed one.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_hashed_password(plain_password: str) -> str:
    """Returnes the hashed version of the password based on the `pwd_context`.

    Args:
        plain_password: the string to hash.

    Returns:
        Returns the hashed password as a `str`."""
    return pwd_context.hash(plain_password)


def create_access_token(data: dict[str, str | list[scopes] | datetime]) -> str:
    """Creates an access token from the data given. Gives it an expire date based on the settings.

    Args:
        data: a `dict` containing the JSON data to encode in the token.

    Returns:
        Returns a token as a `str`"""
    to_encode = data.copy()
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, settings.JWT_SECRET.get_secret_value(), algorithm=settings.JWT_ALGORITHM)
    return encoded_token


async def authenticate_user(email: str, plain_password: str, db: AsyncSession) -> ResponseUserModel:
    """Authenticate the user based on on email and password.

    Args:
        email: the email `str` of the user to query the user in the database.
        plain_password: the plain password to compare to the hashed password stored in the database.

    Returns:
        Returns a :class:`ResponseUserModel` of the user if the credentials given were valid. Else returns None.

    Raises:
        HTTPException: when the credentials are invalid. Should propagate to the endpoint to go back in the HTTP Response
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user, hashed_password = await user_service.get_user_with_password_by_email(email=email, db=db)
    if user is None or hashed_password is None or not verify_password(plain_password, hashed_password):
        raise credentials_exception
    return user


async def verify_jwt(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResponseUserModel:
    """Check the validity of the token against database and security_scopes.

    Args:
        security_scopes: The scopes against which to validate the user's permissions encoded in the token.
        token: the token storing the user's data and permissions.

    Returns:
        Returns a :class:`ResponseUserModel` of the user if the credentials given were valid. Else returns None.

    Raises:
        HTTPException: when the credentials are invalid. Should propagate to the endpoint to go back in the HTTP Response
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        settings = get_settings()
        decoded_payload = jwt.decode(
            token=token, key=settings.JWT_SECRET.get_secret_value(), algorithms=[settings.JWT_ALGORITHM]
        )
        token_expire = decoded_payload.get("exp")
        token_uuid = decoded_payload.get("sub")
        if token_uuid is None or token_expire is None:
            raise credentials_exception
        token_scopes = decoded_payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, uuid=token_uuid, epoch_expire=token_expire)
    except (JWTError, ValidationError) as e:
        raise credentials_exception
    user = await user_service.get_user_by_uuid(uuid=token_data.uuid, db=db)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user
