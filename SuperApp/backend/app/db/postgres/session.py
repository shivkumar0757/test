"""
PostgreSQL session and engine management.
"""

import logging
from typing import AsyncGenerator, Optional, Callable, TypeVar, Generic, Any
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps

from sqlalchemy.ext.asyncio import (
    AsyncEngine, 
    AsyncSession, 
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Context variables to store engine and session factory
_engine_ctx: ContextVar[Optional[AsyncEngine]] = ContextVar("_engine", default=None)
_async_session_ctx: ContextVar[Optional[async_sessionmaker[AsyncSession]]] = ContextVar("_async_session", default=None)

T = TypeVar("T")


class ContextVarHolder(Generic[T]):
    """Context variable holder with get/set methods."""
    
    def __init__(self, ctx_var: ContextVar[Optional[T]], name: str):
        self._ctx_var = ctx_var
        self._name = name
    
    def get(self) -> T:
        """Get value from context variable."""
        value = self._ctx_var.get()
        if value is None:
            raise RuntimeError(f"{self._name} is not initialized")
        return value
    
    def set(self, value: T) -> None:
        """Set value in context variable."""
        self._ctx_var.set(value)


# Create holders for engine and session factory
get_db_engine = ContextVarHolder(_engine_ctx, "Database engine")
get_async_session = ContextVarHolder(_async_session_ctx, "Async session factory")


def create_engine() -> AsyncEngine:
    """Create SQLAlchemy engine."""
    logger.debug("Creating PostgreSQL engine")
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    get_db_engine.set(engine)
    return engine


def create_session_factory(engine: Optional[AsyncEngine] = None) -> async_sessionmaker[AsyncSession]:
    """Create SQLAlchemy session factory."""
    logger.debug("Creating PostgreSQL session factory")
    
    if engine is None:
        try:
            engine = get_db_engine.get()
        except RuntimeError:
            engine = create_engine()
    
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
    )
    get_async_session.set(session_factory)
    return session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    try:
        session_factory = get_async_session.get()
    except RuntimeError:
        create_session_factory()
        session_factory = get_async_session.get()
    
    async with session_factory() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise


@asynccontextmanager
async def db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Database transaction context manager."""
    try:
        session_factory = get_async_session.get()
    except RuntimeError:
        create_session_factory()
        session_factory = get_async_session.get()
    
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction error: {e}")
            raise


def with_db_transaction(func: Callable) -> Callable:
    """Decorator to wrap a function with a database transaction."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with db_transaction() as session:
            kwargs['session'] = session
            return await func(*args, **kwargs)
    return wrapper 