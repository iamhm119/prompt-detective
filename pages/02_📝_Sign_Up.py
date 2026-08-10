from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.auth_service import signup, login, current_user

configure_page(); load_custom_css(); initialize_session_state()
app_header("Sign Up")

if current_user():
    st.success("You're already logged in.")
    st.page_link("pages/05_🚀_Dashboard.py", label="Go to Dashboard", icon="🚀")
    st.stop()

st.markdown("### Create your account")
strength_msg = ""
strength_color = "gray"

def _pw_strength(pw: str):
    if not pw:
        return "", "gray"
    score = 0
    if len(pw) >= 8: score +=1
    if any(c.islower() for c in pw): score +=1
    if any(c.isupper() for c in pw): score +=1
    if any(c.isdigit() for c in pw): score +=1
    if any(c in '!@#$%^&*()-_=+[]{};:,<.>/?' for c in pw): score +=1
    labels = {0:("Too short","red"),1:("Very weak","red"),2:("Weak","orangered"),3:("Fair","orange"),4:("Good","green"),5:("Strong","green")}
    return labels.get(score, ("Weak","orangered"))

with st.form("signup_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    label, color = _pw_strength(password)
    if label:
        st.caption(f"Password strength: :{color}[{label}]")
    submitted = st.form_submit_button("Create account")

if submitted:
    if not email or not password:
        st.error("Email and password are required")
    else:
        res = signup(email, password, name)
        if "error" in res:
            st.error(res["error"])    
        else:
            st.success("Account created. Please log in.")
            st.page_link("pages/01_🔐_Login.py", label="Go to Login")
