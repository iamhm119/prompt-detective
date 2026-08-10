#!/usr/bin/env python3
"""
Auto-migration script that runs on backend startup
This will automatically add missing columns to the production database
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

def run_migrations():
    """Run database migrations automatically"""
    
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("⚠️  No DATABASE_URL found, skipping migrations")
        return
    
    # Skip migrations for SQLite (local development)
    if DATABASE_URL.startswith("sqlite"):
        print("ℹ️  SQLite detected, running SQLite-specific migrations")
        try:
            # Import and run SQLite migration
            from migrations.run_sqlite_migration import run_sqlite_migration
            run_sqlite_migration()
        except Exception as e:
            print(f"⚠️  SQLite migration warning: {e}")
        return
    
    # Handle Render's postgres:// URL (needs to be postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    print("🔄 Running database migrations...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if is_email_verified column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'is_email_verified'
            """))
            
            exists = result.fetchone() is not None
            
            if not exists:
                print("   Adding 'is_email_verified' column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN is_email_verified BOOLEAN DEFAULT false
                """))
                conn.commit()
                print("   ✅ Column 'is_email_verified' added successfully!")
            
            # Run subscription features migration
            try:
                from migrations.add_subscription_features import run_migration
                run_migration(DATABASE_URL)
            except Exception as e:
                print(f"⚠️ Subscription features migration: {e}")

            try:
                from migrations.cleanup_launch_referral import run_migration as run_cleanup
                run_cleanup(DATABASE_URL)
            except Exception as e:
                print(f"⚠️ Cleanup migration warning: {e}")
            
            print("   ✅ All migrations completed")
                
    except Exception as e:
        print(f"   ⚠️  Migration warning: {e}")
        # Don't fail startup if migration fails
        pass

if __name__ == "__main__":
    run_migrations()
