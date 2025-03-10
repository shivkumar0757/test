"""
Base classes for SQLAlchemy models.
"""

from datetime import datetime
from typing import Optional, Any

from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    # Use class name in lowercase as table name by default
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""
    
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """Mixin that adds uuid column as primary key."""
    
    id: Mapped[str] = mapped_column(primary_key=True, default=func.uuid_generate_v4())


class SoftDeleteMixin:
    """Mixin that adds deleted_at column for soft delete."""
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        default=None,
        nullable=True,
        index=True,
    )
    
    @property
    def is_deleted(self) -> bool:
        """Check if record is deleted."""
        return self.deleted_at is not None 