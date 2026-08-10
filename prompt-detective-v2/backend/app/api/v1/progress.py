"""
Real-time progress tracking using Server-Sent Events (SSE)
"""
import asyncio
import json
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...core.auth import get_current_active_user
from ...database import get_db
from ...models.user import User, AnalysisJob

router = APIRouter(prefix="/progress", tags=["progress"])

# Global progress tracking store (in production, use Redis)
# Format: {job_id: {"stage": "...", "progress": 0-100, "message": "..."}}
progress_store: Dict[int, Dict[str, any]] = {}


def update_job_progress(job_id: int, progress: int, stage: str, message: str = ""):
    """Update progress for a job - called from analysis.py"""
    import time
    progress_store[job_id] = {
        "progress": progress,
        "stage": stage,
        "message": message,
        "timestamp": time.time()
    }
    print(f"📊 Progress Update - Job {job_id}: {progress}% - {stage} - {message}")


def get_job_progress(job_id: int) -> Optional[Dict[str, any]]:
    """Get current progress for a job"""
    return progress_store.get(job_id)


def clear_job_progress(job_id: int):
    """Clear progress data for a job"""
    if job_id in progress_store:
        del progress_store[job_id]
        print(f"🗑️ Cleared progress data for job {job_id}")


@router.get("/{job_id}/stream")
async def stream_progress(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Stream real-time progress updates using Server-Sent Events (SSE)"""
    
    # Verify job belongs to user
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    async def event_generator():
        """Generate Server-Sent Events for progress updates"""
        last_progress = -1
        max_iterations = 300  # 5 minutes max (1s polling)
        iteration = 0
        
        try:
            while iteration < max_iterations:
                iteration += 1
                
                # Get fresh job status from database
                db.refresh(job)
                
                # Get progress from store
                progress_data = get_job_progress(job_id)
                
                if progress_data:
                    current_progress = progress_data.get("progress", job.progress)
                    stage = progress_data.get("stage", "Processing...")
                    message = progress_data.get("message", "")
                else:
                    current_progress = job.progress
                    stage = _determine_stage(job.status, current_progress)
                    message = ""
                
                # Only send update if progress changed or job completed/failed
                if current_progress != last_progress or job.status in ['completed', 'failed']:
                    data = {
                        "job_id": job_id,
                        "status": job.status,
                        "progress": current_progress,
                        "stage": stage,
                        "message": message,
                        "error_message": job.error_message if job.status == 'failed' else None
                    }
                    
                    yield f"data: {json.dumps(data)}\n\n"
                    last_progress = current_progress
                
                # Stop streaming if job completed or failed
                if job.status in ['completed', 'failed']:
                    # Send final update
                    final_data = {
                        "job_id": job_id,
                        "status": job.status,
                        "progress": 100 if job.status == 'completed' else current_progress,
                        "stage": "Complete!" if job.status == 'completed' else "Failed",
                        "message": "Analysis complete!" if job.status == 'completed' else job.error_message,
                        "error_message": job.error_message if job.status == 'failed' else None
                    }
                    yield f"data: {json.dumps(final_data)}\n\n"
                    
                    # Clear progress data
                    clear_job_progress(job_id)
                    break
                
                # Wait before next check (1 second for smooth updates)
                await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error in progress stream for job {job_id}: {str(e)}")
            error_data = {
                "job_id": job_id,
                "status": "failed",
                "progress": 0,
                "stage": "Error",
                "message": f"Stream error: {str(e)}",
                "error_message": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering for Nginx
        }
    )


def _determine_stage(status: str, progress: int) -> str:
    """Determine current stage based on status and progress"""
    if status == 'pending':
        return 'Queuing for processing...'
    elif status == 'processing':
        if progress <= 10:
            return 'File uploaded successfully'
        elif progress <= 20:
            return 'Starting content analysis...'
        elif progress <= 40:
            return 'Extracting frames and analyzing structure...'
        elif progress <= 70:
            return 'Running AI processing...'
        elif progress <= 90:
            return 'Generating AI prompts...'
        else:
            return 'Finalizing results...'
    elif status == 'completed':
        return 'Analysis complete!'
    elif status == 'failed':
        return 'Analysis failed'
    else:
        return 'Processing...'


@router.delete("/{job_id}/cancel")
async def cancel_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a processing job and refund quota"""
    
    # Get job
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Only allow canceling pending or processing jobs
    if job.status not in ['pending', 'processing']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    try:
        # Import here to avoid circular dependency
        from datetime import datetime, timezone
        from ...models.user import UsageLog
        
        # Mark job as cancelled
        job.status = 'cancelled'
        job.error_message = 'Cancelled by user'
        job.completed_at = datetime.now(timezone.utc)
        job.progress = 0
        
        # Find and delete the usage log entry for this job to refund quota
        # Query all usage logs and filter in Python (works with SQLite and PostgreSQL)
        usage_logs = db.query(UsageLog).filter(
            UsageLog.user_id == current_user.id,
            UsageLog.action == "analyze"
        ).all()
        
        usage_entry = None
        for log in usage_logs:
            if log.details and log.details.get('job_id') == job_id:
                usage_entry = log
                break
        
        if usage_entry:
            db.delete(usage_entry)
            print(f"✅ Refunded quota for user {current_user.id} - deleted usage log for job {job_id}")
        else:
            print(f"⚠️ No usage log found for job {job_id} - quota may have already been refunded")
        
        # Clear progress data
        clear_job_progress(job_id)
        
        # Commit changes
        db.commit()
        
        # Note: For background workers (Celery/RQ), you would also need to:
        # 1. Send a termination signal to the worker processing this job
        # 2. Clean up any temporary files created during processing
        # Since we're using synchronous processing, the job will naturally stop
        # when it checks the database and sees status = 'cancelled'
        
        return {
            "success": True,
            "message": "Job cancelled successfully",
            "job_id": job_id,
            "quota_refunded": usage_entry is not None
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error cancelling job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel job: {str(e)}"
        )
