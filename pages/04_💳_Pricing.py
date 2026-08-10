from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.db import db

configure_page(); load_custom_css(); initialize_session_state()
app_header("Pricing")

st.markdown("""
### Simple, transparent pricing

- Free — 5 analyses/day
- Pro — 100 analyses/day ($19/mo)
- Team — 500 analyses/day ($49/mo)

Stripe integration can be connected via environment variables.
""")

col1, col2, col3 = st.columns(3)
for col, code in zip([col1, col2, col3], ["free", "pro", "team"]):
    with col:
        p = db.get_plan(code)
        st.write(f"#### {p.name}")
        st.write(f"Daily analyses: {p.daily_analyses}")
        st.write(f"Monthly: ${p.monthly_price:.0f}")
        st.write(f"Yearly: ${p.yearly_price:.0f}")
        st.button("Choose", key=f"choose_{code}")
