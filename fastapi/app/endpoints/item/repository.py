from typing import Sequence
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.future import select

from app.core.database import AsyncSession
from app.core.logger import logger_factory
from app.endpoints.item.util import ItemSchema, CreateItemModel, UpdateItemModel

logger = logger_factory(__name__)


async def get_items(db: AsyncSession) -> Sequence[ItemSchema]:
    """
    Repository layer function to retreive items stored in the database.

    Args:
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        A sequence of :class:`ItemSchema`.
    """
    statement = select(ItemSchema)
    result = (await db.scalars(statement)).unique().all()
    logger.debug(f"get_items() -> {result}")
    return result


async def get_items_count(db: AsyncSession) -> int:
    """
    Repository layer function to get the number of items stored in the database.

    Args:
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The number of items stored in the database as an integer.
    """
    statement = select(func.count()).select_from(ItemSchema)
    result = await db.scalar(statement)
    logger.debug(f"get_items_count() -> {result}")
    return result if result else 0


async def get_item_by_uuid(uuid: UUID, db: AsyncSession) -> ItemSchema | None:
    """
    Repository layer function to query a item by his primary key.

    Args:
        uuid: the uuid variable to make the query
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The item corresponding to the uuid as a :class:`ItemSchema` instance, if present in the database, else None.
    """
    result = await db.get(ItemSchema, uuid)
    logger.debug(f"get_listing_by_uuid({uuid}) -> {result}")
    return result


async def create_item(item: CreateItemModel, db: AsyncSession) -> ItemSchema:
    """
    Repository layer function to add a new item to the database

    Args:
        item: The :class:`CreateItemModel` instance to add to the database.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a :class:`ItemSchema` instance corresponding to the item added to the database.
    """
    schema: ItemSchema = ItemSchema(**item.model_dump())
    db.add(schema)
    await db.flush()
    logger.debug(f"create_item({item}) -> {schema}")
    return schema


async def update_item(item: UpdateItemModel, db: AsyncSession) -> ItemSchema | None:
    """
    Repository layer function to update an item from the database

    Args:
        item: The :class:`UpdateItemModel` instance to update in the database.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a :class:`ItemSchema` instance corresponding to the item updated to the database or None if the item was not found.
    """
    schema: ItemSchema | None = await db.get(ItemSchema, item.id)
    if schema is None:
        return None
    schema.update_from_model(item)
    await db.flush()
    await db.refresh(schema)
    logger.debug(f"update_item({item!r}) -> {schema}")
    return schema


async def delete_item_by_uuid(uuid: UUID, db: AsyncSession) -> bool:
    """
    Repository layer function to delete an item from the database.

    Args:
        uuid: the uuid primary key variable to make the query.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a `bool` to indicate the success or failure of the operation.
    """
    schema: ItemSchema | None = await db.get(ItemSchema, uuid)
    logger.debug(f"delete_item_by_uuid({uuid}) -> {schema}")
    if schema is None:
        return False
    await db.delete(schema)
    return True
