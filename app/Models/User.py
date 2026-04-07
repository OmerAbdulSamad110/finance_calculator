from .Model import Model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from datetime import timezone, datetime
from functools import partial
from libs.Hash import Hash


class User(Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(
        String(255), nullable=False
    )  # Note: minlength isn't validated at DB level
    role_id = Column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
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
    # ---- Mutator (auto-hash password) ----
    @validates("password")
    def validate_password(self, key, value):
        return Hash.make(value)
