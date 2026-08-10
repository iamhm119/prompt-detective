"""
Lightweight database layer (SQLite via SQLAlchemy-like patterns but minimal to avoid heavy deps).
This is modular and can be swapped with real SQLAlchemy later.
"""
from __future__ import annotations
import sqlite3
from dataclasses import asdict
from typing import Optional, List
from pathlib import Path
from datetime import datetime, date
from models.user import User, SubscriptionPlan, Subscription, UsageLog
from datetime import datetime, date

# Forward references for type hints (models to be added)
try:
    from models.analysis import Analysis, Session
except Exception:
    Analysis = None  # type: ignore
    Session = None  # type: ignore

# Import config to get database URL
try:
    from config import Config
    DATABASE_URL = Config.DATABASE_URL
except ImportError:
    # Fallback if config is not available
    import os
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app_data.sqlite3")

# Extract the path from sqlite:/// URL format
if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = Path(DATABASE_URL.replace("sqlite:///", ""))
else:
    DB_PATH = Path("app_data.sqlite3")

class _DB:
    def __init__(self, path: Path):
        self.path = path
        self._init()

    def _conn(self):
        return sqlite3.connect(self.path)

    def _init(self):
        conn = self._conn()
        cur = conn.cursor()
        # Users (role column added for permissions)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            role TEXT DEFAULT 'free',
            created_at TEXT,
            updated_at TEXT
        )
        """)
        # Lightweight migration attempt if upgrading existing DB
        try:
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'free'")
        except Exception:
            pass
        # Plans
        cur.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            monthly_price REAL,
            yearly_price REAL,
            daily_analyses INTEGER
        )
        """)
        # Subscriptions
        cur.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            plan_id INTEGER,
            status TEXT,
            started_at TEXT,
            renewal_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(plan_id) REFERENCES plans(id)
        )
        """)
        # Usage logs
        cur.execute("""
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            meta TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        # Analyses table (stores summary metadata for each analysis)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            content_type TEXT,
            source_filename TEXT,
            stored_path TEXT,
            prompt_preview TEXT,
            full_prompt_path TEXT,
            thumbnail_path TEXT,
            duration REAL,
            frames INTEGER,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        # Sessions table for persistent login
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            user_agent TEXT,
            ip_address TEXT,
            expires_at TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        # User settings table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            updated_at TEXT,
            UNIQUE(user_id, key),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        conn.commit(); conn.close()
        self.create_default_plans()

    def next_id(self, table_base: str) -> int:
        # For sqlite autoincrement, we can just return None, but we keep manual for clarity
        return None  # sqlite will autoincrement

    # Plans
    def create_default_plans(self):
        if self.get_plan("free"):
            return self.get_plan("free")
        conn = self._conn(); cur = conn.cursor()
        plans = [
            (None, "free", "Free", 0.0, 0.0, 5),
            (None, "pro", "Pro", 19.0, 190.0, 100),
            (None, "team", "Team", 49.0, 490.0, 500)
        ]
        cur.executemany("INSERT OR IGNORE INTO plans VALUES (?,?,?,?,?,?)", plans)
        conn.commit(); conn.close()
        return self.get_plan("free")

    def get_plan(self, code: str) -> Optional[SubscriptionPlan]:
        conn = self._conn(); cur = conn.cursor()
        row = cur.execute("SELECT id, code, name, monthly_price, yearly_price, daily_analyses FROM plans WHERE code=?", (code,)).fetchone()
        conn.close()
        if not row:
            return None
        return SubscriptionPlan(id=row[0], code=row[1], name=row[2], monthly_price=row[3], yearly_price=row[4], daily_analyses=row[5])

    # Users
    def save_user(self, user: User) -> User:
        """Persist a new user and set its autogenerated id before returning it."""
        conn = self._conn(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, password_hash, name, created_at, updated_at) VALUES (?,?,?,?,?)",
            (user.email, user.password_hash, user.name, user.created_at.isoformat(), user.updated_at.isoformat())
        )
        user.id = cur.lastrowid
        conn.commit(); conn.close()
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        conn = self._conn(); cur = conn.cursor()
        row = cur.execute("SELECT id, email, password_hash, name, role, created_at, updated_at FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if not row:
            return None
        return User(id=row[0], email=row[1], password_hash=row[2], name=row[3], role=row[4] or 'free', created_at=datetime.fromisoformat(row[5]), updated_at=datetime.fromisoformat(row[6]))

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        conn = self._conn(); cur = conn.cursor()
        row = cur.execute("SELECT id, email, password_hash, name, role, created_at, updated_at FROM users WHERE id=?", (user_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return User(id=row[0], email=row[1], password_hash=row[2], name=row[3], role=row[4] or 'free', created_at=datetime.fromisoformat(row[5]), updated_at=datetime.fromisoformat(row[6]))

    # Analyses
    def save_analysis(self, analysis):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("""INSERT INTO analyses (user_id, content_type, source_filename, stored_path, prompt_preview, full_prompt_path, thumbnail_path, duration, frames, created_at)
                      VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (analysis.user_id, analysis.content_type, analysis.source_filename, analysis.stored_path, analysis.prompt_preview, analysis.full_prompt_path, analysis.thumbnail_path, analysis.duration, analysis.frames, analysis.created_at.isoformat()))
        analysis_id = cur.lastrowid
        conn.commit(); conn.close(); return analysis_id

    def list_analyses(self, user_id: int, limit: int = 100):
        conn = self._conn(); cur = conn.cursor()
        rows = cur.execute("SELECT id, user_id, content_type, source_filename, stored_path, prompt_preview, full_prompt_path, thumbnail_path, duration, frames, created_at FROM analyses WHERE user_id=? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
        conn.close(); return rows

    def get_analysis_by_id(self, analysis_id: int) -> Optional[object]:
        conn = self._conn(); cur = conn.cursor()
        row = cur.execute("SELECT id, user_id, content_type, source_filename, stored_path, prompt_preview, full_prompt_path, thumbnail_path, duration, frames, created_at FROM analyses WHERE id=?", (analysis_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return Analysis(
            id=row[0], user_id=row[1], content_type=row[2], source_filename=row[3], stored_path=row[4],
            prompt_preview=row[5], full_prompt_path=row[6], thumbnail_path=row[7], duration=row[8],
            frames=row[9], created_at=datetime.fromisoformat(row[10])
        )

    def update_analysis_prompt_preview(self, analysis_id: int, new_preview: str, full_prompt_path: str = "") -> None:
        conn = self._conn(); cur = conn.cursor()
        cur.execute("UPDATE analyses SET prompt_preview=?, full_prompt_path=? WHERE id=?", (new_preview, full_prompt_path, analysis_id))
        conn.commit(); conn.close()

    # Sessions
    def save_session(self, session):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("INSERT INTO sessions (user_id, token, user_agent, ip_address, expires_at, created_at) VALUES (?,?,?,?,?,?)",
                    (session.user_id, session.token, session.user_agent, session.ip_address, session.expires_at.isoformat(), session.created_at.isoformat()))
        conn.commit(); conn.close()

    def get_session(self, token: str):
        conn = self._conn(); cur = conn.cursor()
        row = cur.execute("SELECT user_id, token, user_agent, ip_address, expires_at, created_at FROM sessions WHERE token=?", (token,)).fetchone()
        conn.close(); return row

    def delete_session(self, token: str):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("DELETE FROM sessions WHERE token=?", (token,)); conn.commit(); conn.close()

    # User settings
    def set_user_setting(self, user_id: int, key: str, value: str):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("INSERT INTO user_settings (user_id, key, value, updated_at) VALUES (?,?,?,?) ON CONFLICT(user_id,key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                    (user_id, key, value, datetime.utcnow().isoformat()))
        conn.commit(); conn.close()

    def get_user_settings(self, user_id: int) -> dict:
        conn = self._conn(); cur = conn.cursor()
        rows = cur.execute("SELECT key, value FROM user_settings WHERE user_id=?", (user_id,)).fetchall(); conn.close()
        return {k: v for k, v in rows}

    # Subscriptions
    def save_subscription(self, sub: Subscription):
        if sub.user_id is None:
            raise ValueError("Subscription user_id cannot be None. Persist user first to obtain an id.")
        conn = self._conn(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO subscriptions (user_id, plan_id, status, started_at, renewal_at) VALUES (?,?,?,?,?)",
            (sub.user_id, sub.plan_id, sub.status, sub.started_at.isoformat(), sub.renewal_at.isoformat())
        )
        conn.commit(); conn.close()

    def get_user_active_plan(self, user_id: int) -> Optional[SubscriptionPlan]:
        conn = self._conn(); cur = conn.cursor()
        row = cur.execute("""
            SELECT p.id, p.code, p.name, p.monthly_price, p.yearly_price, p.daily_analyses
            FROM subscriptions s
            JOIN plans p ON p.id = s.plan_id
            WHERE s.user_id=? AND s.status='active'
            ORDER BY s.started_at DESC
            LIMIT 1
        """, (user_id,)).fetchone()
        conn.close()
        if not row:
            return self.get_plan("free")
        return SubscriptionPlan(id=row[0], code=row[1], name=row[2], monthly_price=row[3], yearly_price=row[4], daily_analyses=row[5])

    # Usage
    def save_usage(self, usage: UsageLog):
        conn = self._conn(); cur = conn.cursor()
        meta_json = json_dumps_safe(usage.meta)
        cur.execute("INSERT INTO usage_logs (user_id, action, meta, created_at) VALUES (?,?,?,?)",
                    (usage.user_id, usage.action, meta_json, usage.created_at.isoformat()))
        conn.commit(); conn.close()

    def count_user_daily_analyses(self, user_id: int) -> int:
        conn = self._conn(); cur = conn.cursor()
        day_start = datetime.utcnow().date().isoformat()
        row = cur.execute("SELECT COUNT(*) FROM usage_logs WHERE user_id=? AND action='analyze' AND substr(created_at,1,10)=?", (user_id, day_start)).fetchone()
        conn.close()
        return row[0] if row else 0


def json_dumps_safe(obj) -> str:
    try:
        import json
        return json.dumps(obj)
    except Exception:
        return "{}"


db = _DB(DB_PATH)
