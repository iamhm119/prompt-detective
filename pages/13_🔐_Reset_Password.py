from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.db import db
from services.auth_service import _hash_password  # internal reuse acceptable here
import secrets
from datetime import datetime, timedelta

configure_page(); load_custom_css(); initialize_session_state()
app_header("Reset Password (Stub)")

st.markdown("### Password Reset")
st.caption("Prototype flow: generates a one-time token stored server-side. In production you'd email the link.")

mode = st.radio("Mode", ["Request Reset", "Set New Password"], horizontal=True)

if mode == "Request Reset":
    email = st.text_input("Account Email")
    if st.button("Send Reset Link"):
        user = db.get_user_by_email(email.lower()) if email else None
        if not user:
            st.warning("If the email exists, a reset link will be generated (we don't disclose existence).")
        else:
            token = secrets.token_urlsafe(20)
            db.set_user_setting(user.id, 'pw_reset_token', token)
            db.set_user_setting(user.id, 'pw_reset_expires', (datetime.utcnow()+timedelta(minutes=30)).isoformat())
            st.success("Reset token generated (stub). Copy this token (email integration pending):")
            st.code(token)
            st.caption("In production this would be sent via email with a secure link.")
else:
    token = st.text_input("Reset Token", help="Token from email (stub shows in previous step).")
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm Password", type="password")
    if st.button("Update Password", type="primary"):
        # Search token
        import sqlite3
        conn = sqlite3.connect('app_data.sqlite3'); cur = conn.cursor()
        row = cur.execute("SELECT user_id, value FROM user_settings WHERE key='pw_reset_token' AND value=?", (token,)).fetchone()
        if not row:
            st.error("Invalid or expired token")
        else:
            user_id = row[0]
            expires_row = cur.execute("SELECT value FROM user_settings WHERE user_id=? AND key='pw_reset_expires'", (user_id,)).fetchone()
            conn.close()
            try:
                if not expires_row or datetime.utcnow() > datetime.fromisoformat(expires_row[0]):
                    st.error("Token expired")
                elif new_pw != confirm_pw:
                    st.error("Passwords do not match")
                elif len(new_pw) < 8:
                    st.error("Password too short")
                else:
                    # Update user password
                    conn2 = sqlite3.connect('app_data.sqlite3'); c2 = conn2.cursor()
                    c2.execute("UPDATE users SET password_hash=?, updated_at=? WHERE id=?", (_hash_password(new_pw), datetime.utcnow().isoformat(), user_id))
                    # Invalidate token
                    c2.execute("DELETE FROM user_settings WHERE user_id=? AND key IN ('pw_reset_token','pw_reset_expires')", (user_id,))
                    conn2.commit(); conn2.close()
                    st.success("Password updated. You can now login.")
                    st.page_link("pages/01_🔐_Login.py", label="Go to Login")
            except Exception as e:
                st.error(f"Failed: {e}")