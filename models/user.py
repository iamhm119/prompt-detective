from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class User:
    id: Optional[int]
    email: str
    password_hash: str
    name: str
    created_at: datetime
    updated_at: datetime
    role: str = 'free'

@dataclass
class SubscriptionPlan:
    id: Optional[int]
    code: str
    name: str
    monthly_price: float
    yearly_price: float
    daily_analyses: int

@dataclass
class Subscription:
    id: Optional[int]
    user_id: int
    plan_id: Optional[int]
    status: str
    started_at: datetime
    renewal_at: datetime

@dataclass
class UsageLog:
    id: Optional[int]
    user_id: int
    action: str
    meta: Dict[str, Any]
    created_at: datetime
