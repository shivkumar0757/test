"""
PostgreSQL models for vector storage.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres.base import Base, TimestampMixin


try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Mock Vector type for development without pgvector
    class Vector:
        """Mock Vector type."""
        
        def __init__(self, dimensions):
            self.dimensions = dimensions


class UserTable(Base, TimestampMixin):
    """User table for PostgreSQL."""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ApiKeyTable(Base, TimestampMixin):
    """API key table for PostgreSQL."""
    
    __tablename__ = "api_keys"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    service: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key: Mapped[str] = mapped_column(String(512), nullable=False)
    masked_key: Mapped[str] = mapped_column(String(255), nullable=False)
    quota_limit: Mapped[int] = mapped_column(Integer, default=100000)
    quota_used: Mapped[int] = mapped_column(Integer, default=0)
    quota_reset_date: Mapped[datetime] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user = relationship("UserTable", back_populates="api_keys")


# Add relationship to UserTable
UserTable.api_keys = relationship("ApiKeyTable", back_populates="user", cascade="all, delete-orphan")


class QuotaShareTable(Base, TimestampMixin):
    """Quota share table for PostgreSQL."""
    
    __tablename__ = "quota_shares"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    api_key_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("api_keys.id", ondelete="CASCADE"))
    shared_with_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    quota_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    api_key = relationship("ApiKeyTable")
    user = relationship("UserTable", foreign_keys=[shared_with_user_id])


class LinkedInProfileTable(Base, TimestampMixin):
    """LinkedIn profile table for PostgreSQL."""
    
    __tablename__ = "linkedin_profiles"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    linkedin_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    profile_url: Mapped[Optional[str]] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    industry: Mapped[Optional[str]] = mapped_column(String(255))
    profile_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    last_updated: Mapped[datetime] = mapped_column(DateTime)
    
    # Relationships
    user = relationship("UserTable")
    experiences = relationship("LinkedInExperienceTable", back_populates="profile", cascade="all, delete-orphan")
    education = relationship("LinkedInEducationTable", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("LinkedInSkillTable", back_populates="profile", cascade="all, delete-orphan")
    posts = relationship("LinkedInPostTable", back_populates="profile", cascade="all, delete-orphan")


class LinkedInExperienceTable(Base, TimestampMixin):
    """LinkedIn experience table for PostgreSQL."""
    
    __tablename__ = "linkedin_experiences"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    profile_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("linkedin_profiles.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(Text)
    skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(255)))
    
    # Relationships
    profile = relationship("LinkedInProfileTable", back_populates="experiences")


class LinkedInEducationTable(Base, TimestampMixin):
    """LinkedIn education table for PostgreSQL."""
    
    __tablename__ = "linkedin_education"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    profile_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("linkedin_profiles.id", ondelete="CASCADE"))
    school: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[Optional[str]] = mapped_column(String(255))
    field_of_study: Mapped[Optional[str]] = mapped_column(String(255))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    profile = relationship("LinkedInProfileTable", back_populates="education")


class LinkedInSkillTable(Base, TimestampMixin):
    """LinkedIn skill table for PostgreSQL."""
    
    __tablename__ = "linkedin_skills"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    profile_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("linkedin_profiles.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    endorsements: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    profile = relationship("LinkedInProfileTable", back_populates="skills")


class LinkedInPostTable(Base, TimestampMixin):
    """LinkedIn post table for PostgreSQL."""
    
    __tablename__ = "linkedin_posts"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    profile_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("linkedin_profiles.id", ondelete="CASCADE"))
    linkedin_post_id: Mapped[Optional[str]] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    media_urls: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(255)))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    engagement_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=lambda: {
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "impressions": 0,
        "clicks": 0
    })
    # Vector field for embedding
    content_embedding: Mapped[Optional[Any]] = mapped_column(Vector(1536))
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    generation_params: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    ai_engagement_prediction: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(100)))
    
    # Relationships
    user = relationship("UserTable")
    profile = relationship("LinkedInProfileTable", back_populates="posts")


class DocumentTable(Base, TimestampMixin):
    """Document table for RAG system."""
    
    __tablename__ = "documents"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user = relationship("UserTable")
    chunks = relationship("DocumentChunkTable", back_populates="document", cascade="all, delete-orphan")


class DocumentChunkTable(Base, TimestampMixin):
    """Document chunk table for RAG system."""
    
    __tablename__ = "document_chunks"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    document_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    start_idx: Mapped[Optional[int]] = mapped_column(Integer)
    end_idx: Mapped[Optional[int]] = mapped_column(Integer)
    page_number: Mapped[Optional[int]] = mapped_column(Integer)
    section_title: Mapped[Optional[str]] = mapped_column(String(255))
    # Vector field for embedding
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(1536))
    
    # Relationships
    document = relationship("DocumentTable", back_populates="chunks")


class RefreshToken(Base, TimestampMixin):
    """Refresh token table."""
    
    __tablename__ = "refresh_tokens"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String(512), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("UserTable") 