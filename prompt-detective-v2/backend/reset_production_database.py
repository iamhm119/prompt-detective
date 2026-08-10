"""
Database Reset Script for Production
Drops all tables and recreates them fresh
WARNING: This will DELETE ALL DATA!
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_root = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import create_engine, text, inspect
from app.database import Base, engine
from app.models.user import (
    User, OTPCode, APIKey, AnalysisJob, UsageLog, 
    Subscription, AdminNote
)

def reset_database():
    """Drop all tables and recreate them"""
    print("🗑️  Database Reset Script")
    print("=" * 60)
    
    # Confirm this is what you want
    print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print(f"Database: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
    
    # Check if production
    if 'postgres' in os.getenv('DATABASE_URL', ''):
        confirm = input("\n⚠️  This is a PRODUCTION database. Type 'DELETE ALL DATA' to confirm: ")
        if confirm != 'DELETE ALL DATA':
            print("❌ Aborted. No changes made.")
            return
    
    print("\n🔧 Starting database reset...")
    
    try:
        # Get inspector to check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"\n📋 Found {len(existing_tables)} existing tables:")
        for table in existing_tables:
            print(f"  - {table}")
        
        # Drop all tables
        print("\n🗑️  Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
        
        # Recreate all tables
        print("\n🏗️  Creating fresh tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Verify tables were created
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        print(f"\n📋 Created {len(new_tables)} fresh tables:")
        for table in new_tables:
            print(f"  - {table}")
        
        print("\n✅ Database reset complete!")
        print("\n📊 Fresh database ready for use:")
        print("  - All old users deleted")
        print("  - All old OTP codes deleted")
        print("  - All old analyses deleted")
        print("  - Ready for new signups")
        
    except Exception as e:
        print(f"\n❌ Error during database reset: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
