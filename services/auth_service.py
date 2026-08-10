"""
Authentication and session management for Streamlit app (email + OAuth placeholders)
"""
from __future__ import annotations
import streamlit as st
import secrets
import hashlib
import hmac
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from services.db import db
from models.user import User, SubscriptionPlan, Subscription, UsageLog
from models.analysis import Session as UserSession
import os
from urllib.parse import urlencode

COOKIE_KEY = "pd_session_token"

SESSION_TTL_MIN = int(os.getenv("SESSION_TTL_MIN", "720"))  # 12h default, configurable via env

# Feature flag: allow stronger hashing if bcrypt available
try:
    import bcrypt  # type: ignore
    _HAS_BCRYPT = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_BCRYPT = False

MIN_PASSWORD_LEN = 8

def _validate_email(email: str) -> bool:
    return bool(email and '@' in email and '.' in email.split('@')[-1])

def _validate_password_strength(pw: str) -> Tuple[bool, str]:
    if len(pw) < MIN_PASSWORD_LEN:
        return False, f"Password must be at least {MIN_PASSWORD_LEN} characters"
    classes = sum([
        any(c.islower() for c in pw),
        any(c.isupper() for c in pw),
        any(c.isdigit() for c in pw),
        any(c in '!@#$%^&*()-_=+[]{};:,<.>/?' for c in pw)
    ])
    if classes < 2:
        return False, "Use a mix of character types (upper/lower/digit or symbol)"
    return True, "ok"


def _hash_password(password: str) -> str:
    """Return salted hash. Uses bcrypt if available else sha256 fallback."""
    if _HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    # fallback deterministic sha256 (not recommended for production)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def _verify_password(password: str, stored_hash: str) -> bool:
    if _HAS_BCRYPT and stored_hash.startswith('$2'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception:
            return False
    cand = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hmac.compare_digest(cand, stored_hash)


def signup(email: str, password: str, name: str = "") -> Dict[str, Any]:
    email = (email or '').strip().lower()
    if not _validate_email(email):
        return {"error": "Invalid email format"}
    ok_pw, msg_pw = _validate_password_strength(password or '')
    if not ok_pw:
        return {"error": msg_pw}
    if db.get_user_by_email(email):
        return {"error": "Email already registered"}
    user = User(
        id=None,  # will be set by DB
        email=email.lower(),
        password_hash=_hash_password(password),
        name=name or email.split("@")[0],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    user = db.save_user(user)  # capture generated id
    # Auto-create free plan subscription
    plan = db.get_plan("free") or db.create_default_plans()
    plan = db.get_plan("free")
    if not user.id:
        return {"error": "Failed to create user (no id returned)"}
    sub = Subscription(
        id=None,
        user_id=user.id,
        plan_id=plan.id if plan else None,
        status="active",
        started_at=datetime.utcnow(),
        renewal_at=datetime.utcnow() + timedelta(days=30),
    )
    try:
        db.save_subscription(sub)
    except Exception as e:
        return {"error": f"User created but subscription failed: {e}"}
    return {"ok": True}


def login(email: str, password: str) -> Dict[str, Any]:
    email = (email or '').strip().lower()
    user = db.get_user_by_email(email)
    if not user or not _verify_password(password or '', user.password_hash):
        return {"error": "Invalid credentials"}
    token = secrets.token_urlsafe(32)
    # persist session in DB
    session = UserSession(
        id=None,
        user_id=user.id,
        token=token,
        user_agent=st.session_state.get('_user_agent','') if hasattr(st, 'session_state') else '',
        ip_address=os.getenv('CLIENT_IP',''),
        expires_at=datetime.utcnow() + timedelta(minutes=SESSION_TTL_MIN),
        created_at=datetime.utcnow()
    )
    try:
        db.save_session(session)
    except Exception:
        pass
    # in-memory session
    st.session_state.auth = {
        "token": token,
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "role": getattr(user, 'role', 'free'),
        "expires_at": (datetime.utcnow() + timedelta(minutes=SESSION_TTL_MIN)).isoformat(),
    }
    # lightweight cookie set & query param storage for reload resilience
    try: st.session_state[COOKIE_KEY] = token
    except Exception: pass
    # cookie persistence (Streamlit experimental API) – align to session TTL (capped at 7 days)
    try:
        ttl_seconds = min(SESSION_TTL_MIN * 60, 60*60*24*7)
        st.experimental_set_cookie(COOKIE_KEY, token, max_age=ttl_seconds)
    except Exception:
        pass
    # Prefer new query param API, fallback to experimental
    try:
        st.query_params["session"] = token
    except Exception:
        try:
            st.experimental_set_query_params(session=token)
        except Exception:
            pass
    return {"ok": True}


def logout():
    token = st.session_state.get("auth", {}).get("token") if st.session_state.get("auth") else None
    if token:
        try:
            db.delete_session(token)
        except Exception:
            pass
    st.session_state.pop("auth", None)
    st.session_state.pop(COOKIE_KEY, None)
    # delete cookie
    try:
        st.experimental_set_cookie(COOKIE_KEY, "", max_age=0)
    except Exception:
        pass
    # Clear query param without nuking others
    try:
        # new API path
        try:
            if "session" in st.query_params:
                st.query_params.pop("session")
        except Exception:
            # fallback experimental: rebuild without session param
            try:
                qp = st.experimental_get_query_params()
                qp.pop("session", None)
                st.experimental_set_query_params(**qp)
            except Exception:
                pass
    except Exception:
        pass


def current_user() -> Optional[User]:
    data = st.session_state.get("auth")
    # Deep restoration handled by components.auth_bootstrap.ensure_session_bootstrap
    # Provide minimal fallback if bootstrap not used (session_state token only)
    if not data:
        token = st.session_state.get(COOKIE_KEY)
        if token:
            row = db.get_session(token)
            if row:
                user_id, token, user_agent, ip, expires_at, created_at = row
                try:
                    if datetime.utcnow() < datetime.fromisoformat(expires_at):
                        user = db.get_user_by_id(user_id)
                        if user:
                            st.session_state.auth = {
                                "token": token,
                                "user_id": user.id,
                                "email": user.email,
                                "name": user.name,
                                "role": getattr(user, 'role', 'free'),
                                "expires_at": expires_at,
                            }
                            data = st.session_state.auth
                except Exception:
                    pass
    if not data:
        return None
    # TTL check
    try:
        if datetime.utcnow() > datetime.fromisoformat(data["expires_at"]):
            logout();
            return None
    except Exception:
        pass
    return db.get_user_by_id(data["user_id"]) if data else None


def ensure_auth():
    if not current_user():
        st.switch_page("pages/01_🔐_Login.py")


def track_usage(user_id: int, action: str, meta: Optional[dict] = None):
    log = UsageLog(
        id=db.next_id("usage"),
        user_id=user_id,
        action=action,
        meta=meta or {},
        created_at=datetime.utcnow(),
    )
    db.save_usage(log)


def can_analyze(user: User) -> tuple[bool, str]:
    # Free plan: 5 analyses/day unless subscribed
    plan = db.get_user_active_plan(user.id)
    daily_limit = plan.daily_analyses if plan else 5
    used = db.count_user_daily_analyses(user.id)
    if used >= daily_limit:
        return False, f"Daily limit reached: {used}/{daily_limit}. Upgrade to continue."
    return True, f"{used}/{daily_limit} used today"
