from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.auth_service import current_user
from services.db import db
from datetime import datetime

configure_page(); load_custom_css(); initialize_session_state()

# ---------- HERO HEADER ----------
app_header("Prompt Detective — Reverse Engineer AI Content")

user = current_user()

hero_left, hero_right = st.columns([7,5])
with hero_left:
    st.markdown("""
    <div style='padding-top:0.5rem'>
    <h1 style='font-size:2.75rem;line-height:1.1;margin-bottom:0.6rem'>Understand <span style='color:#ff4b4b'>exactly</span> how AI visuals were made</h1>
    <p style='font-size:1.15rem;margin-bottom:1.1rem'>Prompt Detective performs multi-pass forensic analysis of images & videos to reconstruct clean, structured prompts you can reuse instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    cta_cols = st.columns([1,1,1.4])
    with cta_cols[0]:
        if user:
            st.page_link("pages/05_🚀_Dashboard.py", label="🚀 Start Analyzing")
        else:
            st.page_link("pages/02_📝_Sign_Up.py", label="📝 Get Started")
    with cta_cols[1]:
        st.page_link("pages/04_💳_Pricing.py", label="💳 Pricing")
    with cta_cols[2]:
        st.page_link("pages/08_❓_Help_and_FAQ.py", label="❓ How it Works")

with hero_right:
    st.image("samples/sample_image.jpg", caption="Sample analysis prompt output", use_container_width=True)

st.markdown(":sparkles: <b>Private by design</b> • We only persist structured prompt summaries, never your raw files.", unsafe_allow_html=True)

st.markdown("""<hr style='margin:1.7rem 0 1.2rem'/>""", unsafe_allow_html=True)

# ---------- LIVE METRICS (lightweight counts) ----------
def _quick_count(sql: str) -> int:
    try:
        import sqlite3
        conn = sqlite3.connect(str(db.path)); cur = conn.cursor()
        val = cur.execute(sql).fetchone()[0]; conn.close(); return val or 0
    except Exception:
        return 0

total_users = _quick_count("SELECT COUNT(*) FROM users")
total_analyses = _quick_count("SELECT COUNT(*) FROM analyses")
today = datetime.utcnow().date().isoformat()
today_analyses = _quick_count(f"SELECT COUNT(*) FROM usage_logs WHERE action='analyze' AND substr(created_at,1,10)='{today}'")

metric_cols = st.columns(3)
metric_cols[0].metric("Users", f"{total_users}")
metric_cols[1].metric("Analyses Saved", f"{total_analyses}")
metric_cols[2].metric("Analyses Today", f"{today_analyses}")

st.markdown("""
<style>
.feature-card {background: var(--background-color,#11111120); padding:0.9rem 1rem 0.95rem; border:1px solid #4443; border-radius:10px; height:100%;}
.feature-card h4 {margin-top:0;margin-bottom:0.45rem;font-size:1.05rem;}
.workflow-step {background:#262730; padding:0.75rem 0.9rem; border-radius:8px; border:1px solid #333;}
@media (max-width: 840px){ .feature-card{font-size:0.92rem;} }
</style>
""", unsafe_allow_html=True)

# ---------- FEATURE GRID ----------
st.subheader("Core Capabilities")
fg1, fg2, fg3 = st.columns(3)
with fg1:
    st.markdown("""<div class='feature-card'>
    <h4>🔍 Forensic Prompt Reconstruction</h4>
    Multi-pass reasoning isolates stylistic, compositional & aesthetic tokens.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class='feature-card'>
    <h4>🧠 Multi-Model Insight</h4>
    Combines classical CV signals with LLM semantic enrichment.
    </div>""", unsafe_allow_html=True)
with fg2:
    st.markdown("""<div class='feature-card'>
    <h4>🎞️ Smart Frame Selection</h4>
    Rapidly extracts the most information-rich frames from video uploads.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class='feature-card'>
    <h4>🧱 Structured Output</h4>
    Receives clean sections (subject, style, lighting, camera, post-process, negative) ready to copy.
    </div>""", unsafe_allow_html=True)
with fg3:
    st.markdown("""<div class='feature-card'>
    <h4>🔐 Privacy First</h4>
    Raw media never leaves the session context; only summaries stored.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class='feature-card'>
    <h4>📊 Usage & Plan Controls</h4>
    Built-in daily quotas, plan gating & admin oversight.
    </div>""", unsafe_allow_html=True)

st.markdown("""<hr style='margin:1.8rem 0 1.2rem'/>""", unsafe_allow_html=True)

# ---------- WORKFLOW OVERVIEW ----------
st.subheader("How It Works")
wf1, wf2, wf3, wf4 = st.columns(4)
wf1.markdown("""<div class='workflow-step'><b>1. Upload</b><br/>Image or video media.</div>""", unsafe_allow_html=True)
wf2.markdown("""<div class='workflow-step'><b>2. Analyze</b><br/>Multi-pass semantic + visual extraction.</div>""", unsafe_allow_html=True)
wf3.markdown("""<div class='workflow-step'><b>3. Reconstruct</b><br/>Cluster & rank prompt tokens.</div>""", unsafe_allow_html=True)
wf4.markdown("""<div class='workflow-step'><b>4. Export</b><br/>Copy, refine, iterate.</div>""", unsafe_allow_html=True)

st.markdown("""
> You stay focused on creativity—Prompt Detective handles the forensic decoding.
""")

# ---------- PRICING TEASER ----------
st.markdown("""<hr style='margin:2.0rem 0 1.3rem'/>""", unsafe_allow_html=True)
pricing_col, feature_col = st.columns([5,7])
with pricing_col:
    st.markdown("""
    ### Simple Plans
    Free to try with generous daily limits. Upgrade when you need scale.
    """)
    st.page_link("pages/04_💳_Pricing.py", label="View full pricing →")
with feature_col:
    st.markdown("""
    **Free** – 5 daily analyses • **Pro** – 100 • **Team** – 500
    <br/><span style='font-size:0.85rem;color:#888'>Stripe checkout integration ready via environment configuration.</span>
    """, unsafe_allow_html=True)

# ---------- FINAL CTA ----------
st.markdown("""<hr style='margin:2.0rem 0 1.4rem'/>""", unsafe_allow_html=True)
cta2 = st.columns([2,2,5])
with cta2[0]:
    if user:
        st.page_link("pages/05_🚀_Dashboard.py", label="🚀 Open Dashboard")
    else:
        st.page_link("pages/02_📝_Sign_Up.py", label="📝 Create Free Account")
with cta2[1]:
    st.page_link("pages/08_❓_Help_and_FAQ.py", label="❓ FAQ")

st.caption("© {} Prompt Detective. All rights reserved.".format(datetime.utcnow().year))

