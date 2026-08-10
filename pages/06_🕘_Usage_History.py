from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from components.onboarding import render_tooltip
from services.auth_service import current_user
from services.db import db
from reverse_engineer import ReverseEngineerSystem
import os
from datetime import datetime
import pandas as pd

configure_page(); load_custom_css(); initialize_session_state()
app_header("Usage & History")

user = current_user()
if not user:
    st.info("Login to view analysis history")
    st.page_link("pages/01_🔐_Login.py", label="Login")
    st.stop()

st.markdown("### Your Analyses")
render_tooltip('usage_history')
used = db.count_user_daily_analyses(user.id)
st.caption(f"Analyses today: {used}")

col_search, col_type, col_limit = st.columns([3,1,1])
with col_search:
    q = st.text_input("Search", placeholder="filename or prompt text…")
with col_type:
    type_filter = st.selectbox("Type", ["All","image","video"], index=0)
with col_limit:
    limit = st.number_input("Limit", min_value=10, max_value=500, value=100, step=10)

rows = db.list_analyses(user.id, limit=limit)
records = []
for r in rows:
    (aid, uid, content_type, source_filename, stored_path, prompt_preview, full_prompt_path, thumbnail_path, duration, frames, created_at) = r
    records.append({
        "ID": aid,
        "Type": content_type,
        "File": source_filename,
        "Stored Path": stored_path,
        "Thumbnail": thumbnail_path,
        "Preview": (prompt_preview or '')[:120],
        "Duration(s)": duration if content_type=='video' else None,
        "Frames": frames if content_type=='video' else None,
        "Created": created_at
    })

df = pd.DataFrame(records)
if type_filter != "All":
    df = df[df.Type.str.lower()==type_filter.lower()]
if q:
    ql = q.lower()
    df = df[df.apply(lambda row: ql in str(row.File).lower() or ql in str(row.Preview).lower(), axis=1)]

st.dataframe(df.drop(columns=["Stored Path","Thumbnail"]) if not df.empty else df, use_container_width=True, height=500)
st.caption(f"Showing {len(df)} record(s). Newest first.")

if not df.empty:
    with st.expander("Record details & actions"):
        selected_id = st.number_input("Analysis ID", min_value=int(df.ID.min()), max_value=int(df.ID.max()), value=int(df.ID.iloc[0]))
        sel = df[df.ID==selected_id]
        if not sel.empty:
            row = sel.iloc[0]
            st.markdown(f"**File:** {row.File}  |  **Type:** {row.Type}  |  **Created:** {row.Created}")
            # Thumbnail
            if row.Thumbnail and os.path.exists(row.Thumbnail):
                st.image(row.Thumbnail, width=200)
            # View/Download full prompt if exists
            if row.get('Stored Path') and isinstance(row.get('Stored Path'), str):
                st.caption(f"Original file path: {row['Stored Path']}")
            # Edit prompt preview
            new_preview = st.text_area("Edit Prompt Preview", value=row.Preview, height=150)
            colA, colB, colC = st.columns(3)
            with colA:
                if st.button("Save Preview"):
                    try:
                        db.update_analysis_prompt_preview(int(row.ID), new_preview)
                        st.success("Saved preview")
                    except Exception as e:
                        st.error(f"Failed to save: {e}")
            with colB:
                if st.button("Regenerate from File"):
                    source_path = row.get('Stored Path')
                    if source_path and os.path.exists(source_path):
                        sys = ReverseEngineerSystem()
                        with st.spinner("Regenerating analysis..."):
                            res = sys.analyze_content(source_path, save_frames=True)
                        if 'error' in res:
                            st.error(res['error'])
                        else:
                            st.success("Regeneration complete")
                            # Robust prompt extraction after regeneration
                            def _extract_prompt(r: dict) -> str:
                                ctype = (r.get('content_type') or '').lower()
                                if ctype == 'video':
                                    return r.get('comprehensive_video_prompt') or r.get('video_prompt') or ''
                                p = r.get('suggested_prompt')
                                if p:
                                    return p
                                ind = r.get('individual_analyses') or []
                                for a in ind:
                                    if a.get('analysis_type') == 'prompt_analysis' and a.get('raw_analysis'):
                                        return a['raw_analysis']
                                return r.get('comprehensive_analysis') or ''

                            prompt = _extract_prompt(res)
                            st.text_area("New Prompt", prompt, height=200)
                    else:
                        st.warning("Original file not available on disk.")
            with colC:
                if st.button("Open Prompt File"):
                    st.info("If a full prompt file path is stored, opening is supported by your OS. (Manual step)")
