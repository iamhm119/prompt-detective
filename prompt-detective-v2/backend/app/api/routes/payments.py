"""
Razorpay Payment API Endpoints
Handles subscription purchases, credit packs, and payment verification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ...core.auth import get_current_user
from ...database import get_db
from ...models.user import User, Payment, Subscription, CreditPack
from ...services.razorpay_service import razorpay_service


router = APIRouter(prefix="/payments", tags=["payments"])


# ==================== Request/Response Models ====================

class CreateOrderRequest(BaseModel):
    """Request to create Razorpay order"""
    order_type: str  # "subscription" or "credit_pack"
    plan: Optional[str] = None  # For subscriptions: starter, pro, business
    billing_cycle: Optional[str] = None  # monthly or yearly
    pack_name: Optional[str] = None  # For credit packs: Mini, Standard, Power


class VerifyPaymentRequest(BaseModel):
    """Verify Razorpay payment"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    order_type: str  # "subscription" or "credit_pack"
    plan: Optional[str] = None
    billing_cycle: Optional[str] = None
    pack_name: Optional[str] = None


class OrderResponse(BaseModel):
    """Response with Razorpay order details"""
    order_id: str
    amount: int  # in paise
    currency: str
    key_id: str  # Razorpay key for frontend


class PaymentHistoryResponse(BaseModel):
    """Payment history item"""
    id: int
    amount: float
    currency: str
    payment_type: str
    payment_method: str
    status: str
    description: str
    created_at: str
    completed_at: Optional[str]


# ==================== Helper Functions ====================

def get_plan_pricing(plan: str, billing_cycle: str) -> float:
    """Get pricing for subscription plan"""
    pricing = {
        "starter": {"monthly": 299, "yearly": 2990},
        "pro": {"monthly": 699, "yearly": 6990},
        "business": {"monthly": 1299, "yearly": 12990}
    }
    return pricing.get(plan, {}).get(billing_cycle, 0)


def get_credit_pack_pricing(pack_name: str) -> float:
    """Get pricing for credit pack"""
    pricing = {
        "Mini": 99,
        "Standard": 249,
        "Power": 499
    }
    return pricing.get(pack_name, 0)


# ==================== API Endpoints ====================

@router.post("/create-order", response_model=OrderResponse)
async def create_payment_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Razorpay order for subscription or credit pack purchase
    """
    try:
        # Determine amount based on order type
        if request.order_type == "subscription":
            if not request.plan or not request.billing_cycle:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Plan and billing cycle required for subscription"
                )
            
            amount = get_plan_pricing(
                request.plan,
                request.billing_cycle
            )
            
            notes = {
                "user_id": current_user.id,
                "user_email": current_user.email,
                "order_type": "subscription",
                "plan": request.plan,
                "billing_cycle": request.billing_cycle
            }
            
            receipt_id = f"sub_{current_user.id}_{request.plan}_{request.billing_cycle}"
        
        elif request.order_type == "credit_pack":
            if not request.pack_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Pack name required for credit pack"
                )
            
            amount = get_credit_pack_pricing(request.pack_name)
            
            notes = {
                "user_id": current_user.id,
                "user_email": current_user.email,
                "order_type": "credit_pack",
                "pack_name": request.pack_name
            }
            
            receipt_id = f"pack_{current_user.id}_{request.pack_name}"
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid order type"
            )
        
        # Create Razorpay order
        order = razorpay_service.create_order(
            amount=amount,
            currency="INR",
            receipt_id=receipt_id,
            notes=notes
        )
        
        # Return order details
        from ...core.config import settings
        return OrderResponse(
            order_id=order['id'],
            amount=order['amount'],
            currency=order['currency'],
            key_id=settings.RAZORPAY_KEY_ID
        )
    
    except Exception as e:
        print(f"❌ Create order error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.post("/verify-payment")
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify Razorpay payment and activate subscription or credit pack
    """
    try:
        if request.order_type == "subscription":
            if not request.plan or not request.billing_cycle:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Plan and billing cycle required"
                )
            
            subscription = await razorpay_service.process_subscription_payment(
                db=db,
                user=current_user,
                plan=request.plan,
                billing_cycle=request.billing_cycle,
                razorpay_order_id=request.razorpay_order_id,
                razorpay_payment_id=request.razorpay_payment_id,
                razorpay_signature=request.razorpay_signature
            )
            
            return {
                "success": True,
                "message": "Subscription activated successfully! 🎉",
                "subscription": {
                    "id": subscription.id,
                    "plan": subscription.plan,
                    "status": subscription.status,
                    "expires_at": subscription.expires_at.isoformat(),
                    "daily_limit": subscription.daily_limit,
                    "monthly_limit": subscription.monthly_limit
                }
            }
        
        elif request.order_type == "credit_pack":
            if not request.pack_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Pack name required"
                )
            
            credit_pack = await razorpay_service.process_credit_pack_payment(
                db=db,
                user=current_user,
                pack_name=request.pack_name,
                razorpay_order_id=request.razorpay_order_id,
                razorpay_payment_id=request.razorpay_payment_id,
                razorpay_signature=request.razorpay_signature
            )
            
            return {
                "success": True,
                "message": "Credit pack purchased successfully! 🎉",
                "credit_pack": {
                    "id": credit_pack.id,
                    "pack_name": credit_pack.pack_name,
                    "analyses_remaining": credit_pack.analyses_remaining,
                    "expires_at": credit_pack.expires_at.isoformat()
                }
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid order type"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Payment verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment verification failed: {str(e)}"
        )


@router.get("/history")
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment history for current user
    """
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).limit(50).all()
    
    return {
        "payments": [
            PaymentHistoryResponse(
                id=p.id,
                amount=p.amount,
                currency=p.currency,
                payment_type=p.payment_type,
                payment_method=p.payment_method,
                status=p.status,
                description=p.description,
                created_at=p.created_at.isoformat(),
                completed_at=p.completed_at.isoformat() if p.completed_at else None
            ) for p in payments
        ]
    }


@router.get("/pricing")
async def get_pricing_info():
    """
    Get all pricing information for plans and credit packs
    """
    return {
        "subscriptions": {
            "starter": {
                "name": "Starter",
                "monthly": {
                    "regular": 199,
                    "launch": 99
                },
                "yearly": {
                    "regular": 1999,
                    "launch": 999
                },
                "features": {
                    "daily_analyses": 15,
                    "monthly_analyses": 450,
                    "api_access": False,
                    "priority_support": False
                }
            },
            "pro": {
                "name": "Pro",
                "monthly": {
                    "regular": 499,
                    "launch": 299
                },
                "yearly": {
                    "regular": 4999,
                    "launch": 2999
                },
                "features": {
                    "daily_analyses": 50,
                    "monthly_analyses": 1500,
                    "api_calls": 5000,
                    "api_access": True,
                    "priority_support": True
                }
            },
            "business": {
                "name": "Business",
                "monthly": {
                    "regular": 1499,
                    "launch": 999
                },
                "yearly": {
                    "regular": 14999,
                    "launch": 9999
                },
                "features": {
                    "daily_analyses": 150,
                    "monthly_analyses": 4500,
                    "api_calls": 20000,
                    "api_access": True,
                    "priority_support": True,
                    "custom_integrations": True
                }
            }
        },
        "credit_packs": {
            "Mini": {
                "price": 99,
                "analyses": 20,
                "validity_days": 15,
                "best_for": "Occasional users"
            },
            "Standard": {
                "price": 249,
                "analyses": 60,
                "validity_days": 30,
                "best_for": "Regular users"
            },
            "Power": {
                "price": 499,
                "analyses": 150,
                "validity_days": 60,
                "best_for": "Heavy users"
            }
        },
        "currency": "INR",
        "launch_offer": {
            "active": True,
            "message": "🚀 Launch Offer: Lock your price forever!",
            "discount": "50% OFF - Pay launch price, keep it for lifetime"
        }
    }
