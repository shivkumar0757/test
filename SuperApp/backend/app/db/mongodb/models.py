"""
MongoDB document models using Beanie ODM.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from beanie import Document, Indexed, TimeSeriesConfig, Link
from pydantic import BaseModel, Field, EmailStr


class BaseDocument(Document):
    """Base document model for all MongoDB documents."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        """Beanie document settings."""
        use_state_management = True
        validate_on_save = True


class UserSettings(BaseModel):
    """User settings model."""
    
    gemini_api_key: Optional[str] = None
    linkedin_integration: Optional[bool] = False
    email_notifications: Optional[bool] = True
    theme: Optional[str] = "light"
    language: Optional[str] = "en"


class User(BaseDocument):
    """User document model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    email: Indexed(str, unique=True)
    username: Indexed(str, unique=True)
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    settings: Optional[UserSettings] = Field(default_factory=UserSettings)
    
    class Settings:
        """Beanie document settings."""
        name = "users"
        use_state_management = True
        use_revision = True

    class Config:
        schema_extra = {
            "example": {
                "_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2023-01-01T00:00:00.000Z",
                "updated_at": "2023-01-01T00:00:00.000Z",
            }
        }


class ApiKey(BaseDocument):
    """API key document model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Indexed(str)
    service: str  # google, openai, linkedin, github, etc.
    name: str
    key: str  # Encrypted API key
    masked_key: str  # Masked version for display
    quota_limit: int = 100000
    quota_used: int = 0
    quota_reset_date: datetime
    is_active: bool = True
    
    class Settings:
        """Beanie document settings."""
        name = "api_keys"
        use_state_management = True


class ChatMessage(BaseModel):
    """Chat message model (embedded in ChatSession)."""
    
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(BaseDocument):
    """Chat session document model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Indexed(str)
    title: str = "New Conversation"
    model_id: str
    messages: List[ChatMessage] = []
    metadata: Dict[str, Any] = {}
    
    class Settings:
        """Beanie document settings."""
        name = "chat_sessions"
        use_state_management = True


class DocumentChunk(BaseModel):
    """Document chunk model (embedded in Document)."""
    
    content: str
    metadata: Dict[str, Any] = {}
    vector_id: Optional[str] = None
    vector_provider: str = "postgres"  # postgres, pinecone, qdrant, chroma


class Document(BaseDocument):
    """Document model for RAG system."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Indexed(str)
    title: str
    content: str
    metadata: Dict[str, Any] = {}
    chunks: List[DocumentChunk] = []
    is_processed: bool = False
    is_public: bool = False
    
    class Settings:
        """Beanie document settings."""
        name = "documents"
        use_state_management = True


class Experience(BaseModel):
    """Experience model (embedded in LinkedInProfile)."""
    
    title: str
    company: str
    location: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    skills: List[str] = []


class Education(BaseModel):
    """Education model (embedded in LinkedInProfile)."""
    
    school: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None


class Skill(BaseModel):
    """Skill model (embedded in LinkedInProfile)."""
    
    name: str
    endorsements: int = 0


class LinkedInProfile(BaseDocument):
    """LinkedIn profile document model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    linkedin_id: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    profile_data: Dict[str, Any] = {}
    ai_optimizations: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        """Beanie document settings."""
        name = "linkedin_profiles"
        use_state_management = True
        use_revision = True

    class Config:
        schema_extra = {
            "example": {
                "_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001", 
                "linkedin_id": "john-doe-123456",
                "headline": "AI Engineer | Python Developer | Machine Learning Enthusiast",
                "summary": "Experienced AI engineer with a passion for...",
                "created_at": "2023-01-01T00:00:00.000Z",
                "updated_at": "2023-01-01T00:00:00.000Z",
            }
        }


class EngagementMetrics(BaseModel):
    """Engagement metrics model (embedded in LinkedInPost)."""
    
    likes: int = 0
    comments: int = 0
    shares: int = 0
    impressions: int = 0
    clicks: int = 0


class AiEngagementPrediction(BaseModel):
    """AI engagement prediction for a post."""
    
    likes: str = Field(..., description="Predicted likes level")
    comments: str = Field(..., description="Predicted comments level")
    shares: str = Field(..., description="Predicted shares level")


class LinkedInPost(BaseDocument):
    """LinkedIn post document model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    content: str
    title: Optional[str] = None
    image_url: Optional[str] = None
    ai_generated: bool = False
    ai_engagement_prediction: Optional[AiEngagementPrediction] = None
    generation_params: Optional[Dict[str, Any]] = None
    is_published: bool = False
    published_at: Optional[datetime] = None
    linkedin_post_id: Optional[str] = None
    engagement_stats: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        """Beanie document settings."""
        name = "linkedin_posts"
        use_state_management = True
        use_revision = True

    class Config:
        schema_extra = {
            "example": {
                "_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "content": "This is a LinkedIn post about AI and machine learning...",
                "title": "The Future of AI",
                "ai_generated": True,
                "is_published": False,
                "tags": ["ai", "machine-learning"],
                "created_at": "2023-01-01T00:00:00.000Z",
                "updated_at": "2023-01-01T00:00:00.000Z",
            }
        }


async def init_beanie():
    """Initialize Beanie ODM with all document models."""
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings
    
    # Create MongoDB client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize Beanie with all document models
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            User,
            ApiKey,
            ChatSession,
            Document,
            LinkedInProfile,
            LinkedInPost,
        ],
    ) 