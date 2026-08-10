from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from services.auth_service import current_user
from services.db import db
from datetime import datetime

configure_page(); load_custom_css(); initialize_session_state()
app_header("Admin Console")

user = current_user()
if not user or getattr(user, 'role', 'free') != 'admin':
    st.error("Admin access required")
    st.stop()

st.markdown("### Users")
import sqlite3
conn = sqlite3.connect('app_data.sqlite3'); cur = conn.cursor()
rows = cur.execute("SELECT id, email, name, role, created_at FROM users ORDER BY created_at DESC").fetchall(); conn.close()

if not rows:
    st.info("No users yet")
else:
    for r in rows:
        uid, email, name, role, created_at = r
        col1, col2, col3, col4, col5 = st.columns([3,2,2,2,2])
        with col1: st.write(email)
        with col2: st.write(name)
        with col3: st.write(role or 'free')
        with col4:
            new_role = st.selectbox("Role", ["free","pro","team","admin"], index=["free","pro","team","admin"].index(role or 'free'), key=f"role_{uid}")
        with col5:
            if st.button("Update", key=f"upd_{uid}"):
                try:
                    conn2 = sqlite3.connect('app_data.sqlite3'); c2 = conn2.cursor()
                    c2.execute("UPDATE users SET role=? WHERE id=?", (new_role, uid))
                    conn2.commit(); conn2.close()
                    st.success("Updated")
                except Exception as e:
                    st.error(f"Failed: {e}")
        st.divider()

st.markdown("### System Stats & Analytics")
import pandas as pd
conn = sqlite3.connect('app_data.sqlite3'); cur = conn.cursor()
u_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
a_count = cur.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
today = datetime.utcnow().date().isoformat()
today_usage = cur.execute("SELECT COUNT(*) FROM usage_logs WHERE substr(created_at,1,10)=?", (today,)).fetchone()[0]

# Role counts
role_rows = cur.execute("SELECT role, COUNT(*) FROM users GROUP BY role").fetchall()
role_counts = {r if r else 'free': c for r,c in role_rows}

# Usage leaderboard (top 5 by today's analyze actions)
leader_rows = cur.execute("""
    SELECT u.email, COUNT(l.id) as cnt
    FROM usage_logs l JOIN users u ON u.id=l.user_id
    WHERE l.action='analyze' AND substr(l.created_at,1,10)=?
    GROUP BY u.email ORDER BY cnt DESC LIMIT 5
""", (today,)).fetchall()

# 7-day usage trend
trend_rows = cur.execute("""
    SELECT substr(created_at,1,10) d, COUNT(*)
    FROM usage_logs WHERE action='analyze'
    GROUP BY d ORDER BY d DESC LIMIT 7
""").fetchall()
conn.close()

colA, colB, colC = st.columns(3)
with colA: st.metric("Total Users", u_count)
with colB: st.metric("Total Analyses", a_count)
with colC: st.metric("Analyses Today", today_usage)

st.markdown("#### Role Distribution")
if role_counts:
    rd_df = pd.DataFrame([(k or 'free', v) for k,v in role_counts.items()], columns=["Role","Count"])
    st.bar_chart(rd_df.set_index("Role"))
else:
    st.caption("No role data yet")

st.markdown("#### Top Users Today")
if leader_rows:
    lead_df = pd.DataFrame(leader_rows, columns=["User","Analyses Today"])  
    st.table(lead_df)
else:
    st.caption("No usage yet today")

st.markdown("#### 7-Day Analysis Trend")
if trend_rows:
    tr_df = pd.DataFrame(trend_rows, columns=["Date","Analyses"]).sort_values("Date")
    st.line_chart(tr_df.set_index("Date"))
else:
    st.caption("No recent usage")