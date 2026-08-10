from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Analysis:
    id: Optional[int]
    user_id: Optional[int]
    content_type: str
    source_filename: str
    stored_path: str
    prompt_preview: str
    full_prompt_path: str
    thumbnail_path: str
    duration: float | None
    frames: int | None
    created_at: datetime

@dataclass
class Session:
    id: Optional[int]
    user_id: int
    token: str
    user_agent: str | None
    ip_address: str | None
    expires_at: datetime
    created_at: datetime
