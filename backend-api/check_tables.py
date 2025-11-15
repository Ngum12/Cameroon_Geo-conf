#!/usr/bin/env python3
"""Check what tables exist and inject data into the correct Django table"""
import sqlite3

def check_and_fix_tables():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Find all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = cursor.fetchall()
    print("📊 All tables in database:")
    for table in all_tables:
        print(f"  - {table[0]}")
    
    # Find news/article tables specifically
    news_tables = []
    for table in all_tables:
        if 'news' in table[0].lower() or 'article' in table[0].lower():
            news_tables.append(table[0])
    
    print(f"\n📰 News/Article tables: {news_tables}")
    
    # Check what's in each news table
    for table_name in news_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n📊 {table_name}: {count} records")
            
            if count > 0:
                cursor.execute(f"SELECT title, source FROM {table_name} LIMIT 3")
                records = cursor.fetchall()
                for record in records:
                    print(f"  - {record[0][:50]}... (Source: {record[1]})")
        except Exception as e:
            print(f"  ❌ Error reading {table_name}: {e}")
    
    conn.close()

if __name__ == '__main__':
    check_and_fix_tables()
