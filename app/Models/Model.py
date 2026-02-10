from typing import Type, TypeVar
from app.Core.Database import Base, async_session
from contextlib import asynccontextmanager
from sqlalchemy import select

T = TypeVar("T", bound="Model")


class Model(Base):
    __abstract__ = True

    # add it with plural and pascal case liberary
    # @declared_attr
    # def __tablename__(cls):
    #     # Auto table naming: User -> users
    #     return cls.__name__.lower() + "s"

    @classmethod
    @asynccontextmanager
    async def get_session(cls):
        async with async_session() as session:
            yield session

    @classmethod
    async def query(cls: Type[T], statement):
        async with cls.get_session() as session:
            result = await session.execute(statement)
            return result

    @classmethod
    async def first(cls: Type[T]) -> T | None:
        async with cls.get_session() as session:
            result = await session.execute(select(cls))
            return result.scalars().first()

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
