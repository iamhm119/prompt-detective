"""
Trial Management API Endpoints
3-day trials with automatic downgrade to Free plan
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...core.auth import get_current_user
from ...database import get_db
from ...models.user import User
from ...services.trial_service import trial_service


router = APIRouter(prefix="/trials", tags=["trials"])


# ==================== Request/Response Models ====================

class StartTrialRequest(BaseModel):
    """Request to start a trial"""
    plan: str  # starter, pro, business


class TrialStatusResponse(BaseModel):
    """Trial status response"""
    is_on_trial: bool
    has_used_trial: bool
    trial_plan: str | None = None
    trial_started: str | None = None
    trial_ends: str | None = None
    hours_remaining: int | None = None
    days_remaining: int | None = None
    is_expired: bool = False
    message: str | None = None


# ==================== API Endpoints ====================

@router.post("/start")
async def start_trial(
    request: StartTrialRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a 3-day trial for a paid plan
    User can only use trial once in their lifetime
    """
    # Validate plan
    valid_plans = ["starter", "pro", "business"]
    if request.plan not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {', '.join(valid_plans)}"
        )
    
    try:
        subscription = trial_service.start_trial(
            db=db,
            user=current_user,
            plan=request.plan
        )
        
        return {
            "success": True,
            "message": f"🎉 Your {request.plan.title()} trial has started! Enjoy 3 days of premium features.",
            "subscription": {
                "id": subscription.id,
                "plan": subscription.plan,
                "status": subscription.status,
                "started_at": subscription.started_at.isoformat(),
                "expires_at": subscription.expires_at.isoformat(),
                "daily_limit": subscription.daily_limit,
                "monthly_limit": subscription.monthly_limit,
                "api_calls_limit": subscription.api_calls_limit
            },
            "trial_info": {
                "duration_days": 3,
                "auto_downgrade": True,
                "downgrade_plan": "free",
                "message": "After 3 days, you'll be automatically moved to the Free plan unless you upgrade."
            }
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Start trial error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start trial: {str(e)}"
        )


@router.get("/status", response_model=TrialStatusResponse)
async def get_trial_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current trial status for user
    """
    status_data = trial_service.get_trial_status(current_user)
    return TrialStatusResponse(**status_data)


@router.get("/available-plans")
async def get_available_trial_plans(
    current_user: User = Depends(get_current_user)
):
    """
    Get available plans for trial
    """
    # Check if user has already used trial
    if current_user.has_used_trial:
        return {
            "available": False,
            "message": "Trial already used. Please purchase a subscription to enjoy premium features.",
            "plans": []
        }
    
    return {
        "available": True,
        "message": "Start your FREE 3-day trial now! No credit card required.",
        "plans": [
            {
                "name": "starter",
                "display_name": "Starter",
                "trial_duration": "3 days",
                "features": {
                    "daily_analyses": 15,
                    "monthly_analyses": 450,
                    "api_access": False,
                    "priority_support": False
                },
                "after_trial": "Auto-downgrade to Free plan (3 analyses/day)"
            },
            {
                "name": "pro",
                "display_name": "Pro",
                "trial_duration": "3 days",
                "features": {
                    "daily_analyses": 50,
                    "monthly_analyses": 1500,
                    "api_calls": 5000,
                    "api_access": True,
                    "priority_support": True
                },
                "after_trial": "Auto-downgrade to Free plan (3 analyses/day)",
                "recommended": True
            },
            {
                "name": "business",
                "display_name": "Business",
                "trial_duration": "3 days",
                "features": {
                    "daily_analyses": 150,
                    "monthly_analyses": 4500,
                    "api_calls": 20000,
                    "api_access": True,
                    "priority_support": True,
                    "custom_integrations": True
                },
                "after_trial": "Auto-downgrade to Free plan (3 analyses/day)"
            }
        ],
        "terms": {
            "one_time_only": "Trial can only be used once per account",
            "no_credit_card": "No credit card required to start trial",
            "automatic_downgrade": "After 3 days, you'll be moved to Free plan unless you upgrade",
            "full_access": "Get full access to all plan features during trial period"
        }
    }
