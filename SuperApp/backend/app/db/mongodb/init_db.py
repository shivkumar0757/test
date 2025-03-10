"""
MongoDB database initialization.
"""

import logging
import motor.motor_asyncio
from beanie import init_beanie

from app.core.config import settings
from app.db.mongodb.models import User, LinkedInPost, LinkedInProfile

logger = logging.getLogger(__name__)


async def init_mongodb():
    """
    Initialize MongoDB connection and Beanie ODM.
    
    This function:
    1. Creates a connection to MongoDB using the connection string from settings
    2. Initializes Beanie with the document models
    3. Creates indexes for the document models
    """
    try:
        logger.info("Connecting to MongoDB...")
        
        # Create client
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
        
        # Initialize Beanie with document models
        await init_beanie(
            database=client[settings.MONGODB_DB_NAME],
            document_models=[
                User,
                LinkedInPost,
                LinkedInProfile,
            ]
        )
        
        logger.info("MongoDB connection established successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise 