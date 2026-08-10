"""
Check users in local SQLite database
"""
import sqlite3
from pathlib import Path

def check_local_users():
    """Check what users exist in local database"""
    db_path = Path(__file__).parent / "app_data.sqlite3"
    
    if not db_path.exists():
        print("❌ Database file not found:", db_path)
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total users in local database: {total}")
        
        if total > 0:
            # Show all users with admin fields
            cursor.execute("""
                SELECT id, email, full_name, username, 
                       is_active, is_premium, is_email_verified,
                       is_admin, is_super_admin, 
                       api_calls_used, api_calls_limit,
                       subscription_tier, created_at
                FROM users 
                ORDER BY id
            """)
            
            print("\n👥 Users in local database:")
            print("=" * 120)
            
            for row in cursor.fetchall():
                user_id, email, full_name, username = row[0], row[1], row[2], row[3]
                is_active, is_premium, is_verified = row[4], row[5], row[6]
                is_admin, is_super_admin = row[7], row[8]
                api_used, api_limit = row[9], row[10]
                tier, created = row[11], row[12]
                
                print(f"\n📋 User ID: {user_id}")
                print(f"   Email: {email}")
                print(f"   Name: {full_name}")
                print(f"   Username: {username}")
                print(f"   Tier: {tier}")
                print(f"   Status: {'✅ Active' if is_active else '❌ Inactive'} | "
                      f"{'⭐ Premium' if is_premium else '○ Free'} | "
                      f"{'✓ Verified' if is_verified else '✗ Not Verified'}")
                print(f"   Admin: {'👑 SUPER ADMIN' if is_super_admin else ('🔐 Admin' if is_admin else '○ Regular User')}")
                print(f"   API Usage: {api_used} / {'Unlimited' if api_limit == -1 else api_limit}")
                print(f"   Created: {created}")
            
            print("=" * 120)
            
            # Check specifically for super admin
            cursor.execute("""
                SELECT id, email, is_admin, is_super_admin 
                FROM users 
                WHERE email = 'tryreverseai@gmail.com'
            """)
            admin = cursor.fetchone()
            
            if admin:
                print(f"\n✅ Super admin account found:")
                print(f"   ID: {admin[0]}")
                print(f"   Email: {admin[1]}")
                print(f"   is_admin: {admin[2]}")
                print(f"   is_super_admin: {admin[3]}")
                
                if admin[2] == 1 and admin[3] == 1:
                    print("   ✅ Admin flags are correct!")
                else:
                    print("   ❌ Admin flags are NOT correct!")
                    print(f"      Expected: is_admin=1, is_super_admin=1")
                    print(f"      Got: is_admin={admin[2]}, is_super_admin={admin[3]}")
            else:
                print("\n❌ Super admin account (tryreverseai@gmail.com) NOT FOUND!")
                print("   Run: python create_super_admin_local.py")
        else:
            print("\n❌ No users found in database")
            print("   Run: python create_super_admin_local.py")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_local_users()
