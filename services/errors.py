"""User-friendly error handling utilities with decorator and context manager."""
from contextlib import contextmanager
import streamlit as st
import traceback
import functools

@contextmanager
def friendly_errors(context: str = ""):
    try:
        yield
    except Exception:
        st.error(f"Something went wrong. {context}")
        with st.expander("Details"):
            st.code(traceback.format_exc())

def error_boundary(message: str = "Unexpected error"):
    """Decorator to wrap functions with a UI error boundary."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception:
                st.error(message)
                with st.expander("Traceback"):
                    st.code(traceback.format_exc())
                return None
        return wrapper
    return decorator
