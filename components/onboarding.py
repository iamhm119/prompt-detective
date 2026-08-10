import streamlit as st
import os
from services.db import db
from services.auth_service import current_user
from datetime import datetime

"""Onboarding / contextual tooltip helpers.
Simple, lightweight system reading persistent user_settings keys.
- show_tooltips flag governs visibility (can be overridden by ENABLE_ONBOARDING_TOOLTIPS env var)
- Each tooltip can be dismissed individually and stored as dismissed_on:<key>
"""

TOOLTIP_KEYS = {
    'dashboard_upload': {
        'title': 'Upload Media',
        'body': 'Drag in an image or a short video to begin prompt reconstruction. We only keep structured summaries.'
    },
    'dashboard_params': {
        'title': 'Advanced Parameters',
        'body': 'Pro plans unlock model selection & deeper frame coverage. Upgrade anytime from Pricing.'
    },
    'usage_history': {
        'title': 'Usage History',
        'body': 'Browse recently analyzed items. Click rows to inspect prompt previews.'
    },
    'settings_tooltips': {
        'title': 'Disable Tips',
        'body': 'Uncheck "Show onboarding tooltips" in Settings to hide all guidance.'
    }
}

DISMISS_PREFIX = 'dismissed_tooltip_'  # stored as user_settings flag


def tooltips_enabled(user_id: int) -> bool:
    # Check global environment variable first
    env_setting = os.getenv("ENABLE_ONBOARDING_TOOLTIPS", "").lower()
    if env_setting in ("false", "0", "no", "off"):
        return False
    if env_setting in ("true", "1", "yes", "on"):
        return True
    
    # Fall back to user setting
    settings = db.get_user_settings(user_id)
    return settings.get('show_tooltips', 'true') == 'true'


def _dismissed(user_id: int, key: str) -> bool:
    settings = db.get_user_settings(user_id)
    return settings.get(f'{DISMISS_PREFIX}{key}', 'false') == 'true'


def dismiss(user_id: int, key: str):
    db.set_user_setting(user_id, f'{DISMISS_PREFIX}{key}', 'true')
    db.set_user_setting(user_id, f'{DISMISS_PREFIX}{key}_at', datetime.utcnow().isoformat())


def render_tooltip(key: str, icon: str = '💡'):
    user = current_user()
    if not user:
        return
    if not tooltips_enabled(user.id):
        return
    if key not in TOOLTIP_KEYS:
        return
    if _dismissed(user.id, key):
        return
    data = TOOLTIP_KEYS[key]
    with st.container():
        st.markdown(f"**{icon} {data['title']}** — {data['body']}")
        cols = st.columns([1,6])
        with cols[0]:
            if st.button('Got it', key=f'dismiss_{key}'):
                dismiss(user.id, key)
                st.rerun()
        with cols[1]:
            st.caption('You can turn these off in Settings → Show onboarding tooltips')
