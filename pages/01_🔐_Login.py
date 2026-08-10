from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.auth_service import login, current_user
import time

configure_page(); load_custom_css(); initialize_session_state()
app_header("Login")

user = current_user()
if user:
    st.success("Session restored")
    # direct redirect
    st.switch_page("pages/05_🚀_Dashboard.py")

st.markdown("### Welcome back")
st.caption("Access your dashboard and start analyzing content.")
with st.form("login_form"):
    email = st.text_input("Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login", type="primary")

if submitted:
    if not email or not password:
        st.error("Email and password required")
    else:
        res = login(email, password)
        if "error" in res:
            st.error(res["error"])
        else:
            st.success("Redirecting to dashboard…")
            time.sleep(0.4)
            st.switch_page("pages/05_🚀_Dashboard.py")
            
st.info("New here? Create an account.")
st.page_link("pages/02_📝_Sign_Up.py", label="Create account")
st.caption("Forgot your password? Use the reset flow below.")
st.page_link("pages/13_🔐_Reset_Password.py", label="Reset password")
