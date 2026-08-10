"""
Admin authentication and authorization utilities
"""
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User
from .auth import get_current_user

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify that current user is an admin
    Raises 403 if user is not an admin
    """
    if not current_user.is_admin and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_current_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify that current user is a super admin
    Raises 403 if user is not a super admin
    """
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user

def check_unlimited_access(user: User) -> bool:
    """
    Check if user has unlimited access (admin or special limit)
    Returns True if user has unlimited access
    """
    return (
        user.is_admin or 
        user.is_super_admin or 
        user.api_calls_limit == -1
    )

def check_feature_access(user: User, feature: str) -> bool:
    """
    Check if user has access to a specific feature
    
    Features:
    - 'basic': Free tier features
    - 'premium': Pro tier features
    - 'enterprise': Enterprise tier features
    - 'admin': Admin-only features
    """
    # Super admin has access to everything
    if user.is_super_admin:
        return True
    
    # Admin has access to admin features
    if feature == "admin" and user.is_admin:
        return True
    
    # Premium users have access to premium and basic
    if user.is_premium and feature in ["basic", "premium"]:
        return True
    
    # Enterprise tier has access to all non-admin features
    if user.subscription_tier == "enterprise" and feature != "admin":
        return True
    
    # Pro tier has access to premium and basic
    if user.subscription_tier == "pro" and feature in ["basic", "premium"]:
        return True
    
    # Free tier only has basic access
    if user.subscription_tier == "free" and feature == "basic":
        return True
    
    return False

def can_bypass_rate_limit(user: User) -> bool:
    """
    Check if user can bypass rate limiting
    Admins and users with unlimited calls can bypass
    """
    return (
        user.is_admin or 
        user.is_super_admin or 
        user.api_calls_limit == -1
    )
