"""Waitlist subscription endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.user import WaitlistSubscriber
from ...services.email_service import send_waitlist_confirmation_email

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


class WaitlistRequest(BaseModel):
    email: EmailStr
    plan_name: str | None = None
    source: str | None = None
    notes: str | None = None


class WaitlistResponse(BaseModel):
    message: str
    already_joined: bool = False


@router.post("/subscribe", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_waitlist(payload: WaitlistRequest, db: Session = Depends(get_db)) -> WaitlistResponse:
    """Create or update a waitlist subscription entry."""
    normalized_plan = payload.plan_name.strip() if payload.plan_name else None
    normalized_source = payload.source.strip() if payload.source else None
    normalized_email = payload.email.lower()

    existing = (
        db.query(WaitlistSubscriber)
        .filter(
            WaitlistSubscriber.email == normalized_email,
            WaitlistSubscriber.plan_name.is_(normalized_plan) if normalized_plan is None else WaitlistSubscriber.plan_name == normalized_plan,
        )
        .one_or_none()
    )

    timestamp = datetime.now(timezone.utc)

    try:
        if existing:
            existing.source = normalized_source or existing.source
            existing.notes = payload.notes or existing.notes
            existing.updated_at = timestamp
            db.add(existing)
            already_joined = True
        else:
            waitlist_entry = WaitlistSubscriber(
                email=normalized_email,
                plan_name=normalized_plan,
                source=normalized_source,
                notes=payload.notes,
                created_at=timestamp,
                updated_at=timestamp,
            )
            db.add(waitlist_entry)
            already_joined = False

        db.commit()
    except IntegrityError as exc:  # pragma: no cover - defensive double submit handling
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already on the waitlist for this plan.") from exc

    # Send confirmation email (best-effort)
    try:
        await send_waitlist_confirmation_email(
            contact_email=payload.email,
            plan_name=normalized_plan,
            source=normalized_source,
            already_joined=already_joined,
        )
    except Exception as exc:  # pragma: no cover - email failure should not break API
        print(f"⚠️ Waitlist email send failed: {exc}")

    message = "You're already on the waitlist—thanks for staying tuned!" if already_joined else "Welcome to the waitlist! We'll notify you soon."
    return WaitlistResponse(message=message, already_joined=already_joined)
