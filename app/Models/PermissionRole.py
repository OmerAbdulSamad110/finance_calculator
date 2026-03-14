from sqlalchemy import Table, Column, Integer, ForeignKey
from app.Core.Database import Base

permission_role = Table(
    "permission_role",
    Base.metadata,
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)
