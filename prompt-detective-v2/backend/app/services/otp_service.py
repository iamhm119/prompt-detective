"""
OTP Service for email verification and password reset
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from ..models.user import User, OTPCode


def generate_otp_code() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


def create_otp(db: Session, user_id: int, otp_type: str) -> str:
    """
    Create a new OTP code for a user
    
    Args:
        db: Database session
        user_id: User ID
        otp_type: Type of OTP (email_verification or password_reset)
    
    Returns:
        The generated OTP code
    """
    print(f"📝 Creating OTP for user_id: {user_id}, type: {otp_type}")
    
    # Invalidate any existing unused OTPs of the same type for this user
    existing_otps = db.query(OTPCode).filter(
        OTPCode.user_id == user_id,
        OTPCode.otp_type == otp_type,
        OTPCode.is_used == False
    ).all()
    
    print(f"   Found {len(existing_otps)} existing OTPs to invalidate")
    for otp in existing_otps:
        otp.is_used = True
    
    # Generate new OTP
    code = generate_otp_code()
    
    # For SQLite compatibility, store as UTC but without timezone info
    # SQLite doesn't handle timezone-aware datetimes well
    current_time = datetime.now(timezone.utc)
    expires_at = current_time + timedelta(minutes=10)
    
    # Remove timezone info for SQLite storage (store as naive UTC)
    expires_at_naive = expires_at.replace(tzinfo=None)
    
    print(f"   Generated code: {code}, expires at: {expires_at_naive} (UTC)")
    
    otp = OTPCode(
        user_id=user_id,
        code=code,
        otp_type=otp_type,
        expires_at=expires_at_naive,
        is_used=False  # Explicitly set to False
    )
    
    db.add(otp)
    db.commit()
    db.refresh(otp)  # Refresh to get the actual stored values
    
    print(f"✅ OTP created with ID: {otp.id}, code: {otp.code}, is_used: {otp.is_used}")
    
    return code


def verify_otp(db: Session, user_id: int, code: str, otp_type: str) -> bool:
    """
    Verify an OTP code
    
    Args:
        db: Database session
        user_id: User ID
        code: OTP code to verify
        otp_type: Type of OTP (email_verification or password_reset)
    
    Returns:
        True if OTP is valid, False otherwise
    """
    # Clean the code (remove whitespace and convert to string)
    code = str(code).strip()
    
    print(f"🔍 Verifying OTP - User ID: {user_id}, Code: '{code}', Type: {otp_type}")
    
    # Find ALL OTPs for this user and type for debugging
    all_otps = db.query(OTPCode).filter(
        OTPCode.user_id == user_id,
        OTPCode.otp_type == otp_type
    ).all()
    
    print(f"📊 Found {len(all_otps)} total OTPs for user {user_id} and type {otp_type}:")
    for otp_record in all_otps:
        print(f"   - Code: '{otp_record.code}', Used: {otp_record.is_used}, Expires: {otp_record.expires_at}, Created: {otp_record.created_at}")
    
    # Find the OTP - check both False and 0 for is_used
    otp = db.query(OTPCode).filter(
        OTPCode.user_id == user_id,
        OTPCode.code == code,
        OTPCode.otp_type == otp_type,
        OTPCode.is_used == False
    ).first()
    
    if not otp:
        # Try with 0 instead of False (SQLite compatibility)
        otp = db.query(OTPCode).filter(
            OTPCode.user_id == user_id,
            OTPCode.code == code,
            OTPCode.otp_type == otp_type,
            OTPCode.is_used == 0
        ).first()
    
    if not otp:
        print(f"❌ OTP not found or already used. User: {user_id}, Code: '{code}', Type: {otp_type}")
        return False
    
    # Check if expired - handle both timezone-aware and timezone-naive datetimes
    current_time = datetime.now(timezone.utc)
    expires_at = otp.expires_at
    
    # Make both datetimes comparable (convert to UTC if needed)
    if expires_at.tzinfo is None:
        # SQLite stores as naive datetime, treat as UTC
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if current_time.tzinfo is None:
        # Ensure current time is also timezone-aware
        current_time = current_time.replace(tzinfo=timezone.utc)
    
    print(f"⏰ Checking expiry - Expires: {expires_at}, Current: {current_time}")
    
    if expires_at < current_time:
        print(f"❌ OTP expired. Expires at: {expires_at}, Current: {current_time}")
        return False
    
    # Mark as used
    otp.is_used = True
    db.commit()
    
    print(f"✅ OTP verified successfully. User: {user_id}, Code: '{code}', Type: {otp_type}")
    return True


def cleanup_expired_otps(db: Session) -> int:
    """
    Clean up expired OTP codes
    
    Args:
        db: Database session
    
    Returns:
        Number of OTPs deleted
    """
    current_time = datetime.now(timezone.utc)
    
    # Get all OTPs to check expiry (SQLite datetime compatibility)
    all_otps = db.query(OTPCode).all()
    
    expired_otps = []
    for otp in all_otps:
        expires_at = otp.expires_at
        # Handle timezone-naive datetimes from SQLite
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < current_time:
            expired_otps.append(otp)
    
    count = len(expired_otps)
    for otp in expired_otps:
        db.delete(otp)
    
    db.commit()
    return count
