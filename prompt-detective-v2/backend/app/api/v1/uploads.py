"""
File upload and job creation endpoints - Cloud storage version
"""
from typing import Dict
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from ...core.auth import get_current_active_user
from ...database import get_db
from ...models.user import User, AnalysisJob, UsageLog
from ...services.analysis import queue_analysis_job
from ...services.storage import save_upload_file
from ...core.config import settings

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload file and start analysis job"""
    
    # Validate file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.0f}MB"
        )
    
    # Validate file type
    allowed_types = {
        'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
        'image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    # Determine content type
    content_type = "video" if file.content_type.startswith("video/") else "image"
    
    # Check usage limits
    if not check_usage_limit(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily analysis limit exceeded. Please upgrade your plan."
        )
    
    try:
        # Save uploaded file - returns storage metadata
        storage_info = await save_upload_file(file, current_user.id)
        file_url = storage_info.get("file_url")
        analysis_reference: Dict = storage_info
        
        # Create analysis job
        job = AnalysisJob(
            user_id=current_user.id,
            filename=file.filename,
            file_path=file_url,  # Store cloud URL in database
            file_size_bytes=file.size,
            content_type=content_type,
            status="pending"
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Log usage IMMEDIATELY after job creation with timezone-aware timestamp
        from datetime import datetime, timezone
        usage_log = UsageLog(
            user_id=current_user.id,
            action="analyze",
            details={
                "job_id": job.id,
                "filename": file.filename,
                "content_type": content_type,
                "file_size": file.size
            },
            timestamp=datetime.now(timezone.utc)  # Explicitly set timezone-aware timestamp
        )
        db.add(usage_log)
        db.commit()  # Commit usage log immediately
        
        print(f"✅ Usage logged for user {current_user.id}: analyze action at {usage_log.timestamp}")
        
        # Queue background analysis AFTER usage logging
        # Pass full storage metadata for downstream handling
        queue_analysis_job(job.id, analysis_reference, content_type)
        
        return {
            "job_id": job.id,
            "status": "pending",
            "message": "File uploaded successfully. Analysis started."
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

def check_usage_limit(user: User, db: Session) -> bool:
    """Check if user has exceeded daily analysis limit using rolling 24h window"""
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import func
    
    # Get user's subscription plan
    daily_limits = {
        "free": 5,
        "pro": 50,
        "premium": 100,
        "enterprise": 1000,
        "admin": 99999
    }
    
    daily_limit = daily_limits.get(user.subscription_tier, 5)
    if user.is_premium and daily_limit < 50:
        daily_limit = 50
    
    # Rolling 24-hour window
    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    # Count usage in rolling window
    current_usage = db.query(func.count(UsageLog.id)).filter(
        UsageLog.user_id == user.id,
        UsageLog.action == "analyze",
        UsageLog.timestamp >= twenty_four_hours_ago,
        UsageLog.timestamp <= now
    ).scalar() or 0
    
    print(f"🔍 Usage Limit Check - User {user.id}:")
    print(f"  Current usage (24h): {current_usage}")
    print(f"  Daily limit: {daily_limit}")
    print(f"  Can upload: {current_usage < daily_limit}")
    
    return current_usage < daily_limit