from uuid import UUID
from app.core.database import AsyncSession

from app.endpoints.item.util import ResponseItemModel, ItemSchema, CreateItemModel, UpdateItemModel
import app.endpoints.item.repository as repository


async def get_items(db: AsyncSession) -> list[ResponseItemModel]:
    """
    Service layer function to get the items stored in the database.

    Args:
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        A list of :class:`ResponseItemModel`.
    """
    result = await repository.get_items(db)
    return [ResponseItemModel.model_validate(s) for s in result]


async def get_items_count(db: AsyncSession) -> int:
    """
    Service layer function to get the number of items stored in the database.

    Args:
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The number of items stored in the database as an integer.
    """
    return await repository.get_items_count(db)


async def get_item_by_uuid(uuid: UUID, db: AsyncSession) -> ResponseItemModel | None:
    """
    Service layer function to query an item by his uuid primary key.

    Args:
        uuid: the uuid primary key variable to make the query
        db: The :class:`AsyncSession` to connect to the database.

    Returns:
        The item corresponding to the uuid as a :class:`ResponseItemModel` instance, if present in the database, else None.
    """
    result = await repository.get_item_by_uuid(uuid, db)
    return ResponseItemModel.model_validate(result) if result else None


async def create_item(item: CreateItemModel, db: AsyncSession) -> ResponseItemModel:
    """
    Service layer function to create an item to the database.

    Args:
        item: The :class:`CreateItemModel` instance to add to the database.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a :class:`ResponseItemModel` instance corresponding to the item added to the database.
    """
    result: ItemSchema = await repository.create_item(item, db)
    return ResponseItemModel.model_validate(result)


async def update_item(item: UpdateItemModel, db: AsyncSession) -> ResponseItemModel | None:
    """
    Service layer function to update an item from the database.

    Args:
        user: The :class:`UpdateItemModel` instance to update from the database.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a :class:`ResponseItemModel` instance corresponding to the item updated in the database or None if the item was not found.
    """
    result = await repository.update_item(item=item, db=db)
    return ResponseItemModel.model_validate(result) if result else None


async def delete_item_by_uuid(uuid: UUID, db: AsyncSession) -> bool:
    """
    Service layer function to delete an item from the database.

    Args:
        uuid: the uuid primary key variable to make the query.
        db: The :class:`AsyncSession` to connect to the database.

    Return:
        a `bool` to indicate the success or failure of the operation.
    """
    return await repository.delete_item_by_uuid(uuid=uuid, db=db)
