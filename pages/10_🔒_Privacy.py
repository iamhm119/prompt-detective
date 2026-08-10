from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from datetime import datetime

configure_page(); load_custom_css(); initialize_session_state()
app_header("Privacy Policy")

st.markdown(f"""
### 1. Data Philosophy
We practice minimal data retention: raw media is processed in-memory / ephemeral storage only for the duration of analysis. We store structured prompt summaries, usage counts, and account metadata.

### 2. Data Collected
| Category | Examples | Purpose |
|----------|----------|---------|
| Account | Email, password hash, plan role | Authentication & plan enforcement |
| Usage Metrics | Analysis count, timestamps | Quota tracking & product improvement |
| Analysis Summaries | Prompt preview, content type | History UI & productivity features |
| Sessions | Session token (hashed), expiry | Persistent secure login |
| Settings | Theme, tooltip flags | Personalization |

### 3. What We Do NOT Store
We do not persist your original uploaded media files or full raw prompt expansions beyond session context. We do not sell or rent user data.

### 4. Security Measures
 - Hashed credentials (strong hashing recommended in production)
 - Plan to incorporate optional 2FA / OAuth
 - Least-privilege database schema
 - Encrypted transport (HTTPS) assumed at deployment

### 5. Cookies / Sessions
Session tokens are stored server-side and referenced via a transient client value. Revoking a session in future UI invalidates all devices.

### 6. Third-Party Processors
If payment is enabled, billing is handled via PCI-compliant providers (e.g., Stripe). We never receive full card numbers.

### 7. Retention & Deletion
Account and settings data are retained until deletion request. We will provide a data export & deletion workflow in future releases.

### 8. Children
Service not directed to children under 13. Accounts discovered to be underage may be removed.

### 9. Changes
Material changes will be indicated with a new "Last Updated" date below.

---
**Last Updated:** {datetime.utcnow().date().isoformat()}
""")

st.caption("Replace with counsel-reviewed policy before production launch.")
