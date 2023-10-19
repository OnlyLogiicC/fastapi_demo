from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security, HTTPException, Path

from app.core.database import AsyncSession, get_db
import app.endpoints.user.security as security
from app.endpoints.item.util import ResponseItemModel, CreateItemModel, UpdateItemModel
import app.endpoints.item.service as service

router = APIRouter(prefix="/item", tags=["Items"])


@router.get(
    "",
    response_model=list[ResponseItemModel],
    dependencies=[Security(security.verify_jwt)],
    description="Get the items stored in the database",
)
async def get_items(db: Annotated[AsyncSession, Depends(get_db)]) -> list[ResponseItemModel]:
    return await service.get_items(db=db)


@router.get(
    "/count",
    response_model=int,
    dependencies=[Security(security.verify_jwt)],
    description="Get the number of items stored in the database",
)
async def get_items_count(db: Annotated[AsyncSession, Depends(get_db)]) -> int:
    return await service.get_items_count(db)


@router.get(
    "/{uuid}",
    response_model=ResponseItemModel,
    dependencies=[Security(security.verify_jwt)],
    description="Get an item by uuid (primary key) stored in the database",
)
async def get_item_by_uuid(
    uuid: Annotated[UUID, Path(title="uuid to query the listing")], db: Annotated[AsyncSession, Depends(get_db)]
) -> ResponseItemModel:
    result = await service.get_item_by_uuid(uuid, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result


@router.post(
    "",
    response_model=ResponseItemModel,
    dependencies=[Security(security.verify_jwt)],
    status_code=201,
    description="Create a new item",
)
async def add_item(item: CreateItemModel, db: Annotated[AsyncSession, Depends(get_db)]) -> ResponseItemModel:
    return await service.create_item(item=item, db=db)


@router.put(
    "",
    response_model=ResponseItemModel,
    dependencies=[Security(security.verify_jwt)],
    status_code=201,
    description="Modify an item",
)
async def update_item(item: UpdateItemModel, db: Annotated[AsyncSession, Depends(get_db)]) -> ResponseItemModel:
    result = await service.update_item(item=item, db=db)
    if not result:
        raise HTTPException(status_code=404, detail="Item to update not found")
    return result


@router.delete(
    "/{uuid}",
    status_code=204,
    dependencies=[Security(security.verify_jwt)],
    description="Delete an item by his uuid primary key",
)
async def delete_item_by_uuid(
    uuid: Annotated[UUID, Path(title="uuid of the item to delete")], db: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    result = await service.delete_item_by_uuid(uuid=uuid, db=db)
    if not result:
        raise HTTPException(status_code=404, detail="item not found")
