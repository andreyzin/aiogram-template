from typing import Any, List, Sequence
from typing_extensions import Self
from sqlalchemy import JSON, MetaData, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declared_attr, registry

mapper_registry = registry()


@as_declarative()
class Base:
    __abstract__ = True

    metadata = MetaData()

    type_annotation_map = {dict[str, Any]: JSON}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    def __repr__(self):
        return f"{self.__class__.__name__}<{','.join([f'{i}={v}' for i, v in self.__dict__.items() if not i.startswith('_')])}>"

    @classmethod
    async def find_many(cls, session: AsyncSession, **filter_by) -> Sequence[Self]:
        req = await session.execute(select(cls).filter_by(**filter_by))
        res = req.scalars().all()
        return res

    @classmethod
    async def find_one(cls, session: AsyncSession, **filter_by):
        req = await session.execute(select(cls).filter_by(**filter_by))
        card = req.scalars().first()
        return card
