"""Account lifecycle endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.auth import get_current_active_user
from ...database import get_db
from ...models.user import (
    User,
    APIKey,
    AnalysisJob,
    UsageLog,
    Subscription,
    Payment,
    CreditPack,
    OTPCode,
    EmailLog,
)
from ...models.contact_message import ContactMessage
from ...services.email_service import send_account_deletion_confirmation_email

router = APIRouter(prefix="/account", tags=["account"])


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """Permanently delete the authenticated user's account and related data."""
    user_id = current_user.id
    user_email = current_user.email
    user_name = current_user.full_name

    try:
        for model in (AnalysisJob, UsageLog, APIKey, Subscription, Payment, CreditPack, OTPCode, EmailLog):
            db.query(model).filter(model.user_id == user_id).delete(synchronize_session=False)

        db.query(ContactMessage).filter(ContactMessage.email == user_email).delete(synchronize_session=False)

        db.delete(current_user)
        db.commit()
    except Exception as exc:  # pragma: no cover - defensive rollback
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete account") from exc

    try:
        await send_account_deletion_confirmation_email(email=user_email, name=user_name)
    except Exception as exc:  # pragma: no cover - email failure should not block deletion
        print(f"⚠️ Account deletion email send failed: {exc}")
