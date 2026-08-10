"""
Usage tracking and limits endpoints
"""
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ...core.auth import get_current_active_user
from ...database import get_db
from ...models.user import User, UsageLog, Subscription

router = APIRouter(prefix="/usage", tags=["usage"])

@router.get("/daily")
async def get_daily_usage(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's daily usage statistics"""
    
    # Get user's daily limit from user properties (no subscription table dependency)
    daily_limit = 5  # Default free tier limit
    
    # Use existing user fields to determine limits
    if current_user.is_premium:
        daily_limit = 50
    elif current_user.subscription_tier == "pro":
        daily_limit = 50
    elif current_user.subscription_tier == "premium":
        daily_limit = 100
    elif current_user.subscription_tier == "enterprise":
        daily_limit = 500
    else:
        # Free tier
        daily_limit = 5
    
    # Calculate rolling 24-hour window with timezone awareness
    now = datetime.now(timezone.utc)
    rolling_window_start = now - timedelta(hours=24)
    
    try:
        # Get usage count in the rolling window using efficient query
        daily_usage = db.query(func.count(UsageLog.id)).filter(
            and_(
                UsageLog.user_id == current_user.id,
                UsageLog.action == "analyze",
                UsageLog.timestamp >= rolling_window_start,
                UsageLog.timestamp <= now
            )
        ).scalar() or 0
        
        print(f"🔍 Usage Debug - User {current_user.id}:")
        print(f"  Rolling window: {rolling_window_start} to {now}")
        print(f"  Usage count: {daily_usage}")
        
        # Get recent usage logs for debugging
        recent_logs = db.query(UsageLog).filter(
            and_(
                UsageLog.user_id == current_user.id,
                UsageLog.action == "analyze"
            )
        ).order_by(UsageLog.timestamp.desc()).limit(5).all()
        
        print(f"  Recent usage entries:")
        for log in recent_logs:
            print(f"    {log.timestamp} - {log.action}")
        
        # Format usage history for response (defensive against nulls)
        usage_history = []
        for log in recent_logs[:3]:  # Include last 3 for UI
            usage_history.append({
                "timestamp": log.timestamp.isoformat() if getattr(log, "timestamp", None) else None,
                "job_id": str((log.details or {}).get("job_id", "")),
                "content_type": (log.details or {}).get("content_type", "unknown"),
            })
            
    except Exception as e:
        # Handle database errors gracefully
        print(f"Warning: Could not fetch usage logs: {e}")
        daily_usage = 0
        usage_history = []
    
    return {
        "daily_usage": daily_usage,
        "daily_limit": daily_limit,
        "usage_percentage": round((daily_usage / daily_limit) * 100) if daily_limit > 0 else 0,
        "can_upload": daily_usage < daily_limit,
        "remaining_uploads": max(0, daily_limit - daily_usage),
        "rolling_window_hours": 24,
        "window_start": rolling_window_start.isoformat(),
        "current_time": now.isoformat(),
        "user_tier": current_user.subscription_tier or "free",
        "is_premium": current_user.is_premium or False,
        "usage_history": usage_history
    }

@router.get("/stats")
async def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive usage statistics for the user"""
    
    try:
        # Get all usage logs for the user
        all_usage = db.query(func.count(UsageLog.id)).filter(
            and_(
                UsageLog.user_id == current_user.id,
                UsageLog.action == "analyze"
            )
        ).scalar() or 0
        
        # Get this month's usage
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_usage = db.query(func.count(UsageLog.id)).filter(
            and_(
                UsageLog.user_id == current_user.id,
                UsageLog.action == "analyze",
                UsageLog.timestamp >= month_start
            )
        ).scalar() or 0
        
        # Get this week's usage
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        weekly_usage = db.query(func.count(UsageLog.id)).filter(
            and_(
                UsageLog.user_id == current_user.id,
                UsageLog.action == "analyze",
                UsageLog.timestamp >= week_start
            )
        ).scalar() or 0
        
    except Exception as e:
        # Handle database errors gracefully
        print(f"Warning: Could not fetch usage stats: {e}")
        all_usage = 0
        monthly_usage = 0
        weekly_usage = 0
    
    return {
        "total_usage": all_usage,
        "monthly_usage": monthly_usage,
        "weekly_usage": weekly_usage,
        "user_tier": current_user.subscription_tier or "free",
        "is_premium": current_user.is_premium or False,
        "member_since": current_user.created_at.isoformat() if current_user.created_at else None
    }
