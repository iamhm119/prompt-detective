"""
Add missing columns to users table
"""
import sqlite3
import sys
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_data.sqlite3")

def add_missing_columns():
    """Add all missing columns to users table"""
    print(f"🔄 Adding missing columns to users table...")
    print(f"📁 Database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Existing columns ({len(existing_columns)}): {', '.join(existing_columns)}")
        
        # All columns that should exist (based on User model)
        columns_to_add = [
            # Usage tracking
            ("daily_analyses_count", "INTEGER DEFAULT 0"),
            ("last_reset_date", "TIMESTAMP"),
            ("total_analyses_count", "INTEGER DEFAULT 0"),
            
            # Referral system
            ("referral_code", "VARCHAR"),
            ("referred_by_code", "VARCHAR"),
            ("referral_credits", "INTEGER DEFAULT 0"),
            
            # Last login
            ("last_login_at", "TIMESTAMP"),
        ]
        
        added_count = 0
        skipped_count = 0
        
        for column_name, column_def in columns_to_add:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                    print(f"  ➕ Adding column: {column_name}")
                    cursor.execute(sql)
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"  ⚠️  Failed to add {column_name}: {e}")
            else:
                skipped_count += 1
        
        conn.commit()
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(users)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"\n📊 Final column count: {len(final_columns)}")
        
        conn.close()
        
        print(f"\n✅ Migration complete!")
        print(f"   Added: {added_count} columns")
        print(f"   Already existed: {skipped_count} columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_missing_columns()
    sys.exit(0 if success else 1)
