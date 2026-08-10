"""Utility script to validate NeonDB connectivity and schema integrity."""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

EXPECTED_TABLES = {
    "users",
    "api_keys",
    "analysis_jobs",
    "usage_logs",
    "subscriptions",
    "payments",
    "credit_packs",
    "admin_notes",
    "otp_codes",
    "email_logs",
    "waitlist_subscribers",
    "contact_messages",
}


def load_environment() -> None:
    """Load .env file if present so the script can access DATABASE_URL."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def connectivity_check() -> int:
    """Run connectivity, schema, and CRUD smoke tests."""
    load_environment()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL is not set. Export it before running this script.")
        return 1

    from app.database import SessionLocal, engine
    from app.models.user import User

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            inspector = inspect(connection)
            existing_tables = set(inspector.get_table_names())

        missing_tables = EXPECTED_TABLES.difference(existing_tables)
        extra_tables = existing_tables.difference(EXPECTED_TABLES)

        if missing_tables:
            print(f"❌ Missing tables: {sorted(missing_tables)}")
            return 2

        print("✅ All expected tables are present")
        if extra_tables:
            print(f"ℹ️  Additional tables detected (verify if intentional): {sorted(extra_tables)}")

        with SessionLocal() as session:  # type: Session
            temp_user = User(
                email=f"neon-selftest-{uuid.uuid4().hex}@example.com",
                password_hash="integration-test",
                full_name="Neon Connectivity Test",
            )
            session.add(temp_user)
            session.flush()

            session.refresh(temp_user)
            _ = session.get(User, temp_user.id)
            temp_user.full_name = "Neon Connectivity Test (Updated)"
            session.flush()
            session.delete(temp_user)
            session.flush()
            session.rollback()

        print("✅ CRUD smoke test completed without persistence")
        pool = getattr(engine, "pool", None)
        if pool is not None:
            try:
                status = pool.status()
                print(f"ℹ️  Connection pool status: {status}")
            except Exception:  # pragma: no cover - optional diagnostics
                pass

        print("🎉 NeonDB connectivity verified successfully")
        return 0
    except SQLAlchemyError as exc:
        print(f"❌ Database check failed: {exc}")
        return 3


if __name__ == "__main__":
    sys.exit(connectivity_check())
