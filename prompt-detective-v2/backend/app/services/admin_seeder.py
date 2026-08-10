"""Utility helpers for ensuring an admin/super-admin account exists."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from ..core.auth import get_password_hash, verify_password
from ..core.config import settings
from ..database import SessionLocal
from ..models.user import User


def _determine_password() -> Tuple[str, bool]:
    """Resolve the password to use for the admin account.

    Returns a tuple of (password, is_generated) where is_generated indicates whether
    we had to fall back to the default password because no ADMIN_PASSWORD was supplied.
    """
    candidate = (settings.ADMIN_PASSWORD or "").strip()
    if candidate:
        return candidate, False
    # Fall back to default password defined in settings and flag so we can log a warning
    return settings.DEFAULT_ADMIN_PASSWORD, True


def ensure_super_admin(session: Optional[Session] = None) -> None:
    """Create or update the primary admin/super-admin user.

    The function can be called without providing a session; in that case it will manage
    its own database session lifecycle. Existing accounts are elevated to admin/super
    admin status and their password is rotated if ADMIN_PASSWORD is provided.
    """
    external_session = session is not None
    db = session or SessionLocal()

    admin_email = (settings.ADMIN_EMAIL or "").strip().lower()
    if not admin_email:
        print("⚠️  ADMIN_EMAIL not configured; skipping admin bootstrap")
        if not external_session:
            db.close()
        return

    password, used_default = _determine_password()
    now = datetime.now(timezone.utc)

    try:
        user = db.query(User).filter(User.email == admin_email).first()
        created = False
        updated_fields = []

        if user is None:
            hashed_password = get_password_hash(password)
            username = admin_email.split("@")[0]
            user = User(
                email=admin_email,
                password_hash=hashed_password,
                full_name="Super Admin",
                username=username,
                subscription_tier="enterprise",
                is_active=True,
                is_premium=True,
                is_email_verified=True,
                is_admin=True,
                is_super_admin=True,
                api_calls_used=0,
                api_calls_limit=-1,
                created_at=now,
                updated_at=now,
            )
            db.add(user)
            created = True
        else:
            if not user.is_admin:
                user.is_admin = True
                updated_fields.append("is_admin")
            if not user.is_super_admin:
                user.is_super_admin = True
                updated_fields.append("is_super_admin")
            if user.api_calls_limit != -1:
                user.api_calls_limit = -1
                updated_fields.append("api_calls_limit")
            if not user.is_active:
                user.is_active = True
                updated_fields.append("is_active")
            if not user.is_premium:
                user.is_premium = True
                updated_fields.append("is_premium")
            if not user.is_email_verified:
                user.is_email_verified = True
                updated_fields.append("is_email_verified")

            if settings.ADMIN_PASSWORD or used_default:
                if not verify_password(password, user.password_hash):
                    user.password_hash = get_password_hash(password)
                    updated_fields.append("password")

            user.updated_at = now

        db.commit()

        if created:
            db.refresh(user)
            print(f"✅ Seeded super admin account: {admin_email}")
            if used_default:
                print(
                    "⚠️  DEFAULT_ADMIN_PASSWORD is in use. Override ADMIN_PASSWORD in the environment to rotate it."
                )
        else:
            if updated_fields:
                print(
                    f"✅ Super admin {admin_email} synchronized (updated: {', '.join(updated_fields)})"
                )
                if used_default:
                    print(
                        "⚠️  ADMIN_PASSWORD not provided; existing password left unchanged."
                    )
            else:
                print(f"ℹ️  Super admin {admin_email} already configured")

    except Exception as exc:  # pragma: no cover - defensive logging
        db.rollback()
        print(f"⚠️  Failed to ensure super admin user: {exc}")
    finally:
        if not external_session:
            db.close()


__all__ = ["ensure_super_admin"]
