"""Debug script to check OTP codes"""
from app.database import SessionLocal
from app.models.user import User, OTPCode
from datetime import datetime, timezone

db = SessionLocal()

# Find user
user = db.query(User).filter(User.email == 'jethaniaditya7@gmail.com').first()
if user:
    print(f'User ID: {user.id}')
    print(f'Email: {user.email}')
    print(f'Email Verified: {user.is_email_verified}')
    print()
    
    # Get OTPs
    otps = db.query(OTPCode).filter(OTPCode.user_id == user.id).order_by(OTPCode.created_at.desc()).limit(5).all()
    print(f'Found {len(otps)} OTPs:')
    for otp in otps:
        print(f'  Code: {otp.code}')
        print(f'  Type: {otp.otp_type}')
        print(f'  Used: {otp.is_used}')
        print(f'  Expires: {otp.expires_at}')
        print(f'  Created: {otp.created_at}')
        print(f'  Is Expired: {otp.expires_at < datetime.now(timezone.utc)}')
        print()
else:
    print('User not found')

db.close()
