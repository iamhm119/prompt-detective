"""Apply the canonical NeonDB schema using SQLAlchemy."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = PROJECT_ROOT / "migrations" / "20251031_neondb_init.sql"


def load_environment() -> None:
    """Load .env if present to pick up DATABASE_URL."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def apply_schema(database_url: str) -> None:
    """Execute the Neon schema script inside a transaction."""
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

    sql = SCHEMA_FILE.read_text(encoding="utf-8")
    engine = create_engine(database_url)

    with engine.begin() as connection:
        connection.exec_driver_sql(sql)


def main() -> int:
    load_environment()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is missing.")
        return 1

    try:
        normalized_url = database_url.replace("postgres://", "postgresql://", 1)
        apply_schema(normalized_url)
        print(f"✅ Schema applied successfully using {SCHEMA_FILE.name}")
        return 0
    except (SQLAlchemyError, OSError) as exc:
        print(f"❌ Failed to apply schema: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
