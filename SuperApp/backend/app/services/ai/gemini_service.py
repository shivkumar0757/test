"""
Gemini API service for AI-powered content generation.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google's Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service with API key."""
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("No Gemini API key provided")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Default model
        self.default_model_name = "gemini-pro"
        self.default_model = genai.GenerativeModel(self.default_model_name)
        
        # Model for vision tasks
        self.vision_model_name = "gemini-pro-vision"
        self.vision_model = genai.GenerativeModel(self.vision_model_name)
        
        logger.info(f"Gemini service initialized with models: {self.default_model_name}, {self.vision_model_name}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        max_output_tokens: int = 1024,
        safety_settings: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: Input prompt for text generation
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            max_output_tokens: Maximum number of tokens to generate
            safety_settings: Safety settings for content filtering
            
        Returns:
            Generated text and metadata
        """
        start_time = time.time()
        
        try:
            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_output_tokens,
            }
            
            # Generate content
            response = self.default_model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # in milliseconds
            
            # Parse response
            return {
                "text": response.text,
                "usage": {
                    "prompt_tokens": 0,  # Not provided by Gemini API
                    "completion_tokens": 0,  # Not provided by Gemini API
                    "total_tokens": 0,  # Not provided by Gemini API
                    "latency_ms": latency,
                },
                "model": self.default_model_name,
            }
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        max_output_tokens: int = 1024,
        safety_settings: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate chat response using Gemini API.
        
        Args:
            messages: List of message objects with 'role' and 'content' keys
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            max_output_tokens: Maximum number of tokens to generate
            safety_settings: Safety settings for content filtering
            
        Returns:
            Generated response and metadata
        """
        start_time = time.time()
        
        try:
            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_output_tokens,
            }
            
            # Convert messages format
            history = []
            latest_message = None
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                # Convert role (user, assistant) to Gemini format (user, model)
                gemini_role = "model" if role == "assistant" else role
                
                # Add to history or set as latest message
                if len(history) > 0 or gemini_role == "system":
                    history.append({"role": gemini_role, "parts": [{"text": content}]})
                else:
                    latest_message = {"role": gemini_role, "parts": [{"text": content}]}
            
            # Create chat session with history
            chat = self.default_model.start_chat(history=history)
            
            # Generate response to the latest message
            if latest_message:
                response = chat.send_message(
                    latest_message["parts"][0]["text"],
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                )
            else:
                # If no user message, use an empty prompt
                response = chat.send_message(
                    "",
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                )
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # in milliseconds
            
            # Parse response
            return {
                "text": response.text,
                "usage": {
                    "prompt_tokens": 0,  # Not provided by Gemini API
                    "completion_tokens": 0,  # Not provided by Gemini API
                    "total_tokens": 0,  # Not provided by Gemini API
                    "latency_ms": latency,
                },
                "model": self.default_model_name,
            }
        except Exception as e:
            logger.error(f"Gemini Chat API error: {str(e)}")
            raise
    
    async def generate_linkedin_post(
        self,
        topic: str,
        tone: str = "professional",
        length: str = "medium",
        keywords: Optional[List[str]] = None,
        audience: Optional[str] = None,
        count: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Generate LinkedIn post variations.
        
        Args:
            topic: Post topic
            tone: Tone of the post (professional, casual, academic)
            length: Post length (short, medium, long)
            keywords: Keywords to include
            audience: Target audience
            count: Number of variations to generate
            
        Returns:
            List of post variations with engagement predictions
        """
        logger.info(f"Generating {count} LinkedIn post variations about '{topic}'")
        
        # Build prompt for post generation
        prompt = f"""
Generate {tone} LinkedIn posts about {topic} in {length} length format.
{f"Include these keywords if relevant: {', '.join(keywords)}." if keywords else ""}
{f"Target audience: {audience}." if audience else ""}

Create {count} variations of LinkedIn posts, each with a different style and approach.
Each post should be engaging, professional, and optimized for LinkedIn's algorithm.
Include relevant hashtags at the end of each post.

Format the response as {count} distinct posts labeled as "Variation 1:", "Variation 2:", etc.
        """
        
        # Generate content
        result = await self.generate_text(
            prompt=prompt,
            temperature=0.8,  # Higher temperature for creative variations
            max_output_tokens=2048,  # More tokens for multiple variations
        )
        
        # Parse variations from the generated text
        variations = []
        raw_text = result["text"]
        
        # Split by variation labels
        import re
        variation_pattern = re.compile(r"Variation\s+(\d+):(.*?)(?=Variation\s+\d+:|$)", re.DOTALL)
        matches = variation_pattern.findall(raw_text)
        
        for _, content in matches:
            content = content.strip()
            if content:
                variations.append({
                    "content": content,
                    "ai_engagement_prediction": await self._predict_engagement(),
                })
        
        # If no variations found or parsing failed, create a single variation
        if not variations:
            variations.append({
                "content": raw_text,
                "ai_engagement_prediction": await self._predict_engagement(),
            })
        
        logger.info(f"Generated {len(variations)} LinkedIn post variations")
        return variations
    
    async def analyze_linkedin_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze LinkedIn content for SEO and engagement potential.
        
        Args:
            content: LinkedIn post content
            
        Returns:
            Analysis results
        """
        logger.info("Analyzing LinkedIn content")
        
        # Build prompt for content analysis
        prompt = f"""
Analyze this LinkedIn post for SEO optimization and engagement potential:

"{content}"

Provide an analysis with the following information:
1. Overall engagement score (0-100)
2. SEO score (0-100)
3. Readability analysis
4. Sentiment analysis
5. Present keywords
6. Missing keywords that would improve engagement
7. Trending keywords that could be included
8. Specific improvement suggestions

Format the response as a structured analysis.
        """
        
        # Generate analysis
        result = await self.generate_text(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_output_tokens=1024,
        )
        
        # Parse analysis - in a production environment, we'd use a more robust parsing method
        # For demonstration, we'll return a structured mock response
        return {
            "engagement_score": 85,
            "seo_score": 78,
            "readability": {
                "score": 72,
                "level": "Professional",
                "suggestions": [
                    "Consider breaking up the second paragraph for improved readability",
                    "Add one more relevant hashtag to increase discoverability"
                ]
            },
            "sentiment": {
                "overall": "positive",
                "strength": "moderate"
            },
            "keywords": {
                "present": ["AI", "machine learning", "recommendations"],
                "missing": ["data", "algorithm", "improvement"],
                "trending": ["AI ethics", "responsible AI", "ML ops"]
            },
            "improvement_suggestions": [
                "Add a call to action at the end of your post",
                "Include a specific achievement or metric for credibility",
                "Consider adding an industry-specific hashtag for better targeting"
            ]
        }
    
    async def optimize_linkedin_profile(
        self,
        profile: Dict[str, Any],
        target_role: str,
        industry: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Optimize LinkedIn profile for target role.
        
        Args:
            profile: LinkedIn profile data
            target_role: Target role to optimize for
            industry: Industry context
            
        Returns:
            Optimization suggestions
        """
        logger.info(f"Optimizing LinkedIn profile for '{target_role}'")
        
        # Build prompt for profile optimization
        prompt = f"""
Analyze this LinkedIn profile and provide optimization suggestions for the target role of {target_role}
{f"in the {industry} industry" if industry else ""}.

Current LinkedIn Profile:
- Headline: {profile.get("headline", "Not provided")}
- Summary: {profile.get("summary", "Not provided")}
- Experience: {str(profile.get("experience", []))[:500]}
- Skills: {", ".join(profile.get("skills", []))[:300] if isinstance(profile.get("skills", []), list) else "Not provided"}

Provide specific suggestions to improve:
1. The headline (make it more attention-grabbing and specific)
2. The summary (highlight relevant achievements and skills for {target_role})
3. Skills to add, remove, or prioritize for {target_role}

Format your response as JSON with these sections: headline, summary, skills.
        """
        
        # Generate optimization suggestions
        result = await self.generate_text(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more focused suggestions
            max_output_tokens=1024,
        )
        
        # Parse the response - in a production environment, we'd parse the JSON
        # For demonstration, we'll return structured mock data
        return {
            "headline": {
                "current": profile.get("headline", "Not provided"),
                "suggestion": f"Senior {target_role} specializing in AI-driven applications",
                "explanation": f"This headline directly mentions your seniority level and specialization, making it more targeted for {target_role} roles."
            },
            "summary": {
                "current": profile.get("summary", "Not provided"),
                "suggestion": f"Results-driven professional with extensive experience in {target_role} roles. Specializing in AI applications and innovative solutions.",
                "explanation": f"The revised summary emphasizes your experience with roles relevant to {target_role} and highlights key technologies."
            },
            "skills": {
                "add": ["Machine Learning", "TensorFlow", "API Design", "System Architecture"],
                "remove": [],
                "prioritize": ["AI", "Machine Learning", "Cloud Architecture"]
            }
        }
    
    async def _predict_engagement(self) -> Dict[str, str]:
        """
        Predict engagement metrics for a post.
        
        Returns:
            Engagement predictions (low, medium, high)
        """
        # Simple mock implementation for demonstration
        # In a real implementation, this would use a ML model
        import random
        
        levels = ["low", "medium", "high"]
        return {
            "likes": random.choice(levels),
            "comments": random.choice(levels),
            "shares": random.choice(levels),
        } 