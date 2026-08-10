from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.auth_service import current_user
from services.db import db
from components.onboarding import render_tooltip
import json

configure_page(); load_custom_css(); initialize_session_state()
app_header("Settings")

user = current_user()
if not user:
	st.info("Login to edit settings")
	st.page_link("pages/01_🔐_Login.py", label="Login")
	st.stop()

settings = db.get_user_settings(user.id)
theme = st.selectbox("Theme", ["light","dark"], index=["light","dark"].index(settings.get('theme','light')))
email_notif = st.checkbox("Email notifications", value=(settings.get('email_notifications','true')=='true'))
show_tooltips = st.checkbox("Show onboarding tooltips", value=(settings.get('show_tooltips','true')=='true'))
render_tooltip('settings_tooltips')

if st.button("Save Settings", type="primary"):
	db.set_user_setting(user.id, 'theme', theme)
	db.set_user_setting(user.id, 'email_notifications', 'true' if email_notif else 'false')
	db.set_user_setting(user.id, 'show_tooltips', 'true' if show_tooltips else 'false')
	st.success("Settings saved")

st.caption("Preferences are stored server-side and persist across sessions.")
