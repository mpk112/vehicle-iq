"""API rate limiting and fallback service."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.metrics import APIUsage
from app.core.config import settings

logger = logging.getLogger(__name__)


class APIRateLimiter:
    """Manages API rate limiting and automatic fallback."""
    
    # Daily rate limits (free tier)
    RATE_LIMITS = {
        "groq": 14400,  # Groq free tier: 14,400 requests per day
        "together_ai": 100000,  # Together.ai has higher limits
        "paddleocr": 999999,  # Self-hosted, no limit
        "yolo": 999999,  # Self-hosted, no limit
        "embeddings": 999999,  # Self-hosted, no limit
    }
    
    # Warning threshold (percentage)
    WARNING_THRESHOLD = 0.90  # 90%
    
    def __init__(self, db: Session):
        """Initialize rate limiter with database session."""
        self.db = db
    
    def track_request(
        self,
        service_name: str,
        success: bool = True,
        duration_ms: float = 0,
        endpoint: Optional[str] = None,
    ) -> None:
        """
        Track an API request.
        
        Args:
            service_name: Name of the service (groq, together_ai, etc.)
            success: Whether the request was successful
            duration_ms: Request duration in milliseconds
            endpoint: Optional endpoint path
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Check if we have a record for today
        usage = (
            self.db.query(APIUsage)
            .filter(
                APIUsage.service_name == service_name,
                APIUsage.date == today,
                APIUsage.endpoint == endpoint,
            )
            .first()
        )
        
        if usage:
            # Update existing record
            usage.request_count += 1
            if success:
                usage.success_count += 1
            else:
                usage.failure_count += 1
            usage.total_duration_ms += duration_ms
        else:
            # Create new record
            usage = APIUsage(
                service_name=service_name,
                endpoint=endpoint,
                request_count=1,
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                total_duration_ms=duration_ms,
                date=today,
            )
            self.db.add(usage)
        
        self.db.commit()
        
        # Check if we're approaching the limit
        if usage.request_count >= self.RATE_LIMITS.get(service_name, 999999) * self.WARNING_THRESHOLD:
            logger.warning(
                f"API usage for {service_name} is at {usage.request_count} "
                f"({usage.request_count / self.RATE_LIMITS.get(service_name, 999999) * 100:.1f}% of daily limit)"
            )
    
    def check_rate_limit(self, service_name: str) -> Dict[str, Any]:
        """
        Check if service has exceeded rate limit.
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            Dict with rate limit status
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Get today's usage
        usage = (
            self.db.query(func.sum(APIUsage.request_count))
            .filter(
                APIUsage.service_name == service_name,
                APIUsage.date == today,
            )
            .scalar()
        ) or 0
        
        limit = self.RATE_LIMITS.get(service_name, 999999)
        remaining = max(0, limit - usage)
        percentage = (usage / limit * 100) if limit > 0 else 0
        
        return {
            "service": service_name,
            "total_requests": usage,
            "limit": limit,
            "remaining": remaining,
            "percentage": percentage,
            "exceeded": usage >= limit,
        }
    
    def should_use_fallback(self, primary_service: str) -> bool:
        """
        Determine if fallback service should be used.
        
        Args:
            primary_service: Primary service name
            
        Returns:
            True if fallback should be used
        """
        status = self.check_rate_limit(primary_service)
        return status["exceeded"]
    
    def get_usage_stats(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics for service(s).
        
        Args:
            service_name: Optional service name to filter by
            
        Returns:
            Dict with usage statistics
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        query = self.db.query(
            APIUsage.service_name,
            func.sum(APIUsage.request_count).label("total_requests"),
            func.sum(APIUsage.success_count).label("successful_requests"),
            func.sum(APIUsage.failure_count).label("failed_requests"),
        ).filter(APIUsage.date == today)
        
        if service_name:
            query = query.filter(APIUsage.service_name == service_name)
        
        query = query.group_by(APIUsage.service_name)
        
        results = []
        for row in query.all():
            limit = self.RATE_LIMITS.get(row.service_name, 999999)
            remaining = max(0, limit - row.total_requests)
            percentage = (row.total_requests / limit * 100) if limit > 0 else 0
            
            results.append({
                "service": row.service_name,
                "total_requests": row.total_requests,
                "successful_requests": row.successful_requests,
                "failed_requests": row.failed_requests,
                "remaining_quota": remaining,
                "quota_percentage": percentage,
            })
        
        return {"date": today, "services": results}
    
    def get_fallback_count(self, date: Optional[str] = None) -> int:
        """
        Get count of fallback events.
        
        Args:
            date: Optional date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Count of fallback events
        """
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Count requests to fallback service (together_ai)
        count = (
            self.db.query(func.sum(APIUsage.request_count))
            .filter(
                APIUsage.service_name == "together_ai",
                APIUsage.date == date,
            )
            .scalar()
        ) or 0
        
        return count


class LLMClient:
    """Client for calling LLM APIs with automatic fallback."""
    
    def __init__(self, db: Session):
        """Initialize LLM client."""
        self.db = db
        self.rate_limiter = APIRateLimiter(db)
    
    async def call_llm(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Call LLM with automatic fallback.
        
        Args:
            prompt: Prompt text
            model: Optional model name
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with response and metadata
        """
        import time
        
        # Check if we should use fallback
        use_fallback = self.rate_limiter.should_use_fallback("groq")
        
        if use_fallback:
            logger.info("Groq rate limit exceeded, using Together.ai fallback")
            service = "together_ai"
            # TODO: Implement Together.ai API call
            response_text = "FALLBACK: This is a mock response from Together.ai"
        else:
            service = "groq"
            # TODO: Implement Groq API call
            response_text = "This is a mock response from Groq"
        
        # Track the request
        start_time = time.time()
        duration_ms = (time.time() - start_time) * 1000
        
        self.rate_limiter.track_request(
            service_name=service,
            success=True,
            duration_ms=duration_ms,
        )
        
        return {
            "response": response_text,
            "service_used": service,
            "fallback_triggered": use_fallback,
            "duration_ms": duration_ms,
        }
