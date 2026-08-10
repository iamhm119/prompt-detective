"""
Reusable navigation and header components
"""
import streamlit as st
from services.auth_service import current_user, logout


def app_header(title: str = "Prompt Detective"):
    cols = st.columns([6,1,1,1])
    with cols[0]:
        st.markdown(f"### {title}")
    user = current_user()
    if user:
        with cols[1]:
            st.page_link("pages/03_👤_Profile.py", label="Profile")
        with cols[2]:
            st.page_link("pages/04_💳_Pricing.py", label="Pricing")
        with cols[3]:
            if st.button("Logout"):
                logout(); st.rerun()
    else:
        with cols[2]:
            st.page_link("pages/01_🔐_Login.py", label="Login")
        with cols[3]:
            st.page_link("pages/02_📝_Sign_Up.py", label="Sign up")
