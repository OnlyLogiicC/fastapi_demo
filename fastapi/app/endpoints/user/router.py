from typing import Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from uuid import UUID

from app.endpoints.user.util import CreateUserModel, ResponseUserModel, UpdateUserModel
import app.endpoints.user.security as security
import app.endpoints.user.service as user_service
from app.core.database import AsyncSession, get_db


auth_router = APIRouter(tags=["Token"])


@auth_router.post("/token", response_model=security.Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]
):
    user = await security.authenticate_user(form_data.username, form_data.password, db)
    access_token = security.create_access_token(data={"sub": str(user.id), "scopes": user.get_scopes()})
    return {"access_token": access_token, "token_type": "bearer"}


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get(
    "",
    response_model=list[ResponseUserModel],
    dependencies=[Security(security.verify_jwt, scopes=["users:view"])],
    description="Get the users stored in the database",
)
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]) -> list[ResponseUserModel]:
    return await user_service.get_users(db=db)


@user_router.post(
    "",
    response_model=ResponseUserModel,
    status_code=201,
    # dependencies=[Security(security.verify_jwt, scopes=["users:edit"])],
    description="Create a new user",
)
async def create_user(user: CreateUserModel, db: Annotated[AsyncSession, Depends(get_db)]) -> ResponseUserModel:
    user.password = security.get_hashed_password(user.password)
    return await user_service.create_user(user=user, db=db)


@user_router.put(
    "",
    response_model=ResponseUserModel,
    status_code=201,
    dependencies=[Security(security.verify_jwt, scopes=["users:edit"])],
    description="Modify a user",
)
async def update_user(user: UpdateUserModel, db: Annotated[AsyncSession, Depends(get_db)]) -> ResponseUserModel:
    if user.password is not None:
        user.password = security.get_hashed_password(user.password)
    result = await user_service.update_user(user=user, db=db)
    if not result:
        raise HTTPException(status_code=404, detail="User to update not found")
    return result


@user_router.get(
    "/count",
    response_model=int,
    dependencies=[Security(security.verify_jwt, scopes=["users:view"])],
    description="Get the number of users stored in the database",
)
async def get_users_count(db: Annotated[AsyncSession, Depends(get_db)]) -> int:
    return await user_service.get_users_count(db=db)


@user_router.get("/me", response_model=ResponseUserModel, description="Get personnal user informations")
async def get_user_info(current_user: Annotated[ResponseUserModel, Depends(security.verify_jwt)]):
    return current_user


@user_router.get(
    "/{uuid}",
    response_model=ResponseUserModel,
    dependencies=[Security(security.verify_jwt, scopes=["users:view"])],
    description="Get a user by his uuid primary key",
)
async def get_user_by_uuid(
    uuid: Annotated[UUID, Path(title="uuid to query the user")], db: Annotated[AsyncSession, Depends(get_db)]
) -> ResponseUserModel:
    result = await user_service.get_user_by_uuid(uuid=uuid, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@user_router.delete(
    "/{uuid}",
    status_code=204,
    dependencies=[Security(security.verify_jwt, scopes=["users:edit"])],
    description="Delete a user by his uuid primary key",
)
async def delete_user_by_uuid(
    uuid: Annotated[UUID, Path(title="uuid of the user to delete")], db: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    result = await user_service.delete_user_by_uuid(uuid=uuid, db=db)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")


@user_router.get(
    "/email/{email}",
    response_model=ResponseUserModel,
    dependencies=[Security(security.verify_jwt, scopes=["users:view"])],
    description="Get a user by his email",
)
async def get_user_by_email(
    email: Annotated[EmailStr, Path(title="email to query the user")], db: Annotated[AsyncSession, Depends(get_db)]
) -> ResponseUserModel:
    result, _ = await user_service.get_user_with_password_by_email(email=email, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result
