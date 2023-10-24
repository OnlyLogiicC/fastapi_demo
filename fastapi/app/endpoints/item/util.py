from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, PastDatetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ListingModel(BaseModel):
    """Base Model of item"""

    model_config = ConfigDict(
        from_attributes=True,
    )


class CreateItemModel(ListingModel):
    """Model used for creating a item"""

    user_id: UUID
    name: str


class UpdateItemModel(ListingModel):
    """Model used for updating the item"""

    id: UUID
    name: str


class ResponseItemModel(ListingModel):
    """Model returned when converting from ItemSchema"""

    id: UUID
    name: str
    created_on: PastDatetime
    updated_on: PastDatetime
    user_id: UUID


class ItemSchema(Base):
    """Schema mirroring the items table in the database"""

    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(init=False, primary_key=True, server_default=func.uuid_generate_v4())
    name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_on: Mapped[datetime] = mapped_column(init=False, nullable=False, server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        init=False, nullable=False, onupdate=func.now(), server_default=func.now()
    )

    def update_from_model(self, model: UpdateItemModel) -> None:
        for field, value in model.model_dump().items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)
