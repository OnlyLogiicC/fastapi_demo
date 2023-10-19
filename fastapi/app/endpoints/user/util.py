from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, ConfigDict, PastDatetime, EmailStr, Field
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.scopes import scopes

from app.endpoints.item.util import ItemSchema, ResponseItemModel


class UserRole(str, Enum):
    member = "member"
    admin = "admin"
    super_admin = "super_admin"


scopes_dict: dict[UserRole, list[scopes]] = {
    UserRole.member: ["users:view", "address:view"],
    UserRole.admin: ["users:view", "users:edit", "address:view", "address:edit"],
    UserRole.super_admin: [
        "users:view",
        "users:edit",
        "address:view",
        "address:edit",
        "system_config",
    ],
}


class UserModel(BaseModel):
    """Base Model of user"""

    model_config = ConfigDict(from_attributes=True)


class CreateUserModel(UserModel):
    """Model used for creating an user"""

    email: EmailStr
    name: str
    password: str


class UpdateUserModel(UserModel):
    """Model used for modifying an user"""

    id: UUID
    name: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None)


class ResponseUserModel(UserModel):
    """Model returned when converting from UserSchema"""

    model_config = ConfigDict(extra="ignore")

    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    created_on: PastDatetime
    updated_on: PastDatetime
    is_disabled: bool
    items: list[ResponseItemModel]

    def get_scopes(self) -> list[scopes]:
        return scopes_dict.get(self.role, [])


class UserSchema(Base):
    """Schema mirroring the users table in the database"""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(init=False, primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(init=False, nullable=False, insert_default=UserRole.member)
    created_on: Mapped[datetime] = mapped_column(init=False, nullable=False, server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        init=False, nullable=False, onupdate=func.now(), server_default=func.now()
    )
    items: Mapped[list[ItemSchema]] = relationship(
        init=False, cascade="all, delete-orphan", passive_deletes=True, lazy="joined"
    )
    is_disabled: Mapped[bool] = mapped_column(init=False, nullable=False, server_default="false")

    def update_from_model(self, model: UpdateUserModel) -> None:
        for field, value in model.model_dump().items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)
