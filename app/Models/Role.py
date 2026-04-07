from .Model import Model
from functools import partial
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, validates
from datetime import timezone, datetime
from string import capwords
from utils.helper import snakeCase


class Role(Model):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime, nullable=False, default=partial(datetime.now, timezone.utc)
    )  # No parentheses
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
