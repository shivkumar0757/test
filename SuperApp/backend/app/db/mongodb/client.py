"""
MongoDB client module.
"""

import logging
from typing import Optional, Callable, Any
from functools import lru_cache, wraps
from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global client variable
_client: Optional[AsyncIOMotorClient] = None


class MongoDBClientManager:
    """MongoDB client manager with dependency injection support."""
    
    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
    
    async def get_client(self, client: Optional[AsyncIOMotorClient] = None) -> AsyncIOMotorClient:
        """Get MongoDB client, optionally setting a new client."""
        if client is not None:
            self._client = client
            logger.debug("MongoDB client set")
        
        if self._client is None:
            logger.debug("Creating new MongoDB client")
            self._client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        return self._client
    
    async def get_db(self, db_name: Optional[str] = None) -> AsyncIOMotorDatabase:
        """Get MongoDB database."""
        client = await self.get_client()
        db_name = db_name or settings.MONGODB_DB_NAME
        return client[db_name]
    
    async def close(self):
        """Close MongoDB client."""
        if self._client:
            logger.debug("Closing MongoDB client")
            self._client.close()
            self._client = None


# Create global manager instance
_manager = MongoDBClientManager()


@lru_cache()
def get_mongodb_client():
    """Get MongoDB client dependency."""
    async def dependency(client: Optional[AsyncIOMotorClient] = None) -> AsyncIOMotorClient:
        return await _manager.get_client(client)
    return dependency


@lru_cache()
def get_mongodb_db():
    """Get MongoDB database dependency."""
    async def dependency(db_name: Optional[str] = None) -> AsyncIOMotorDatabase:
        return await _manager.get_db(db_name)
    return dependency


async def close_mongodb_client():
    """Close MongoDB client."""
    await _manager.close()


@asynccontextmanager
async def mongodb_transaction():
    """MongoDB transaction context manager.
    
    Note: Transactions require a replica set.
    """
    client = await _manager.get_client()
    session = await client.start_session()
    try:
        await session.start_transaction()
        yield session
        await session.commit_transaction()
    except Exception as e:
        await session.abort_transaction()
        logger.error(f"MongoDB transaction error: {e}")
        raise
    finally:
        await session.end_session()


def with_mongodb_transaction(func: Callable) -> Callable:
    """Decorator to wrap a function with a MongoDB transaction."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with mongodb_transaction() as session:
            kwargs['session'] = session
            return await func(*args, **kwargs)
    return wrapper 