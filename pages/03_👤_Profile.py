from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.auth_service import current_user
from services.db import db

configure_page(); load_custom_css(); initialize_session_state()
app_header("Profile")

user = current_user()
if not user:
    st.info("Please login first.")
    st.page_link("pages/01_🔐_Login.py", label="Login")
    st.stop()

st.text_input("Name", value=user.name, disabled=True)
st.text_input("Email", value=user.email, disabled=True)

plan = db.get_user_active_plan(user.id)
st.metric("Plan", plan.name if plan else "Free")

st.markdown("---")
st.subheader("Usage today")
used = db.count_user_daily_analyses(user.id)
st.progress(min(1.0, used / (plan.daily_analyses if plan else 5)))
st.caption(f"{used}/{plan.daily_analyses if plan else 5} analyses used today")
