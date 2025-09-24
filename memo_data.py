import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class VoiceMemoFolder:
    """Represents a Voice Memos folder with its metadata."""
    pk: int
    encrypted_name: str
    uuid: str
    rank: int
    recording_count: int
    
    def __str__(self) -> str:
        return f"Folder(id={self.pk}, name='{self.encrypted_name}', recordings={self.recording_count})"

def query_folder_structure(db_path: str) -> Dict[int, VoiceMemoFolder]:
    """
    Query the Voice Memos database to understand the folder structure.
    
    Args:
        db_path: Path to the CloudRecordings.db file
        
    Returns:
        Dictionary mapping folder PK to VoiceMemoFolder objects
        
    Reasoning:
        - ZFOLDER table contains the folder metadata
        - ZENCRYPTEDNAME likely contains the folder name (may need decryption)
        - ZRANK determines display order
        - ZCOUNTOFRECORDINGS shows how many recordings are in each folder
        - We need to understand if there's a hierarchy (parent-child relationships)
    """
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    
    try:
        cursor = conn.cursor()
        
        # Query all folders with their metadata
        query = """
        SELECT 
            Z_PK as pk,
            ZENCRYPTEDNAME as encrypted_name,
            ZUUID as uuid,
            ZRANK as rank,
            ZCOUNTOFRECORDINGS as recording_count
        FROM ZFOLDER 
        ORDER BY ZRANK ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        folders = {}
        for row in rows:
            folder = VoiceMemoFolder(
                pk=row['pk'],
                encrypted_name=row['encrypted_name'] or 'Unnamed',
                uuid=row['uuid'] or '',
                rank=row['rank'] or 0,
                recording_count=row['recording_count'] or 0
            )
            folders[folder.pk] = folder
            
        return folders
        
    finally:
        conn.close()

def analyze_folder_usage(db_path: str) -> Tuple[Dict[int, VoiceMemoFolder], Dict[int, int]]:
    """
    Analyze how recordings are distributed across folders.
    
    Returns:
        Tuple of (folders_dict, folder_usage_count)
        
    Reasoning:
        - We need to cross-reference ZCLOUDRECORDING.ZFOLDER with actual folder data
        - This will show us which folders are actually used
        - Help identify orphaned recordings (ZFOLDER = NULL or 0)
    """
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get folder structure
        folders = query_folder_structure(db_path)
        
        # Count actual recordings per folder
        cursor = conn.cursor()
        usage_query = """
        SELECT 
            ZFOLDER as folder_id,
            COUNT(*) as actual_count
        FROM ZCLOUDRECORDING 
        GROUP BY ZFOLDER
        ORDER BY folder_id
        """
        
        cursor.execute(usage_query)
        usage_rows = cursor.fetchall()
        
        folder_usage = {}
        for row in usage_rows:
            folder_id = row['folder_id']
            actual_count = row['actual_count']
            folder_usage[folder_id] = actual_count
            
        return folders, folder_usage
        
    finally:
        conn.close()


# Test function to validate our understanding
def print_folder_analysis(db_path: str):
    """Debug function to print folder structure analysis."""
    
    folders, usage = analyze_folder_usage(db_path)
    
    print("=== FOLDER STRUCTURE ANALYSIS ===")
    print(f"Total folders found: {len(folders)}")
    print()
    
    for folder_id, folder in folders.items():
        actual_count = usage.get(folder_id, 0)
        stored_count = folder.recording_count
        status = "✓" if actual_count == stored_count else "⚠️"
        
        print(f"{status} {folder}")
        print(f"    Stored count: {stored_count}, Actual count: {actual_count}")
        print(f"    UUID: {folder.uuid}")
        print()
    
    # Check for recordings without folders (orphaned)
    orphaned_count = usage.get(None, 0) + usage.get(0, 0)
    if orphaned_count > 0:
        print(f"⚠️  Found {orphaned_count} recordings without folder assignment")
