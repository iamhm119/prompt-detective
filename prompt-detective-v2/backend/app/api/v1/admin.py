"""
Comprehensive Admin API for user management, analytics, and platform control
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timezone
from typing import List, Optional, Dict
from pydantic import BaseModel

from ...database import get_db
from ...models.user import User, AnalysisJob
from ...core.admin import get_current_admin, get_current_super_admin

router = APIRouter(prefix="/admin", tags=["admin"])

# ==================== Pydantic Models ====================

class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    premium_users: int
    total_analyses: int
    analyses_today: int
    total_api_calls: int
    subscription_breakdown: Dict[str, int]

class UserDetail(BaseModel):
    id: int
    email: str
    full_name: str
    username: str
    subscription_tier: str
    is_active: bool
    is_premium: bool
    is_email_verified: bool
    is_admin: bool
    is_super_admin: bool
    api_calls_used: int
    api_calls_limit: int
    created_at: datetime
    total_analyses: int

class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    subscription_tier: Optional[str] = None
    api_calls_limit: Optional[int] = None

# ==================== Dashboard & Analytics ====================

@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get comprehensive dashboard statistics - Requires: Admin access"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    verified_users = db.query(func.count(User.id)).filter(User.is_email_verified == True).scalar()
    premium_users = db.query(func.count(User.id)).filter(User.is_premium == True).scalar()
    total_analyses = db.query(func.count(AnalysisJob.id)).scalar()
    analyses_today = db.query(func.count(AnalysisJob.id)).filter(
        AnalysisJob.created_at >= today_start
    ).scalar()
    total_api_calls = db.query(func.sum(User.api_calls_used)).scalar() or 0
    
    subscription_breakdown = {}
    for tier in ["free", "pro", "enterprise"]:
        count = db.query(func.count(User.id)).filter(User.subscription_tier == tier).scalar()
        subscription_breakdown[tier] = count
    
    return AdminDashboardStats(
        total_users=total_users,
        active_users=active_users,
        verified_users=verified_users,
        premium_users=premium_users,
        total_analyses=total_analyses,
        analyses_today=analyses_today,
        total_api_calls=total_api_calls,
        subscription_breakdown=subscription_breakdown
    )

# ==================== User Management ====================

@router.get("/users", response_model=List[UserDetail])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get all users with filtering - Requires: Admin access"""
    query = db.query(User)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_filter)) |
            (User.full_name.ilike(search_filter)) |
            (User.username.ilike(search_filter))
        )
    
    users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        total_analyses = db.query(func.count(AnalysisJob.id)).filter(
            AnalysisJob.user_id == user.id
        ).scalar()
        
        result.append(UserDetail(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            username=user.username,
            subscription_tier=user.subscription_tier,
            is_active=user.is_active,
            is_premium=user.is_premium,
            is_email_verified=user.is_email_verified,
            is_admin=user.is_admin,
            is_super_admin=user.is_super_admin,
            api_calls_used=user.api_calls_used,
            api_calls_limit=user.api_calls_limit,
            created_at=user.created_at,
            total_analyses=total_analyses
        ))
    
    return result

@router.get("/users/{user_id}", response_model=UserDetail)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get detailed user information - Requires: Admin access"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    total_analyses = db.query(func.count(AnalysisJob.id)).filter(
        AnalysisJob.user_id == user.id
    ).scalar()
    
    return UserDetail(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        username=user.username,
        subscription_tier=user.subscription_tier,
        is_active=user.is_active,
        is_premium=user.is_premium,
        is_email_verified=user.is_email_verified,
        is_admin=user.is_admin,
        is_super_admin=user.is_super_admin,
        api_calls_used=user.api_calls_used,
        api_calls_limit=user.api_calls_limit,
        created_at=user.created_at,
        total_analyses=total_analyses
    )

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    update_data: UpdateUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_super_admin)
):
    """Update user properties - Requires: Super admin access"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    if update_data.is_premium is not None:
        user.is_premium = update_data.is_premium
    if update_data.subscription_tier:
        if update_data.subscription_tier not in ["free", "pro", "enterprise"]:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        user.subscription_tier = update_data.subscription_tier
    if update_data.api_calls_limit is not None:
        user.api_calls_limit = update_data.api_calls_limit
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"message": "User updated successfully", "user_id": user_id}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_super_admin)
):
    """Delete a user - Requires: Super admin access"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_super_admin:
        raise HTTPException(status_code=400, detail="Cannot delete super admin")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully", "user_id": user_id}

@router.post("/users/{user_id}/reset-usage")
async def reset_user_usage(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Reset user API usage - Requires: Admin access"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.api_calls_used = 0
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"message": "Usage reset successfully", "user_id": user_id}

@router.post("/users/{user_id}/toggle-premium")
async def toggle_premium(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Toggle user premium status - Requires: Admin access"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_premium = not user.is_premium
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "message": "Premium status toggled",
        "user_id": user_id,
        "is_premium": user.is_premium
    }
