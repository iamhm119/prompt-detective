"""Purge NeonDB data, rebuild schema, and reseed the super admin."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = PROJECT_ROOT / "migrations" / "20251031_neondb_init.sql"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_environment() -> None:
    """Load .env if present to pick up DATABASE_URL."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def drop_public_schema(engine) -> None:
    """Drop and recreate the public schema (PostgreSQL only)."""
    commands = [
        "DROP SCHEMA IF EXISTS public CASCADE",
        "CREATE SCHEMA public",
        "ALTER SCHEMA public OWNER TO CURRENT_USER",
        "GRANT ALL ON SCHEMA public TO CURRENT_USER",
        "GRANT ALL ON SCHEMA public TO PUBLIC",
    ]
    with engine.begin() as connection:
        for statement in commands:
            connection.execute(text(statement))


def apply_schema(engine) -> None:
    """Execute the canonical Neon schema script."""
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

    sql = SCHEMA_FILE.read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.exec_driver_sql(sql)


def main() -> int:
    load_environment()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is missing.")
        return 1

    cleaned_url = database_url.strip()
    if len(cleaned_url) >= 2 and cleaned_url[0] == cleaned_url[-1] and cleaned_url[0] in {'"', '\''}:
        cleaned_url = cleaned_url[1:-1].strip()

    normalized_url = cleaned_url.replace("postgres://", "postgresql://", 1)
    engine = create_engine(normalized_url)

    try:
        print("🧨 Dropping existing schema ...")
        drop_public_schema(engine)
        print("✅ Schema dropped")

        print("🏗️  Applying canonical schema ...")
        apply_schema(engine)
        print("✅ Fresh schema created")

        print("👑 Seeding super admin ...")
        from app.services.admin_seeder import ensure_super_admin

        ensure_super_admin()
        print("✅ Super admin ensured")

        print("🎉 NeonDB reset complete")
        return 0
    except (SQLAlchemyError, OSError) as exc:
        print(f"❌ Failed to reset NeonDB: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
