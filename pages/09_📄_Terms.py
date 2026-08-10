from components.auth_bootstrap import ensure_session_bootstrap
ensure_session_bootstrap()
import streamlit as st
from streamlit_config import configure_page, load_custom_css, initialize_session_state
from components.navigation import app_header
from datetime import datetime

configure_page(); load_custom_css(); initialize_session_state()
app_header("Terms of Service")

st.markdown("""
### 1. Overview
These Terms of Service ("Terms") govern your use of the Prompt Detective application (the "Service"). By creating an account or using the Service you agree to these Terms.

### 2. Accounts & Access
You are responsible for safeguarding your credentials. You must be 18+ or have legal guardian consent. We may suspend accounts for abuse, security risk, or excessive automated scraping.

### 3. Acceptable Use
You agree not to: (a) attempt to decompile or reverse engineer proprietary code; (b) upload unlawful or infringing content; (c) misrepresent analysis output as ground-truth forensic certification; (d) exceed plan limits via automation.

### 4. Generated Output
Prompt reconstructions are probabilistic. You are solely responsible for how you use or distribute generated prompts. We disclaim all warranties regarding accuracy or fitness for a particular purpose.

### 5. Privacy & Data
We minimize retention: raw media is processed transiently; only structured summaries & usage metrics are stored. See the Privacy Policy for full details.

### 6. Plans, Billing & Upgrades
Free tier provides limited daily analyses. Paid plans may auto-renew unless cancelled. Where payment processing is enabled, third‑party processors handle card data; refunds are discretionary in cases of misuse.

### 7. Service Changes
We may add, modify, or remove features with notice where practical. Material changes to limits or pricing will be communicated in advance.

### 8. Intellectual Property
All software, design elements, and branding remain our property. You retain rights to your own uploaded media and legal rights to prompts you create or export.

### 9. Termination
You may stop using the Service at any time. We may terminate or restrict access for violations of these Terms or legal requirements.

### 10. Disclaimer & Limitation of Liability
Service provided "AS IS" without warranties. To the fullest extent permitted, our aggregate liability for any claim is limited to fees paid (if any) in the 3 months preceding the claim.

### 11. Export & Compliance
You agree to comply with applicable export, sanctions, and local laws when using the Service.

### 12. Updates to Terms
We may update these Terms; continued use after effective date constitutes acceptance. A revision notice will appear here with last updated date.

---
**Last Updated:** {datetime.utcnow().date().isoformat()}
""" )

st.caption("These placeholders are not legal advice. Replace with counsel-reviewed language for production.")
