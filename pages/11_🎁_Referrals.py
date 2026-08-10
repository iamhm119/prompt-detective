from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.auth_service import current_user

configure_page(); load_custom_css(); initialize_session_state()
app_header("Referrals")

user = current_user()
if not user:
    st.info("Please login first.")
    st.page_link("pages/01_🔐_Login.py", label="Login")
    st.stop()

st.write("Share your referral link:")
st.code(f"https://example.com/?ref={user.id}")
