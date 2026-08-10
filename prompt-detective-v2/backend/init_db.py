#!/usr/bin/env python3
"""
Initialize database tables
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import create_tables

if __name__ == "__main__":
    print("🔄 Creating database tables...")
    try:
        create_tables()
        print("✅ Database initialization completed!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)