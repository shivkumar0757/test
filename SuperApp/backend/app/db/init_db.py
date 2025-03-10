"""
Database initialization module.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import redis.asyncio as redis

from app.core.config import settings
from app.db.mongodb.client import get_mongodb_client, close_mongodb_client
from app.db.postgres.session import get_db_engine, get_async_session

logger = logging.getLogger(__name__)


async def init_mongodb():
    """Initialize MongoDB connection."""
    logger.info("Initializing MongoDB connection")
    
    # Create MongoDB client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Test connection
    try:
        # The ismaster command is cheap and does not require auth
        await client.admin.command('ismaster')
        logger.info("MongoDB connection successful")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise
    
    # Set client in app state
    await get_mongodb_client(client=client)
    
    return client


async def init_postgres():
    """Initialize PostgreSQL connection."""
    logger.info("Initializing PostgreSQL connection")
    
    # Create engine and session factory
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    
    # Test connection
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("PostgreSQL connection successful")
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        raise
    
    # Create sessionmaker
    async_session_factory = async_sessionmaker(
        engine, 
        expire_on_commit=False,
        autoflush=False,
    )
    
    # Set engine and session in app state
    get_db_engine.set(engine)
    get_async_session.set(async_session_factory)
    
    return engine, async_session_factory


async def init_redis():
    """Initialize Redis connection."""
    logger.info("Initializing Redis connection")
    
    # Create Redis client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URI,
            encoding="utf-8",
            decode_responses=True,
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection successful")
        
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        logger.warning("Continuing without Redis. Some features may not work correctly.")
        return None


async def init_vector_extensions():
    """Initialize vector extensions for PostgreSQL."""
    logger.info("Initializing vector extensions")
    
    if settings.VECTOR_DB_TYPE == "postgres":
        try:
            engine = get_db_engine()
            async with engine.begin() as conn:
                # Create pgvector extension if not exists
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            logger.info("Vector extension initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector extension: {e}")
            raise


async def init_db():
    """Initialize all database connections."""
    # Initialize MongoDB
    await init_mongodb()
    
    # Initialize PostgreSQL
    await init_postgres()
    
    # Initialize Redis (optional)
    await init_redis()
    
    # Initialize vector extensions
    await init_vector_extensions()
    
    logger.info("All database connections initialized successfully")


async def close_db_connections():
    """Close all database connections."""
    logger.info("Closing database connections")
    
    # Close MongoDB connection
    await close_mongodb_client()
    
    # Close PostgreSQL connection
    engine = get_db_engine()
    if engine:
        await engine.dispose()
    
    logger.info("Database connections closed") 