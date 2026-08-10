"""Unified launcher for the modern multipage UI (no legacy fallback).

Usage:
  streamlit run app_launcher.py

Behavior:
  1. Attempt to redirect user into modern multipage Home page.
  2. If an error occurs, show diagnostics and a retry button. No legacy UI is exposed.
"""
import streamlit as st
from datetime import datetime

def _try_new_ui():
    try:
        st.switch_page("pages/00_🏠_Home.py")
    except Exception as e:
        raise RuntimeError(f"Failed to switch to new UI: {e}")

def main():
    st.set_page_config(page_title="Prompt Detective Launcher", page_icon="🧪", layout="wide")
    st.markdown("# Prompt Detective Launcher")
    st.caption("Unified entry — attempting to load modern experience.")
    try:
        _try_new_ui()
    except Exception as err:
        st.warning("Modern multipage UI failed to initialize.")
        with st.expander("Diagnostics", expanded=True):
            st.code(str(err))
        if st.button("Retry New UI", type="primary"):
            st.rerun()
        st.info("No legacy interface is available in this build. Please address the diagnostics above.")
        st.page_link("pages/00_🏠_Home.py", label="Go to Home", icon="🏠")

if __name__ == "__main__":
    main()
