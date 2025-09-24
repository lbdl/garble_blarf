"""
voicememo_db

Searches for a voicememo db in the ususal location, this is noteworthy:
    `~/Library/G
"""
import sqlite3
import os
from pathlib import Path

def _check_db_access():
    """Check if we can access the Voice Memos database"""
    containers = "Library/Group Containers"
    voice_memo_base = "group.com.apple.VoiceMemos.shared/Recordings"
    db_file = "CloudRecordings.db"
    db_path = Path.home() / containers / voice_memo_base / db_file
    
    print(f"Checking: {db_path}")
    
    if not db_path.exists():
        print("❌ Database file not found")
        return False, "❌ Database file not found"
    
    if not os.access(db_path, os.R_OK):
        print("❌ No read permission")
        return False, "❌ No read permission"
    
    try:
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("SELECT 1").fetchone()
        print("✅ Database accessible")
        return True, db_path 
    except sqlite3.OperationalError as e:
        print(f"❌ Cannot open database: {e}")
        return False, f"❌ Cannot open database: {e}"

def get_db_path():
    fp = _check_db_access()
    return fp[1]


def cli_get_db_path():
    fp = _check_db_access()
    return fp


def get_schema():
    """Find out what tables and columns exist"""
    db_path = get_db_path()
    
    with sqlite3.connect(str(db_path)) as conn:
        # Get all tables
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print("Tables found:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Get column info for each table
        for table in tables:
            table_name = table[0]
            print(f"\nColumns in {table_name}:")
            columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")


def get_memo_files():
    """Get voice memo file paths and metadata from database"""
    db_path = get_db_path()
    
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.execute("""
            SELECT 
                ZUNIQUEID,
                ZCUSTOMLABEL,
                ZENCRYPTEDTITLE, 
                ZPATH,
                ZDURATION,
                ZDATE
            FROM ZCLOUDRECORDING 
            WHERE ZPATH IS NOT NULL
            ORDER BY ZDATE DESC
        """)
        
        recordings = []
        for row in cursor.fetchall():
            recording = {
                'unique_id': row[0],
                'custom_label': row[1], # this seems to map to a date stamp
                'encrypted_title': row[2], # in fact the DE crypted title 
                'path': row[3], 
                'duration': row[4],
                'date': row[5] # float number
            }
            recordings.append(recording)
        
        return recordings

if __name__ == "__main__":
    import sys
    globals()[sys.argv[1]]()
