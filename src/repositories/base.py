from typing import Any, Generic, TypeVar, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel

from src.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base generic repository providing standard DB CRUD operations.
    Note: NO commit or rollback happens here per AI API Architecture rules.
    """
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    def create(self, db: AsyncSession, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        obj_in_data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        # Flush to get the IDs without committing the transaction.
        return db_obj

    def update(self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        obj_data = db_obj.__dict__
        update_data = obj_in.model_dump(exclude_unset=True) if isinstance(obj_in, BaseModel) else obj_in
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, id: Any) -> ModelType | None:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
        return obj
