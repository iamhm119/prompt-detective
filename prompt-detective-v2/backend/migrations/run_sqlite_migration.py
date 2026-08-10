"""
SQLite Migration: Recreate tables with new structure
This is needed because SQLite doesn't support ALTER TABLE ... ADD COLUMN for all cases
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.models.user import (
    User, APIKey, AnalysisJob, UsageLog, Subscription,
    AdminNote, OTPCode, Payment, CreditPack, EmailLog, WaitlistSubscriber
)
from app.models.contact_message import ContactMessage

def run_sqlite_migration():
    """
    Create all new tables for SQLite
    """
    print("🔄 Running SQLite migration...")
    
    try:
        # Create all tables (will skip existing ones)
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created/verified successfully!")
        
        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Database tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_sqlite_migration()
    sys.exit(0 if success else 1)
