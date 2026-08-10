"""Migration: remove launch pricing/referral columns and create waitlist table."""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def run_migration(database_url: str) -> None:
    """Execute cleanup migration within a single connection."""
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Drop referral columns from users
        try:
            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS referral_code"))
            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS referred_by_code"))
            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS referral_credits"))
            conn.commit()
            print("✅ Referral columns removed from users table")
        except SQLAlchemyError as exc:
            conn.rollback()
            print(f"⚠️ Failed to drop referral columns: {exc}")

        # Drop launch pricing columns from subscriptions
        try:
            conn.execute(text("ALTER TABLE subscriptions DROP COLUMN IF EXISTS is_launch_pricing"))
            conn.execute(text("ALTER TABLE subscriptions DROP COLUMN IF EXISTS locked_price"))
            conn.commit()
            print("✅ Launch pricing columns removed from subscriptions table")
        except SQLAlchemyError as exc:
            conn.rollback()
            print(f"⚠️ Failed to drop launch pricing columns: {exc}")

        # Create waitlist table
        try:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS waitlist_subscribers (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) NOT NULL,
                        plan_name VARCHAR(100),
                        source VARCHAR(100),
                        notes TEXT,
                        is_notified BOOLEAN DEFAULT false,
                        notified_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE,
                        CONSTRAINT uq_waitlist_email_plan UNIQUE (email, plan_name)
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist_subscribers(email)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_waitlist_plan ON waitlist_subscribers(plan_name)"))
            conn.commit()
            print("✅ Waitlist table created")
        except SQLAlchemyError as exc:
            conn.rollback()
            print(f"⚠️ Failed to create waitlist table: {exc}")
