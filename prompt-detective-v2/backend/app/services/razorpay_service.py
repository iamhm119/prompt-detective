"""
Razorpay Payment Integration Service
Supports UPI, Cards, NetBanking, Wallets - All Indian payment methods
"""
import razorpay
import hmac
import hashlib
from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from ..core.config import settings
from ..models.user import User, Payment, Subscription, CreditPack
from .email_service import send_payment_success_email, send_subscription_confirmation_email


class RazorpayService:
    """Razorpay payment gateway integration"""
    
    def __init__(self):
        # Initialize Razorpay client
        self.client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))
    
    def create_order(
        self,
        amount: float,
        currency: str = "INR",
        receipt_id: Optional[str] = None,
        notes: Optional[Dict] = None
    ) -> Dict:
        """
        Create a Razorpay order
        
        Args:
            amount: Amount in INR (will be converted to paise)
            currency: Currency code (default INR)
            receipt_id: Unique receipt ID
            notes: Additional notes
        
        Returns:
            Order details from Razorpay
        """
        # Convert amount to paise (smallest currency unit)
        amount_paise = int(amount * 100)
        
        order_data = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt_id or f"rcpt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "notes": notes or {}
        }
        
        order = self.client.order.create(data=order_data)
        return order
    
    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature for security
        
        Args:
            razorpay_order_id: Order ID from Razorpay
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature to verify
        
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Generate expected signature
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            expected_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, razorpay_signature)
        except Exception as e:
            print(f"❌ Signature verification error: {e}")
            return False
    
    async def process_subscription_payment(
        self,
        db: Session,
        user: User,
        plan: str,
        billing_cycle: str,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> Subscription:
        """
        Process subscription payment and activate subscription
        
        Args:
            db: Database session
            user: User object
            plan: Subscription plan (starter, pro, business)
            billing_cycle: monthly or yearly
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Payment signature
        
        Returns:
            Subscription object
        """
        # Verify payment signature
        if not self.verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            raise ValueError("Invalid payment signature")
        
        # Get payment details from Razorpay
        payment_details = self.client.payment.fetch(razorpay_payment_id)
        amount_paid = payment_details['amount'] / 100  # Convert paise to INR
        payment_method = payment_details.get('method', 'unknown')
        
        # Create payment record
        payment = Payment(
            user_id=user.id,
            amount=amount_paid,
            currency="INR",
            payment_type="subscription",
            payment_method=payment_method,
            status="success",
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            description=f"{plan} subscription - {billing_cycle}",
            completed_at=datetime.now(timezone.utc)
        )
        db.add(payment)
        
        # Cancel existing active subscriptions
        existing_subs = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        ).all()
        
        for sub in existing_subs:
            sub.status = "cancelled"
            sub.cancelled_at = datetime.now(timezone.utc)
        
        # Calculate subscription period
        now = datetime.now(timezone.utc)
        if billing_cycle == "monthly":
            expires_at = now + timedelta(days=30)
            next_billing = now + timedelta(days=30)
        else:  # yearly
            expires_at = now + timedelta(days=365)
            next_billing = now + timedelta(days=365)
        
        # Get plan limits
        plan_config = self._get_plan_config(plan)
        
        # Create new subscription
        subscription = Subscription(
            user_id=user.id,
            plan=plan,
            status="active",
            payment_status="paid",
            daily_limit=plan_config['daily_limit'],
            monthly_limit=plan_config['monthly_limit'],
            api_calls_limit=plan_config['api_calls_limit'],
            billing_cycle=billing_cycle,
            price_paid=amount_paid,
            currency="INR",
            started_at=now,
            expires_at=expires_at,
            next_billing_date=next_billing,
            auto_renew=True
        )
        db.add(subscription)
        
        # Update user
        user.subscription_tier = plan
        user.is_premium = True
        user.api_calls_limit = plan_config['daily_limit']
        user.is_on_trial = False  # End trial if active
        
        db.commit()
        db.refresh(subscription)
        
        # Send confirmation email
        try:
            await send_subscription_confirmation_email(
                email=user.email,
                name=user.full_name,
                plan=plan,
                amount=amount_paid,
                billing_cycle=billing_cycle,
                next_billing_date=next_billing
            )
        except Exception as e:
            print(f"⚠️ Failed to send subscription email: {e}")
        
        return subscription
    
    async def process_credit_pack_payment(
        self,
        db: Session,
        user: User,
        pack_name: str,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> CreditPack:
        """
        Process credit pack purchase
        
        Args:
            db: Database session
            user: User object
            pack_name: Credit pack name (Mini, Standard, Power)
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Payment signature
        
        Returns:
            CreditPack object
        """
        # Verify payment signature
        if not self.verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            raise ValueError("Invalid payment signature")
        
        # Get payment details
        payment_details = self.client.payment.fetch(razorpay_payment_id)
        amount_paid = payment_details['amount'] / 100
        payment_method = payment_details.get('method', 'unknown')
        
        # Get pack configuration
        pack_config = self._get_credit_pack_config(pack_name)
        
        # Create payment record
        payment = Payment(
            user_id=user.id,
            amount=amount_paid,
            currency="INR",
            payment_type="credit_pack",
            payment_method=payment_method,
            status="success",
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            description=f"{pack_name} credit pack",
            completed_at=datetime.now(timezone.utc)
        )
        db.add(payment)
        
        # Create credit pack
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=pack_config['validity_days'])
        
        credit_pack = CreditPack(
            user_id=user.id,
            pack_name=pack_name,
            analyses_total=pack_config['analyses'],
            analyses_remaining=pack_config['analyses'],
            price_paid=amount_paid,
            purchased_at=now,
            expires_at=expires_at,
            is_active=True
        )
        db.add(credit_pack)
        
        db.commit()
        db.refresh(credit_pack)
        
        # Send confirmation email
        try:
            await send_payment_success_email(
                email=user.email,
                name=user.full_name,
                amount=amount_paid,
                description=f"{pack_name} Credit Pack - {pack_config['analyses']} analyses",
                valid_until=expires_at
            )
        except Exception as e:
            print(f"⚠️ Failed to send payment email: {e}")
        
        return credit_pack
    
    def _get_plan_config(self, plan: str) -> Dict:
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
    
    def _get_credit_pack_config(self, pack_name: str) -> Dict:
        """Get credit pack configuration"""
        configs = {
            "Mini": {"analyses": 20, "validity_days": 15, "price": 99},
            "Standard": {"analyses": 60, "validity_days": 30, "price": 249},
            "Power": {"analyses": 150, "validity_days": 60, "price": 499}
        }
        return configs.get(pack_name, configs["Mini"])


# Singleton instance
razorpay_service = RazorpayService()
