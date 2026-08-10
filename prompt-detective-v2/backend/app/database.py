"""Database configuration and session management."""
from __future__ import annotations

import time
from typing import Any, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from .core.config import settings


def _normalize_database_url(raw_url: str) -> str:
    """Ensure compatibility with SQLAlchemy and Neon connection strings."""
    if not raw_url:
        raise ValueError("DATABASE_URL is required")

    cleaned = raw_url.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', '\''}:
        cleaned = cleaned[1:-1].strip()

    if cleaned.startswith("postgres://"):
        cleaned = cleaned.replace("postgres://", "postgresql://", 1)

    try:
        url = make_url(cleaned)
    except Exception as exc:  # pragma: no cover - defensive logging
        raise ValueError("DATABASE_URL is not a valid SQLAlchemy URL") from exc
    drivername = url.drivername
    if drivername == "postgres":
        url = url.set(drivername="postgresql")

    # Enforce sslmode for Neon unless explicitly provided
    if url.get_backend_name() != "sqlite":
        query = dict(url.query)
        query.setdefault("sslmode", settings.DB_SSL_MODE)
        url = url.set(query=query)

    return url.render_as_string(hide_password=False)


def _create_engine_once(db_url: str) -> Engine:
    """Instantiate the SQLAlchemy engine with pooling tuned for Neon."""
    url: URL = make_url(db_url)
    engine_kwargs: dict[str, Any] = {"echo": settings.DB_ECHO}
    connect_args: dict[str, Any] = {}

    if url.get_backend_name() == "sqlite":
        connect_args["check_same_thread"] = False
        engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)
        return engine

    host = url.host or ""
    connect_args.update(
        {
            "sslmode": settings.DB_SSL_MODE,
            "connect_timeout": settings.DB_POOL_TIMEOUT,
        }
    )

    if settings.DB_STATEMENT_TIMEOUT_MS and "pooler" not in host:
        connect_args["options"] = f"-c statement_timeout={settings.DB_STATEMENT_TIMEOUT_MS}"

    engine_kwargs["pool_pre_ping"] = settings.DB_PRE_PING
    engine_kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE

    if settings.DB_POOL_ENABLED:
        engine_kwargs.update(
            {
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
            }
        )
    else:
        engine_kwargs["poolclass"] = NullPool

    engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)

    # Fail fast if the connection cannot be established and apply per-session tuning
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        if settings.DB_STATEMENT_TIMEOUT_MS and "pooler" in host:
            connection.execute(text(f"SET statement_timeout = {int(settings.DB_STATEMENT_TIMEOUT_MS)}"))

    return engine


def _create_engine_with_retry() -> Engine:
    """Create engine with exponential backoff retries."""
    db_url = _normalize_database_url(settings.DATABASE_URL)

    attempts = max(1, settings.DB_CONNECT_RETRIES)
    delay = max(0.1, settings.DB_RETRY_INITIAL_DELAY)
    backoff = max(1.0, settings.DB_RETRY_BACKOFF_FACTOR)

    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            engine = _create_engine_once(db_url)
            print("✅ Database engine initialized")
            return engine
        except (OperationalError, SQLAlchemyError) as exc:  # pragma: no cover - defensive logging
            last_error = exc
            wait_seconds = delay * (backoff ** (attempt - 1))
            print(f"⚠️  Database connection failed (attempt {attempt}/{attempts}): {exc}")
            if attempt == attempts:
                break
            time.sleep(wait_seconds)

    raise RuntimeError("Unable to establish database connection") from last_error


# Create database engine with retry strategy suitable for serverless environments
engine = _create_engine_with_retry()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session with retry-aware acquisition."""
    attempt = 0
    session: Session | None = None
    while True:
        try:
            session = SessionLocal()
            yield session
            break
        except (OperationalError, SQLAlchemyError) as exc:
            attempt += 1
            if attempt > settings.DB_CONNECT_RETRIES:
                raise
            backoff_seconds = settings.DB_RETRY_INITIAL_DELAY * (settings.DB_RETRY_BACKOFF_FACTOR ** (attempt - 1))
            print(f"⚠️  Retrying database session acquisition (attempt {attempt}): {exc}")
            time.sleep(backoff_seconds)
        finally:
            if session is not None:
                session.close()
                session = None


def create_tables() -> None:
    """Create all database tables registered with SQLAlchemy Base."""
    # Import all models to ensure they're registered with Base
    from .models import user  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"❌ Error creating database tables: {exc}")
        raise