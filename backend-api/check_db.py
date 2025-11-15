#!/usr/bin/env python3
"""Check what tables exist in the SQLite database"""
import sqlite3

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📋 TABLES IN DATABASE:")
    for table in tables:
        print(f"  - {table[0]}")
        
    # Check if dashboard_newsarticle exists
    if 'dashboard_newsarticle' in [table[0] for table in tables]:
        cursor.execute("SELECT COUNT(*) FROM dashboard_newsarticle;")
        count = cursor.fetchone()[0]
        print(f"✅ dashboard_newsarticle exists with {count} records")
    else:
        print("❌ dashboard_newsarticle table does NOT exist")
        
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")
