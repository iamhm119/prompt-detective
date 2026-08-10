"""Admin account seeding utility.
Ensures there's at least one admin user. Can be driven by env/secrets.

Environment/Secrets (optional):
- ADMIN_EMAIL
- ADMIN_PASSWORD

If not provided, a development-safe default is used and clearly documented.
"""
from __future__ import annotations
import os
from datetime import datetime
from typing import Optional

try:
    import streamlit as st  # for secrets and safe logging in sidebar if needed
except Exception:  # pragma: no cover
    st = None  # type: ignore

from services.db import db
from services.auth_service import _hash_password  # reuse same hashing path
from models.user import User


DEFAULT_ADMIN_EMAIL = "admin@promptdetective.local"
DEFAULT_ADMIN_PASSWORD = "ChangeMe!123!"  # advise rotation in prod


def _get_secret(name: str) -> Optional[str]:
    val = os.getenv(name)
    if val:
        return val
    try:
        if st is not None and hasattr(st, "secrets"):
            return st.secrets.get(name)  # type: ignore[attr-defined]
    except Exception:
        pass
    return None


def ensure_admin_from_env() -> dict:
    """Ensure at least one admin user exists.

    Priority:
    1) Use ADMIN_EMAIL/ADMIN_PASSWORD if provided via env or st.secrets.
    2) Otherwise, seed a default development admin (documented).

    Returns a summary dict with email, created(bool), password_set(bool).
    """
    email = (_get_secret("ADMIN_EMAIL") or DEFAULT_ADMIN_EMAIL).strip().lower()
    password = _get_secret("ADMIN_PASSWORD")  # None if not provided

    # Does user already exist?
    user = db.get_user_by_email(email)
    created = False
    password_set = False

    if user is None:
        # Create user
        pw_to_use = password or DEFAULT_ADMIN_PASSWORD
        user = User(
            id=None,
            email=email,
            password_hash=_hash_password(pw_to_use),
            name="Admin",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        user = db.save_user(user)
        created = True
        password_set = True

    # Ensure role is admin
    if user and getattr(user, "id", None) is not None:
        try:
            conn = db._conn(); cur = conn.cursor()  # use internal connection for a small update
            cur.execute("UPDATE users SET role=? WHERE id=?", ("admin", user.id))
            # If ADMIN_PASSWORD explicitly set, enforce it (idempotent only if provided)
            if password:
                cur.execute(
                    "UPDATE users SET password_hash=?, updated_at=? WHERE id=?",
                    (_hash_password(password), datetime.utcnow().isoformat(), user.id),
                )
                password_set = True
            conn.commit(); conn.close()
        except Exception:
            # Best effort; do not crash app initialization
            pass

    return {"email": email, "created": created, "password_set": password_set}


__all__ = ["ensure_admin_from_env", "DEFAULT_ADMIN_EMAIL", "DEFAULT_ADMIN_PASSWORD"]
