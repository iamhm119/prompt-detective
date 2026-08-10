"""
Check and optionally clean users from production database
"""
import os
import sys
from sqlalchemy import create_engine, text

def check_users():
    """Check what users exist in production database"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        print("💡 Make sure to set it from .env.production")
        return
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Count total users
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            total = result.scalar()
            print(f"\n📊 Total users in database: {total}")
            
            if total > 0:
                # Show all users
                result = conn.execute(text("""
                    SELECT id, email, username, full_name, is_email_verified, created_at 
                    FROM users 
                    ORDER BY created_at DESC
                """))
                
                print("\n👥 Users in database:")
                print("-" * 100)
                for row in result:
                    verified = "✅" if row[4] else "❌"
                    print(f"{verified} ID: {row[0]} | Email: {row[1]} | Username: {row[2]} | Name: {row[3]} | Created: {row[5]}")
                print("-" * 100)
                
                # Ask if user wants to delete
                print("\n⚠️  Do you want to DELETE ALL USERS? (type 'yes' to confirm)")
                response = input("> ").strip().lower()
                
                if response == "yes":
                    # Delete all users and related data
                    tables_to_clear = [
                        "otp_codes",
                        "refresh_tokens",
                        "analyses", 
                        "usage_logs",
                        "users"
                    ]
                    
                    for table in tables_to_clear:
                        try:
                            conn.execute(text(f"DELETE FROM {table}"))
                            conn.commit()  # Commit after each successful delete
                            print(f"  ✓ Cleared {table}")
                        except Exception as e:
                            conn.rollback()  # Rollback on error
                            if "does not exist" in str(e):
                                print(f"  ⊘ Skipped {table} (doesn't exist)")
                            else:
                                print(f"  ✗ Failed to clear {table}: {e}")
                    
                    print("\n✅ Database cleanup completed!")
                else:
                    print("\n❌ Deletion cancelled")
            else:
                print("\n✅ Database is clean - no users found")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Load environment from .env.production
    from pathlib import Path
    env_file = Path(__file__).parent / ".env.production"
    
    if env_file.exists():
        print("📂 Loading environment from .env.production...")
        with open(env_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    
    check_users()
