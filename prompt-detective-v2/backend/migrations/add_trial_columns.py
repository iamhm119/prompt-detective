"""
Add trial-related columns to users table
"""
import sqlite3
import sys
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_data.sqlite3")

def add_trial_columns():
    """Add trial columns to users table if they don't exist"""
    print(f"🔄 Adding trial columns to users table...")
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
        print(f"📋 Existing columns: {len(existing_columns)}")
        
        # Columns to add
        columns_to_add = [
            ("is_on_trial", "BOOLEAN DEFAULT 0"),
            ("trial_started_at", "TIMESTAMP"),
            ("trial_ends_at", "TIMESTAMP"),
            ("has_used_trial", "BOOLEAN DEFAULT 0"),
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
                print(f"  ✓ Column already exists: {column_name}")
                skipped_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Migration complete!")
        print(f"   Added: {added_count} columns")
        print(f"   Skipped: {skipped_count} columns (already exist)")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_trial_columns()
    sys.exit(0 if success else 1)
