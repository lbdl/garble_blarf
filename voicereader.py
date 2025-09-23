import sqlite3
import os
from pathlib import Path

def check_db_access():
    """Check if we can access the Voice Memos database"""
    containers = "Library/Group Containers"
    voice_memo_base = "group.com.apple.VoiceMemos.shared/Recordings"
    db_file = "CloudRecordings.db"
    db_path = Path.home() / containers / voice_memo_base / db_file
    
    print(f"Checking: {db_path}")
    
    if not db_path.exists():
        print("❌ Database file not found")
        return False
    
    if not os.access(db_path, os.R_OK):
        print("❌ No read permission")
        return False
    
    try:
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("SELECT 1").fetchone()
        print("✅ Database accessible")
        return True, db_path 
    except sqlite3.OperationalError as e:
        print(f"❌ Cannot open database: {e}")
        return False, ""

def get_db_path():
    fp = check_db_access()
    if fp[0] == True:
        return fp[1]
        


if __name__ == "__main__":
    print(f"{get_db_path()}")
