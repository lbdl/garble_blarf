"""
VoiceMemosPrinter - Helper class for printing Voice Memos database data in a formatted way.
"""

from typing import Dict, List
from .memo_data import analyze_folder_usage, get_unassigned_recordings, list_unassigned_recording_details
from .memo_data import VoiceMemoFile, VoiceMemoFolder, UnassignedRecordings

class VoiceMemosPrinter:
    """Helper class for printing Voice Memos database data in a formatted way."""

    @staticmethod
    def print_memo_files(memo_files: List['VoiceMemoFile']) -> None:
        """Print all voice memo files with their details."""
        if not memo_files:
            print("📁 No memo files found.")
            return

        print(f"🎙️  Found {len(memo_files)} voice memo files:")
        print("=" * 70)
        print()

        for i, memo in enumerate(memo_files, 1):
            print(f"[{i:3d}] 🎵 {memo.plain_title}")
            print(f"      📁 Folder: {memo.memo_folder}")
            print(f"      🆔 UUID: {memo.uuid}")
            print(f"      📄 Path: {memo.f_path}")
            print("-" * 70)

    @staticmethod
    def print_folders(folders: Dict[int, 'VoiceMemoFolder']) -> None:
        """Print folder structure."""
        if not folders:
            print("No folders found.")
            return

        print(f"Found {len(folders)} folders:")
        print("-" * 50)

        for folder in folders.values():
            print(folder)

    @staticmethod
    def print_unassigned_recordings(unassigned: List['UnassignedRecordings']) -> None:
        """Print unassigned recordings summary."""
        if not unassigned:
            print("No unassigned recordings found.")
            return

        total_count = sum(group.count for group in unassigned)
        print(f"Found {total_count} unassigned recordings:")
        print("-" * 40)

        for group in unassigned:
            print(group)

    @staticmethod
    def print_folder_analysis(db_path: str) -> None:
        """Print comprehensive folder structure analysis."""
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

    @staticmethod
    def example_usage_patterns(db_path: str) -> None:
        """Demonstrate different ways to work with unassigned recordings."""
        print("=== EXAMPLE USAGE PATTERNS ===\n")

        # Method 1: Get detailed information about unassigned recordings
        print("1. Detailed unassigned recording info:")
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

        # Method 2: Full analysis (what we had before)
        print("2. Full folder analysis:")
        print("   (This gives you the complete picture)")
        VoiceMemosPrinter.print_folder_analysis(db_path)
