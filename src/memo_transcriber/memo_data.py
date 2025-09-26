import sqlite3
from .voicememo_db import get_db_path, get_memos_with_folders
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass



@dataclass
class VoiceMemoFile:
    """Represents a Voice Memo file with its metadata."""
    uuid: str
    encrypted_name: str
    f_path: str
    memo_folder: str

    def __str__(self) -> str:
        return (f"File: name='{self.encrypted_name}', "
                        f"uuid={self.uuid}, "
                        f"folder={self.memo_folder}, "
                        f"path={self.f_path}")


@dataclass
class VoiceMemoFolder:
    """Represents a Voice Memos folder with its metadata."""
    pk: int
    plain_name: str
    uuid: str
    rank: int
    recording_count: int

    def __str__(self) -> str:
        return f"Folder(id={self.uuid}, name='{self.plain_name}', recordings={self.recording_count})"


@dataclass
class UnassignedRecordings:
    """Represents recordings not assigned to any folder."""
    count: int
    folder_id: Optional[int]  # Could be None, 0, or other values
    
    def __str__(self) -> str:
        folder_desc = "NULL" if self.folder_id is None else str(self.folder_id)
        return f"Unassigned(folder_id={folder_desc}, recordings={self.count})"


def get_memo_data(db_path: str) -> List[VoiceMemoFile]:
    memos = get_memos_with_folders(db_path)
    memo_files = []

    for record in memos:
        memo = VoiceMemoFile(
            uuid=record['recording_id'] or '',
            encrypted_name=record['title'] or 'Untitled',
            f_path=record['file_path'] or '',
            memo_folder=record['folder_name'] or 'Unassigned'
        )
        memo_files.append(memo)

    return memo_files



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
            ZENCRYPTEDNAME as plain_name,
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
                plain_name=row['plain_name'] or 'Unnamed',
                uuid=row['uuid'] or '',
                rank=row['rank'] or 0,
                recording_count=row['recording_count'] or 0
            )
            folders[folder.pk] = folder
            
        return folders
        
    finally:
        conn.close()

def analyze_folder_usage(db_path: str) -> Tuple[Dict[int, VoiceMemoFolder], Dict[Optional[int], int]]:
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


def get_unassigned_recordings(folder_usage: Dict[Optional[int], int]) -> List[UnassignedRecordings]:
    """
    Extract unassigned recording information from folder usage data.
    
    Args:
        folder_usage: Dictionary from analyze_folder_usage()
        
    Returns:
        List of UnassignedRecordings objects for different unassigned states
        
    Reasoning:
        - Recordings might be unassigned in different ways:
          - ZFOLDER = NULL (None in Python)
          - ZFOLDER = 0 (default/root folder?)
          - ZFOLDER = negative values (error states?)
        - We need to capture all these cases for complete analysis
    """
    
    unassigned = []
    
    # Check for common unassigned states
    unassigned_indicators = [None, 0]
    
    for folder_id in unassigned_indicators:
        if folder_id in folder_usage:
            unassigned.append(UnassignedRecordings(
                count=folder_usage[folder_id],
                folder_id=folder_id
            ))
    
    # Check for any negative or unusual folder IDs that might indicate unassigned state
    for folder_id, count in folder_usage.items():
        if folder_id is not None and folder_id < 0:
            unassigned.append(UnassignedRecordings(
                count=count,
                folder_id=folder_id
            ))
    
    return unassigned


def list_unassigned_recording_details(db_path: str) -> List[Dict]:
    """
    Get detailed information about each unassigned recording.
    
    Returns:
        List of dictionaries with recording details for unassigned recordings
        
    Usage:
        unassigned_details = list_unassigned_recording_details(db_path)
        
        for recording in unassigned_details:
            print(f"Recording: {recording['title']} (Duration: {recording['duration']}s)")
            print(f"  Path: {recording['path']}")
            print(f"  Date: {recording['date']}")
    """
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        
        # Query for recordings that are unassigned (ZFOLDER is NULL, 0, or negative)
        query = """
        SELECT 
            Z_PK as pk,
            ZCUSTOMLABEL as title,
            ZENCRYPTEDTITLE as plain_name,
            ZPATH as path,
            ZDURATION as duration,
            ZDATE as date_timestamp,
            ZFOLDER as folder_id,
            ZUNIQUEID as unique_id,
            datetime(ZDATE + 978307200, 'unixepoch') as formatted_date
        FROM ZCLOUDRECORDING 
        WHERE ZFOLDER IS NULL 
           OR ZFOLDER = 0 
           OR ZFOLDER < 0
        ORDER BY ZDATE DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        recordings = []
        for row in rows:
            recordings.append({
                'pk': row['pk'],
                'title': row['title'] or 'Untitled',
                'name': row['plain_name'] or 'Unnamed',
                'path': row['path'] or '',
                'duration': row['duration'] or 0.0,
                'date_timestamp': row['date_timestamp'],
                'formatted_date': row['formatted_date'],
                'folder_id': row['folder_id'],
                'unique_id': row['unique_id'] or '',
            })
            
        return recordings
        
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    db_p = get_db_path()
    globals()[sys.argv[1]](db_p)
