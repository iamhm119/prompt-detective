import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header

configure_page(); load_custom_css(); initialize_session_state()
app_header("Legal")

st.markdown("""
### Terms & Conditions
Use responsibly. No prohibited content.

### Privacy Policy
We store minimal account data and usage counts. Uploaded files are processed transiently.
""")
