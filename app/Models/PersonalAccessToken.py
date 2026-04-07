from .Model import Model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import timezone, datetime
from functools import partial


class PersonalAccessToken(Model):
    __tablename__ = "personal_access_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=partial(datetime.now, timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=partial(datetime.now, timezone.utc),
        onupdate=partial(datetime.now, timezone.utc),
    )
