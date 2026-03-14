from typing import Type, TypeVar, Optional
from app.Core.Database import Base
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
    async def query(cls: Type[T], statement):
        async with cls.get_session() as session:
            result = await session.execute(statement)
            return result

    @classmethod
    async def first(cls: Type[T]) -> T | None:
        async with cls.get_session() as session:
            result = await session.execute(select(cls))
            return result.scalars().first()

    def toDict(self, exclude: Optional[list | str] = None):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if exclude is None
            or (isinstance(exclude, str) and exclude != column.name)
            or column.name not in exclude
        }
