"""
Content creation endpoints for LinkedIn and other platforms.
"""

import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field

from app.db.mongodb.models import User, LinkedInPost, LinkedInProfile
from app.services.ai.gemini_service import GeminiService
from app.api.deps import get_current_active_user, get_user_gemini_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""
    
    topic: str = Field(..., description="Topic of the content")
    tone: str = Field(
        "professional", 
        description="Tone of the content",
        enum=["professional", "casual", "academic"]
    )
    length: str = Field(
        "medium", 
        description="Length of the content",
        enum=["short", "medium", "long"]
    )
    keywords: Optional[List[str]] = Field(
        None, 
        description="Keywords to include in the content"
    )
    audience: Optional[str] = Field(
        None, 
        description="Target audience for the content"
    )
    count: int = Field(
        3, 
        description="Number of content variations to generate",
        ge=1,
        le=5
    )


class AiEngagementPrediction(BaseModel):
    """AI engagement prediction model."""
    
    likes: str = Field(..., enum=["low", "medium", "high"])
    comments: str = Field(..., enum=["low", "medium", "high"])
    shares: str = Field(..., enum=["low", "medium", "high"])


class ContentVariation(BaseModel):
    """Content variation model."""
    
    content: str
    ai_engagement_prediction: AiEngagementPrediction


class ContentGenerationResponse(BaseModel):
    """Response model for content generation."""
    
    variations: List[ContentVariation]


class ContentAnalysisRequest(BaseModel):
    """Request model for content analysis."""
    
    content: str = Field(..., description="Content to analyze")
    platform: str = Field(
        "linkedin", 
        description="Platform the content is for",
        enum=["linkedin", "twitter", "facebook"]
    )


class ContentAnalysisResponse(BaseModel):
    """Response model for content analysis."""
    
    engagement_score: int = Field(..., ge=0, le=100)
    seo_score: int = Field(..., ge=0, le=100)
    readability: Dict[str, Any]
    sentiment: Dict[str, Any]
    keywords: Dict[str, Any]
    improvement_suggestions: List[str]


class LinkedInProfileOptimizationRequest(BaseModel):
    """Request model for LinkedIn profile optimization."""
    
    current_profile: Dict[str, Any] = Field(..., description="Current LinkedIn profile data")
    target_role: str = Field(..., description="Target role to optimize for")
    industry: Optional[str] = Field(None, description="Industry context")
    focus_areas: Optional[List[str]] = Field(None, description="Areas to focus on")


class LinkedInProfileOptimizationResponse(BaseModel):
    """Response model for LinkedIn profile optimization."""
    
    suggestions: Dict[str, Any]


@router.post(
    "/linkedin/post/generate",
    response_model=ContentGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate LinkedIn post variations",
    description="Generate multiple variations of LinkedIn posts based on topic, tone, and other parameters",
)
async def generate_linkedin_post(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    gemini_service: GeminiService = Depends(get_user_gemini_service),
):
    """Generate LinkedIn post variations."""
    logger.info(f"Generating LinkedIn post variations about '{request.topic}'")
    
    try:
        # Generate post variations
        variations = await gemini_service.generate_linkedin_post(
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            keywords=request.keywords,
            audience=request.audience,
            count=request.count,
        )
        
        # Save generated posts to database
        for variation in variations:
            post = LinkedInPost(
                user_id=current_user.id,
                content=variation["content"],
                ai_generated=True,
                ai_engagement_prediction=variation["ai_engagement_prediction"],
                generation_params={
                    "topic": request.topic,
                    "tone": request.tone,
                    "length": request.length,
                    "keywords": request.keywords,
                    "audience": request.audience,
                },
                tags=request.keywords or [],
            )
            await post.save()
        
        return {"variations": variations}
    except Exception as e:
        logger.error(f"Error generating LinkedIn post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate LinkedIn post: {str(e)}",
        )


@router.post(
    "/linkedin/post/analyze",
    response_model=ContentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze LinkedIn post",
    description="Analyze LinkedIn post for SEO optimization and engagement potential",
)
async def analyze_linkedin_post(
    request: ContentAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    gemini_service: GeminiService = Depends(get_user_gemini_service),
):
    """Analyze LinkedIn post."""
    logger.info("Analyzing LinkedIn post")
    
    try:
        # Analyze content
        analysis = await gemini_service.analyze_linkedin_content(request.content)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing LinkedIn post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze LinkedIn post: {str(e)}",
        )


@router.post(
    "/linkedin/profile/optimize",
    response_model=LinkedInProfileOptimizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimize LinkedIn profile",
    description="Optimize LinkedIn profile for target role",
)
async def optimize_linkedin_profile(
    request: LinkedInProfileOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    gemini_service: GeminiService = Depends(get_user_gemini_service),
):
    """Optimize LinkedIn profile."""
    logger.info(f"Optimizing LinkedIn profile for '{request.target_role}'")
    
    try:
        # Optimize profile
        suggestions = await gemini_service.optimize_linkedin_profile(
            profile=request.current_profile,
            target_role=request.target_role,
            industry=request.industry,
        )
        
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error optimizing LinkedIn profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize LinkedIn profile: {str(e)}",
        )


@router.get(
    "/linkedin/posts",
    status_code=status.HTTP_200_OK,
    summary="Get user's LinkedIn posts",
    description="Get all LinkedIn posts for the current user",
)
async def get_linkedin_posts(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    ai_generated: Optional[bool] = Query(None),
    is_published: Optional[bool] = Query(None),
):
    """Get all LinkedIn posts for the current user."""
    logger.info("Getting LinkedIn posts")
    
    try:
        # Build query
        query = {"user_id": current_user.id}
        
        if ai_generated is not None:
            query["ai_generated"] = ai_generated
            
        if is_published is not None:
            query["is_published"] = is_published
        
        # Get posts
        posts = await LinkedInPost.find(query).sort(-LinkedInPost.created_at).skip(skip).limit(limit).to_list()
        total = await LinkedInPost.find(query).count()
        
        return {
            "data": posts,
            "total": total,
            "limit": limit,
            "skip": skip,
        }
    except Exception as e:
        logger.error(f"Error getting LinkedIn posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get LinkedIn posts: {str(e)}",
        ) 