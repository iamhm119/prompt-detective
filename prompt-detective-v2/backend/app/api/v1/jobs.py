"""
Job status and results endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.auth import get_current_active_user
from ...database import get_db
from ...models.user import User, AnalysisJob
from ...services.analysis import get_analysis_summary, get_downloadable_content

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/{job_id}")
async def get_job_status(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analysis job status and progress"""
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Use the analysis service to get comprehensive summary
    return get_analysis_summary(job)

@router.get("/{job_id}/results")
async def get_job_results(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analysis job results for download"""
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job not completed. Current status: {job.status}"
        )
    
    # Use the analysis service to get downloadable content
    return get_downloadable_content(job)

@router.get("")  # Handle /jobs without trailing slash
@router.get("/")  # Handle /jobs/ with trailing slash  
async def list_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List user's analysis jobs with comprehensive summaries"""
    
    query = db.query(AnalysisJob).filter(AnalysisJob.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(AnalysisJob.status == status_filter)
    
    jobs = query.order_by(AnalysisJob.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "jobs": [get_analysis_summary(job) for job in jobs],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }