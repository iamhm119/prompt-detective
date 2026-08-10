from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from components.onboarding import render_tooltip
from services.auth_service import current_user

configure_page(); load_custom_css(); initialize_session_state()
app_header("Help & FAQ")

st.markdown("""
### Quick Answers
**How many free analyses?** 5 per day on the Free plan.\
**Do you store my files?** Only structured prompt summaries, not the raw media.\
**Are prompts accurate?** They are best-effort reconstructions—treat as creative starting points.\
**How do I upgrade?** Visit the Pricing page; billing keys enable checkout.\
**Video support?** Yes: we select representative frames and aggregate patterns.
""")

with st.expander("Troubleshooting Tips"):
	st.markdown("""
	- Upload failing? Ensure file extension is preserved and supported (jpg/png/mp4/webm).
	- Hitting quota? Check Usage History or upgrade your plan.
	- Empty prompt? Some low-information frames may reduce extraction quality—try a clearer image.
	- Session lost? Re-login; persistent sessions are restored if still valid.
	""")

with st.expander("Feature Roadmap (High-Level)"):
	st.markdown("""
	- OAuth login options\n- Shareable analysis exports\n- Team workspace roles\n- Full prompt file download linking\n- Batch automation API
	""")

st.markdown("---")
st.subheader("Contact Support")
st.caption("We aim for fast, human responses.")
col_form, col_info = st.columns([3,2])
with col_form:
	user = current_user()
	default_email = getattr(user, 'email', '') if user else ''
	email = st.text_input("Your Email", value=default_email, placeholder="you@example.com")
	topic = st.selectbox("Topic", ["General","Billing","Bug Report","Feedback"]) 
	message = st.text_area("Message", height=160, placeholder="Describe your question or issue…")
	if st.button("Send Message", type="primary"):
		if not email or not message.strip():
			st.warning("Email and message required")
		else:
			# Placeholder for future email / ticket integration
			st.success("Message queued (placeholder). We'll reply soon.")
with col_info:
	st.markdown("""
	**Response Time**: < 24h (business)
	**Status Page**: Coming soon
	**Support Email**: support@example.com
	""")

render_tooltip('usage_history')
