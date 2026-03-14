from .Model import Model
from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from functools import partial


class PasswordResetToken(Model):
    __tablename__ = "password_reset_tokens"
    email = Column(String(255), primary_key=True, index=True)
    token = Column(String(255), nullable=False, unique=True)
    created_at = Column(
        DateTime, nullable=False, default=partial(datetime.now, timezone.utc)
    )
