from .Model import Model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from datetime import timezone, datetime
from functools import partial
from string import capwords
from utils.helper import snakeCase


class Permission(Model):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    parent_id = Column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=True
    )
    created_at = Column(
        DateTime, nullable=False, default=partial(datetime.now, timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=partial(datetime.now, timezone.utc),
        onupdate=partial(datetime.now, timezone.utc),
    )

    # Mutators
    # ---- Mutator (auto-generate slug from label) ----
    @validates("label")
    def generateSlug(self, key, value: str):
        value = capwords(value)
        self.slug = snakeCase(value)
        return value
