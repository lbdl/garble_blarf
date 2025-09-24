import sqlite3
from .voicememo_db import get_db_path
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


@dataclass
class UnassignedRecordings:
    """Represents recordings not assigned to any folder."""
    count: int
    folder_id: Optional[int]  # Could be None, 0, or other values
    
    def __str__(self) -> str:
        folder_desc = "NULL" if self.folder_id is None else str(self.folder_id)
        return f"Unassigned(folder_id={folder_desc}, recordings={self.count})"


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


def get_unassigned_recordings_direct(db_path: str) -> Tuple[List[UnassignedRecordings], int]:
    """
    Direct function to get unassigned recordings without needing the full analysis.
    
    Returns:
        Tuple of (unassigned_recordings_list, total_unassigned_count)
        
    Usage:
        unassigned_list, total_count = get_unassigned_recordings_direct(db_path)
        
        if total_count > 0:
            print(f"Found {total_count} unassigned recordings:")
            for group in unassigned_list:
                print(f"  - {group}")
    """
    
    _, usage = analyze_folder_usage(db_path)
    unassigned = get_unassigned_recordings(usage)
    total_count = sum(group.count for group in unassigned)
    
    return unassigned, total_count


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


# Test function to validate our understanding
def print_folder_analysis(db_path: str):
    """Debug function to print folder structure analysis."""

    folders, usage = analyze_folder_usage(db_path)
    unassigned = get_unassigned_recordings(usage)

    print("=== FOLDER STRUCTURE ANALYSIS ===")
    print(f"Total folders found: {len(folders)}")
    print(f"Total folder assignments tracked: {len(usage)}")
    print()

    # Print assigned folders
    print("--- ASSIGNED FOLDERS ---")
    assigned_recordings = 0
    for folder_id, folder in folders.items():
        actual_count = usage.get(folder_id, 0)
        stored_count = folder.recording_count
        status = "✓" if actual_count == stored_count else "⚠️"

        print(f"{status} {folder}")
        print(f"    Stored count: {stored_count}, Actual count: {actual_count}")
        print(f"    UUID: {folder.uuid}")
        if actual_count != stored_count:
            print("    ⚠️  Count mismatch - database may need maintenance")
        print()

        assigned_recordings += actual_count


    # Print unassigned recordings
    print("--- UNASSIGNED RECORDINGS ---")
    total_unassigned = 0
    if unassigned:
        for unassigned_group in unassigned:
            print(f"📁 {unassigned_group}")
            total_unassigned += unassigned_group.count
    else:
        print("✓ No unassigned recordings found")

    print()
    print("--- SUMMARY ---")
    total_recordings = assigned_recordings + total_unassigned
    print(f"Total recordings: {total_recordings}")
    print(f"  - In folders: {assigned_recordings}")
    print(f"  - Unassigned: {total_unassigned}")
    
    if total_unassigned > 0:
        print(f"  - Unassigned percentage: {(total_unassigned/total_recordings)*100:.1f}%")
    
    # Check for any folder IDs in usage that aren't in folders table
    orphaned_folder_ids = set(usage.keys()) - set(folders.keys()) - {None, 0}
    if orphaned_folder_ids:
        print(f"\n⚠️  Found recordings assigned to non-existent folder IDs: {orphaned_folder_ids}")
        for orphaned_id in orphaned_folder_ids:
            if orphaned_id is not None and orphaned_id > 0:
                print(f"    Folder ID {orphaned_id}: {usage[orphaned_id]} recordings")


# Example usage functions
def example_usage_patterns(db_path: str):
    """
    Demonstrates different ways to work with unassigned recordings.
    """
    
    print("=== EXAMPLE USAGE PATTERNS ===\n")
    
    # Method 1: Quick check for unassigned recordings
    print("1. Quick unassigned check:")
    unassigned_list, total_count = get_unassigned_recordings_direct(db_path)
    
    if total_count > 0:
        print(f"   ⚠️  Found {total_count} unassigned recordings")
        for group in unassigned_list:
            print(f"   - {group}")
    else:
        print("   ✓ All recordings are properly assigned to folders")
    
    print()
    
    # Method 2: Get detailed information about unassigned recordings
    print("2. Detailed unassigned recording info:")
    unassigned_details = list_unassigned_recording_details(db_path)
    
    if unassigned_details:
        print(f"   Found {len(unassigned_details)} unassigned recordings:")
        for i, recording in enumerate(unassigned_details[:3]):  # Show first 3
            print(f"   [{i+1}] '{recording['name']}'")
            print(f"       Duration: {recording['duration']:.1f}s")
            print(f"       Date: {recording['formatted_date']}")
            print(f"       Path: {recording['path']}")
            print(f"       Folder ID: {recording['folder_id']}")
        
        if len(unassigned_details) > 3:
            print(f"   ... and {len(unassigned_details) - 3} more")
    else:
        print("   ✓ No unassigned recordings found")
    
    print()
    
    # Method 3: Full analysis (what we had before)
    print("3. Full folder analysis:")
    print("   (This gives you the complete picture)")
    print_folder_analysis(db_path)


def check_for_unassigned_only(db_path: str) -> bool:
    """
    Simple boolean check: are there any unassigned recordings?
    
    Returns:
        True if there are unassigned recordings, False otherwise
        
    Usage:
        if check_for_unassigned_only(db_path):
            print("Need to handle unassigned recordings")
            # ... do something about it
    """
    
    _, total_count = get_unassigned_recordings_direct(db_path)
    return total_count > 0


if __name__ == "__main__":
    import sys
    db_p = get_db_path()
    globals()[sys.argv[1]](db_p)
