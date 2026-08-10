"""
Minimal entrypoint that redirects to the new multi-page UI.
The legacy single-page UI has been removed from runtime per product requirements.
"""
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state


def main():
    configure_page(); load_custom_css(); initialize_session_state()
    # Redirect to Home page; if switch_page not available, present a link
    try:
        st.switch_page("pages/00_🏠_Home.py")
    except Exception:
        st.markdown("## Prompt Detective — New UI")
        st.page_link("pages/00_🏠_Home.py", label="Go to Home", icon="🏠")
        st.info("The legacy single-page UI has been removed from this build.")


if __name__ == "__main__":
    main()
