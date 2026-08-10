"""
Simple Database Reset Script for Production
Drops and recreates all tables without importing models
WARNING: This will DELETE ALL DATA!
"""
import os
import sys
from sqlalchemy import create_engine, text

def reset_database_simple():
    """Drop and recreate all tables using raw SQL"""
    print("🗑️  Simple Database Reset Script")
    print("=" * 60)
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nSet it first:")
        print('$env:DATABASE_URL="postgresql://..."')
        sys.exit(1)
    
    print(f"\n📍 Database: {database_url[:50]}...")
    
    # Confirm this is what you want
    if 'postgres' in database_url:
        print("\n⚠️  WARNING: This will DELETE ALL DATA in the production database!")
        confirm = input("\nType 'DELETE ALL DATA' to confirm: ")
        if confirm != 'DELETE ALL DATA':
            print("❌ Aborted. No changes made.")
            return
    
    print("\n🔧 Starting database reset...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("\n🗑️  Dropping all tables...")
                
                # Drop tables in correct order (foreign keys first)
                tables_to_drop = [
                    'admin_notes',
                    'otp_codes',
                    'usage_logs',
                    'analysis_jobs',
                    'api_keys',
                    'subscriptions',
                    'users'
                ]
                
                for table in tables_to_drop:
                    print(f"  Dropping {table}...")
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                
                print("✅ All tables dropped successfully")
                
                print("\n🏗️  Creating fresh tables...")
                
                # Create users table
                conn.execute(text("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(255) NOT NULL,
                        username VARCHAR(255) UNIQUE,
                        subscription_tier VARCHAR(50) DEFAULT 'free',
                        is_active BOOLEAN DEFAULT TRUE,
                        is_premium BOOLEAN DEFAULT FALSE,
                        is_email_verified BOOLEAN DEFAULT FALSE,
                        api_calls_used INTEGER DEFAULT 0,
                        api_calls_limit INTEGER DEFAULT 100,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ Created users table")
                
                # Create OTP codes table
                conn.execute(text("""
                    CREATE TABLE otp_codes (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        code VARCHAR(6) NOT NULL,
                        otp_type VARCHAR(50) NOT NULL,
                        is_used BOOLEAN DEFAULT FALSE,
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ Created otp_codes table")
                
                # Create API keys table
                conn.execute(text("""
                    CREATE TABLE api_keys (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        name VARCHAR(255) NOT NULL,
                        key_hash VARCHAR(255) UNIQUE NOT NULL,
                        prefix VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        last_used_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ Created api_keys table")
                
                # Create analysis jobs table
                conn.execute(text("""
                    CREATE TABLE analysis_jobs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        filename VARCHAR(255) NOT NULL,
                        file_path VARCHAR(500) NOT NULL,
                        file_size_bytes INTEGER,
                        content_type VARCHAR(50) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        progress INTEGER DEFAULT 0,
                        error_message TEXT,
                        result_data JSONB,
                        processing_time_seconds INTEGER,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP WITH TIME ZONE
                    )
                """))
                print("  ✓ Created analysis_jobs table")
                
                # Create usage logs table
                conn.execute(text("""
                    CREATE TABLE usage_logs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        action VARCHAR(50) NOT NULL,
                        details JSONB,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ Created usage_logs table")
                
                # Create subscriptions table
                conn.execute(text("""
                    CREATE TABLE subscriptions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        plan VARCHAR(50) NOT NULL,
                        status VARCHAR(50) DEFAULT 'active',
                        daily_limit INTEGER DEFAULT 5,
                        monthly_limit INTEGER DEFAULT 150,
                        started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        stripe_subscription_id VARCHAR(255)
                    )
                """))
                print("  ✓ Created subscriptions table")
                
                # Create admin notes table
                conn.execute(text("""
                    CREATE TABLE admin_notes (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        admin_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        note TEXT NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ Created admin_notes table")
                
                print("\n📊 Creating indexes...")
                
                # Create indexes
                conn.execute(text("CREATE INDEX idx_users_email ON users(email)"))
                conn.execute(text("CREATE INDEX idx_users_username ON users(username)"))
                conn.execute(text("CREATE INDEX idx_otp_codes_user_id ON otp_codes(user_id)"))
                conn.execute(text("CREATE INDEX idx_api_keys_user_id ON api_keys(user_id)"))
                conn.execute(text("CREATE INDEX idx_analysis_jobs_user_id ON analysis_jobs(user_id)"))
                conn.execute(text("CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id)"))
                
                print("  ✓ Created all indexes")
                
                # Commit transaction
                trans.commit()
                
                print("\n✅ Database reset complete!")
                print("\n📊 Fresh database ready for use:")
                print("  - 7 tables created")
                print("  - All old data deleted")
                print("  - Ready for new signups")
                print("  - Can reuse previously registered emails")
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        print(f"\n❌ Error during database reset: {e}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    reset_database_simple()
