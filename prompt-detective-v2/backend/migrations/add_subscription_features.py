"""
Migration: Add subscription features, trials, payments, credits
"""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os

def run_migration(database_url: str):
    """Run migration for adding subscription features"""
    
    engine = create_engine(database_url)
    
    with engine.connect() as conn:

        def column_exists(table: str, column: str) -> bool:
            result = conn.execute(
                text(
                    """
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = :table
                    AND column_name = :column
                    """
                ),
                {"table": table, "column": column},
            )
            return result.scalar() is not None

        # Add new columns to users table
        try:
            # Trial management
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_on_trial BOOLEAN DEFAULT false"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_started_at TIMESTAMP WITH TIME ZONE"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMP WITH TIME ZONE"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS has_used_trial BOOLEAN DEFAULT false"))
            
            # Usage tracking
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_analyses_count INTEGER DEFAULT 0"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_reset_date TIMESTAMP WITH TIME ZONE"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS total_analyses_count INTEGER DEFAULT 0"))
            
            # Referral system
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code VARCHAR(20) UNIQUE"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by_code VARCHAR(20)"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_credits INTEGER DEFAULT 0"))
            
            # Last login
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE"))
            conn.commit()
            
            print("✅ Users table updated")
        except SQLAlchemyError as e:
            conn.rollback()
            print(f"⚠️ Users table migration: {e}")
        
        # Update subscriptions table
        try:
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50) DEFAULT 'pending'"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS api_calls_limit INTEGER DEFAULT 0"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS billing_cycle VARCHAR(20)"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS price_paid FLOAT"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'INR'"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS next_billing_date TIMESTAMP WITH TIME ZONE"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMP WITH TIME ZONE"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS razorpay_subscription_id VARCHAR(255)"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS razorpay_customer_id VARCHAR(255)"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS auto_renew BOOLEAN DEFAULT true"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS is_launch_pricing BOOLEAN DEFAULT false"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS locked_price FLOAT"))
            conn.commit()

            if column_exists("subscriptions", "stripe_subscription_id") and not column_exists("subscriptions", "razorpay_subscription_id"):
                try:
                    conn.execute(text("ALTER TABLE subscriptions RENAME COLUMN stripe_subscription_id TO razorpay_subscription_id"))
                    conn.commit()
                    print("ℹ️  Renamed stripe_subscription_id to razorpay_subscription_id")
                except SQLAlchemyError as rename_error:
                    conn.rollback()
                    print(f"⚠️ Subscriptions column rename: {rename_error}")
            else:
                print("ℹ️  No legacy stripe_subscription_id column to rename")
            
            print("✅ Subscriptions table updated")
        except SQLAlchemyError as e:
            conn.rollback()
            print(f"⚠️ Subscriptions table migration: {e}")
        
        # Create payments table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    amount FLOAT NOT NULL,
                    currency VARCHAR(10) DEFAULT 'INR',
                    payment_type VARCHAR(50) NOT NULL,
                    payment_method VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'pending',
                    razorpay_order_id VARCHAR(255) UNIQUE,
                    razorpay_payment_id VARCHAR(255) UNIQUE,
                    razorpay_signature VARCHAR(500),
                    description TEXT,
                    payment_metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP WITH TIME ZONE
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)"))
            print("✅ Payments table created")
            conn.commit()
        except SQLAlchemyError as e:
            conn.rollback()
            print(f"⚠️ Payments table creation: {e}")
        
        # Create credit_packs table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS credit_packs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    pack_name VARCHAR(50) NOT NULL,
                    analyses_total INTEGER NOT NULL,
                    analyses_remaining INTEGER NOT NULL,
                    price_paid FLOAT NOT NULL,
                    purchased_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_active BOOLEAN DEFAULT true
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_credit_packs_user_id ON credit_packs(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_credit_packs_active ON credit_packs(is_active)"))
            print("✅ Credit packs table created")
            conn.commit()
        except SQLAlchemyError as e:
            conn.rollback()
            print(f"⚠️ Credit packs table creation: {e}")
        
        # Create contact_messages table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS contact_messages (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    subject VARCHAR(500) NOT NULL,
                    message TEXT NOT NULL,
                    category VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'new',
                    priority VARCHAR(20) DEFAULT 'normal',
                    auto_response_sent BOOLEAN DEFAULT false,
                    admin_response TEXT,
                    responded_at TIMESTAMP WITH TIME ZONE,
                    responded_by INTEGER REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))

            required_contact_columns = {
                "status": "VARCHAR(50) DEFAULT 'new'",
                "priority": "VARCHAR(20) DEFAULT 'normal'",
                "auto_response_sent": "BOOLEAN DEFAULT false",
                "responded_by": "INTEGER REFERENCES users(id)",
            }

            for col_name, col_def in required_contact_columns.items():
                if not column_exists("contact_messages", col_name):
                    conn.execute(
                        text(
                            f"ALTER TABLE contact_messages ADD COLUMN {col_name} {col_def}"
                        )
                    )

            if column_exists("contact_messages", "status"):
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_contact_status ON contact_messages(status)"
                    )
                )

            conn.commit()
            print("✅ Contact messages table created")
        except SQLAlchemyError as e:
            conn.rollback()
            print(f"⚠️ Contact messages table creation: {e}")
        
        # Create email_logs table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS email_logs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    email_to VARCHAR(255) NOT NULL,
                    email_type VARCHAR(50) NOT NULL,
                    subject VARCHAR(500) NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP WITH TIME ZONE
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_email_logs_user_id ON email_logs(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_email_logs_type ON email_logs(email_type)"))
            print("✅ Email logs table created")
            conn.commit()
        except SQLAlchemyError as e:
            conn.rollback()
            print(f"⚠️ Email logs table creation: {e}")
        print("🎉 Migration completed successfully!")

if __name__ == "__main__":
    # For production
    database_url = os.getenv("DATABASE_URL", "")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        run_migration(database_url)
    else:
        print("❌ No DATABASE_URL found")
