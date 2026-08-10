"""Centralized session restoration & auth bootstrap.
Ensures consistent persistent login across all pages.
"""
from __future__ import annotations
import streamlit as st
from datetime import datetime
from services.auth_service import current_user, COOKIE_KEY
from services.db import db

BOOTSTRAP_FLAG = "_auth_bootstrap_ran"
DEBUG_FLAG_KEY = "AUTH_DEBUG"  # set in st.secrets or st.session_state for verbose info once

RESTORE_KEYS = [
    "session_state",  # already in-memory
    "cookie",          # experimental_get_cookie
    "query_params",    # st.query_params or experimental
    "db"                # DB session lookup
]

def _debug(msg: str):
    try:
        debug_enabled = bool(st.session_state.get(DEBUG_FLAG_KEY) or st.secrets.get(DEBUG_FLAG_KEY, False))
    except Exception:
        debug_enabled = bool(st.session_state.get(DEBUG_FLAG_KEY))
    if debug_enabled:
        st.sidebar.caption(f"[auth-debug] {msg}")


def _attempt_restore_from_token(token: str, source: str) -> bool:
    if not token:
        return False
    row = db.get_session(token)
    if not row:
        return False
    user_id, token, user_agent, ip, expires_at, created_at = row
    try:
        if datetime.utcnow() > datetime.fromisoformat(expires_at):
            return False
    except Exception:
        return False
    user = db.get_user_by_id(user_id)
    if not user:
        return False
    st.session_state.auth = {
        "token": token,
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "role": getattr(user, 'role', 'free'),
        "expires_at": expires_at,
    }
    _debug(f"Restored from {source}")
    return True


def ensure_session_bootstrap():
    if st.session_state.get(BOOTSTRAP_FLAG):
        return
    # If already logged in just mark flag and return
    if st.session_state.get("auth"):
        st.session_state[BOOTSTRAP_FLAG] = True
        return

    token = None
    # 1. Cookie key in session_state (write-through)
    token = st.session_state.get(COOKIE_KEY)
    if token and _attempt_restore_from_token(token, "session_state"):
        st.session_state[BOOTSTRAP_FLAG] = True
        return

    # 2. Browser cookie
    if not token:
        try:
            token = st.experimental_get_cookie(COOKIE_KEY)
            if token and _attempt_restore_from_token(token, "cookie"):
                st.session_state[BOOTSTRAP_FLAG] = True
                return
        except Exception:
            pass

    # 3. Query params
    if not token:
        qp_token = None
        try:
            qp_token = st.query_params.get("session")
        except Exception:
            try:
                qp_token = st.experimental_get_query_params().get("session", [None])[0]
            except Exception:
                pass
        if qp_token and _attempt_restore_from_token(qp_token, "query_params"):
            st.session_state[BOOTSTRAP_FLAG] = True
            return

    # 4. (Optional) Fallback: nothing else to do – user will be anonymous
    st.session_state[BOOTSTRAP_FLAG] = True
    _debug("No session restored")

__all__ = ["ensure_session_bootstrap"]
