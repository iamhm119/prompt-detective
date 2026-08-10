"""
Trial Management Service
Handles 3-day trials for paid plans with automatic downgrade to Free
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from typing import List
import asyncio

from ..models.user import User, Subscription
from .email_service import (
    send_trial_started_email,
    send_trial_expiring_soon_email,
    send_trial_expired_email
)


class TrialService:
    """Manage user trials and automatic expiration"""
    
    @staticmethod
    def start_trial(db: Session, user: User, plan: str) -> Subscription:
        """
        Start a 3-day trial for a paid plan
        
        Args:
            db: Database session
            user: User object
            plan: Plan to trial (starter, pro, business)
        
        Returns:
            Subscription object
        """
        # Check if user has already used trial
        if user.has_used_trial:
            raise ValueError("Trial already used. Please purchase a subscription.")
        
        # Cancel any existing active subscriptions
        existing_subs = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        ).all()
        
        for sub in existing_subs:
            sub.status = "cancelled"
            sub.cancelled_at = datetime.now(timezone.utc)
        
        # Calculate trial period
        now = datetime.now(timezone.utc)
        trial_ends = now + timedelta(days=3)
        
        # Get plan limits
        plan_config = TrialService._get_plan_config(plan)
        
        # Create trial subscription
        subscription = Subscription(
            user_id=user.id,
            plan=plan,
            status="trialing",
            payment_status="trial",
            daily_limit=plan_config['daily_limit'],
            monthly_limit=plan_config['monthly_limit'],
            api_calls_limit=plan_config['api_calls_limit'],
            billing_cycle="trial",
            price_paid=0.0,
            currency="INR",
            started_at=now,
            expires_at=trial_ends,
            auto_renew=False
        )
        db.add(subscription)
        
        # Update user
        user.subscription_tier = plan
        user.is_premium = True
        user.api_calls_limit = plan_config['daily_limit']
        user.is_on_trial = True
        user.trial_started_at = now
        user.trial_ends_at = trial_ends
        user.has_used_trial = True  # Mark trial as used
        
        db.commit()
        db.refresh(subscription)
        
        # Send trial started email (async)
        try:
            asyncio.create_task(
                send_trial_started_email(
                    email=user.email,
                    name=user.full_name,
                    plan=plan,
                    trial_ends=trial_ends
                )
            )
        except Exception as e:
            print(f"⚠️ Failed to send trial email: {e}")
        
        return subscription
    
    @staticmethod
    async def check_and_expire_trials(db: Session) -> List[dict]:
        """
        Check all active trials and expire them if needed
        Should be run as a scheduled job (cron/background task)
        
        Returns:
            List of expired trial details
        """
        now = datetime.now(timezone.utc)
        expired_trials = []
        
        # Find users with expired trials
        users_with_expired_trials = db.query(User).filter(
            User.is_on_trial == True,
            User.trial_ends_at <= now
        ).all()
        
        for user in users_with_expired_trials:
            try:
                # Find trial subscription
                trial_sub = db.query(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.status == "trialing"
                ).first()
                
                if trial_sub:
                    # End trial subscription
                    trial_sub.status = "expired"
                    trial_sub.cancelled_at = now
                    
                    # Downgrade to Free plan
                    free_sub = Subscription(
                        user_id=user.id,
                        plan="free",
                        status="active",
                        payment_status="free",
                        daily_limit=3,
                        monthly_limit=90,
                        api_calls_limit=0,
                        billing_cycle="free",
                        price_paid=0.0,
                        currency="INR",
                        started_at=now,
                        expires_at=None,  # Free never expires
                        auto_renew=False
                    )
                    db.add(free_sub)
                    
                    # Update user
                    user.subscription_tier = "free"
                    user.is_premium = False
                    user.api_calls_limit = 3
                    user.is_on_trial = False
                    
                    db.commit()
                    
                    # Send trial expired email
                    try:
                        await send_trial_expired_email(
                            email=user.email,
                            name=user.full_name,
                            trial_plan=trial_sub.plan
                        )
                    except Exception as e:
                        print(f"⚠️ Failed to send trial expired email: {e}")
                    
                    expired_trials.append({
                        "user_id": user.id,
                        "email": user.email,
                        "trial_plan": trial_sub.plan,
                        "expired_at": now.isoformat()
                    })
            except Exception as e:
                print(f"⚠️ Failed to expire trial for user {user.id}: {e}")
                db.rollback()
        
        return expired_trials
    
    @staticmethod
    async def check_and_notify_expiring_trials(db: Session, days_before: int = 1) -> List[dict]:
        """
        Check trials expiring soon and send notifications
        Should be run as a scheduled job
        
        Args:
            db: Database session
            days_before: Notify X days before expiry (default: 1 day)
        
        Returns:
            List of notified users
        """
        now = datetime.now(timezone.utc)
        notify_threshold = now + timedelta(days=days_before)
        
        notified_users = []
        
        # Find users with trials expiring soon
        users_expiring_soon = db.query(User).filter(
            User.is_on_trial == True,
            User.trial_ends_at <= notify_threshold,
            User.trial_ends_at > now  # Not already expired
        ).all()
        
        for user in users_expiring_soon:
            try:
                trial_sub = db.query(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.status == "trialing"
                ).first()
                
                if trial_sub:
                    time_remaining = user.trial_ends_at - now
                    hours_remaining = int(time_remaining.total_seconds() / 3600)
                    
                    # Send expiring soon email
                    await send_trial_expiring_soon_email(
                        email=user.email,
                        name=user.full_name,
                        plan=trial_sub.plan,
                        hours_remaining=hours_remaining,
                        trial_ends=user.trial_ends_at
                    )
                    
                    notified_users.append({
                        "user_id": user.id,
                        "email": user.email,
                        "trial_plan": trial_sub.plan,
                        "expires_at": user.trial_ends_at.isoformat(),
                        "hours_remaining": hours_remaining
                    })
            except Exception as e:
                print(f"⚠️ Failed to notify user {user.id}: {e}")
        
        return notified_users
    
    @staticmethod
    def get_trial_status(user: User) -> dict:
        """
        Get trial status for a user
        
        Returns:
            Dict with trial info
        """
        if not user.is_on_trial:
            return {
                "is_on_trial": False,
                "has_used_trial": user.has_used_trial,
                "message": "Trial already used" if user.has_used_trial else "No active trial"
            }
        
        now = datetime.now(timezone.utc)
        time_remaining = user.trial_ends_at - now
        
        return {
            "is_on_trial": True,
            "trial_plan": user.subscription_tier,
            "trial_started": user.trial_started_at.isoformat(),
            "trial_ends": user.trial_ends_at.isoformat(),
            "hours_remaining": int(time_remaining.total_seconds() / 3600),
            "days_remaining": time_remaining.days,
            "is_expired": time_remaining.total_seconds() <= 0
        }
    
    @staticmethod
    def _get_plan_config(plan: str) -> dict:
        """Get plan configuration"""
        configs = {
            "starter": {
                "daily_limit": 15,
                "monthly_limit": 450,
                "api_calls_limit": 0
            },
            "pro": {
                "daily_limit": 50,
                "monthly_limit": 1500,
                "api_calls_limit": 5000
            },
            "business": {
                "daily_limit": 150,
                "monthly_limit": 4500,
                "api_calls_limit": 20000
            }
        }
        return configs.get(plan, configs["starter"])


# Singleton instance
trial_service = TrialService()
