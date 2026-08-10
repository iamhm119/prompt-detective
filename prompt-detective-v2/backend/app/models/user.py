"""
SQLAlchemy models for the application
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    subscription_tier = Column(String, default="free")  # free, starter, pro, business
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)
    
    # Trial management
    is_on_trial = Column(Boolean, default=False)
    trial_started_at = Column(DateTime(timezone=True))
    trial_ends_at = Column(DateTime(timezone=True))
    has_used_trial = Column(Boolean, default=False)  # Prevent multiple trials
    
    # Usage tracking
    api_calls_used = Column(Integer, default=0)
    api_calls_limit = Column(Integer, default=5)  # Daily limit based on plan
    daily_analyses_count = Column(Integer, default=0)  # Resets daily
    last_reset_date = Column(DateTime(timezone=True))
    total_analyses_count = Column(Integer, default=0)  # Lifetime count
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True))
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user")
    jobs = relationship("AnalysisJob", back_populates="user")
    usage_logs = relationship("UsageLog", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    otp_codes = relationship("OTPCode", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    credits = relationship("CreditPack", back_populates="user")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    key_hash = Column(String, unique=True, nullable=False)
    prefix = Column(String, nullable=False)  # First 8 chars for display
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer)
    content_type = Column(String, nullable=False)  # video, image
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text)
    result_data = Column(JSON)
    processing_time_seconds = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="jobs")

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # analyze, download, api_call
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(String, nullable=False)  # free, starter, pro, business
    status = Column(String, default="active")  # active, cancelled, expired, trialing
    payment_status = Column(String, default="pending")  # pending, paid, failed, refunded
    
    # Limits
    daily_limit = Column(Integer, default=5)
    monthly_limit = Column(Integer, default=150)
    api_calls_limit = Column(Integer, default=0)
    
    # Billing
    billing_cycle = Column(String)  # monthly, yearly
    price_paid = Column(Float)  # Amount paid in INR
    currency = Column(String, default="INR")
    
    # Dates
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True))
    next_billing_date = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Payment gateway
    razorpay_subscription_id = Column(String)
    razorpay_customer_id = Column(String)
    auto_renew = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    payment_type = Column(String, nullable=False)  # subscription, credit_pack, api_usage
    payment_method = Column(String)  # upi, card, netbanking, wallet
    status = Column(String, default="pending")  # pending, success, failed, refunded
    
    # Razorpay details
    razorpay_order_id = Column(String, unique=True)
    razorpay_payment_id = Column(String, unique=True)
    razorpay_signature = Column(String)
    
    # Metadata
    description = Column(Text)
    payment_metadata = Column(JSON)  # Additional payment metadata (renamed from metadata)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="payments")

class CreditPack(Base):
    __tablename__ = "credit_packs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Pack details
    pack_name = Column(String, nullable=False)  # Mini, Standard, Power
    analyses_total = Column(Integer, nullable=False)
    analyses_remaining = Column(Integer, nullable=False)
    price_paid = Column(Float, nullable=False)
    
    # Validity
    purchased_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="credits")

class AdminNote(Base):
    __tablename__ = "admin_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class OTPCode(Base):
    __tablename__ = "otp_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(6), nullable=False)  # 6-digit OTP
    otp_type = Column(String, nullable=False)  # email_verification, password_reset
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="otp_codes")

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Email details
    email_to = Column(String, nullable=False)
    email_type = Column(String, nullable=False)  # welcome, verification, subscription, trial_ending, etc.
    subject = Column(String, nullable=False)
    
    # Status
    status = Column(String, default="pending")  # pending, sent, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime(timezone=True))


class WaitlistSubscriber(Base):
    __tablename__ = "waitlist_subscribers"

    __table_args__ = (UniqueConstraint("email", "plan_name", name="uq_waitlist_email_plan"),)

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    plan_name = Column(String, nullable=True)
    source = Column(String, nullable=True)  # e.g. coming_soon_page, landing_cta
    notes = Column(Text)
    is_notified = Column(Boolean, default=False)
    notified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))