"""
Development and testing commands for memo transcriber.
This module is excluded from production builds.
"""

import click
from .voicememo_db import cli_get_db_path
from .memo_data import get_memo_data
from .memo_organiser import MemoOrganiser
from .database import MemoDatabase, get_user_data_dir


def _get_db():
    """Helper to get database path (duplicated from cli.py for dev isolation)."""
    db_path = cli_get_db_path()
    if not db_path[0]:
        print(f"{db_path[1]}")
        import sys
        sys.exit(1)
    else:
        return str(db_path[1])


def register_dev_commands(main_group):
    """Register development commands with the main CLI group."""

    @main_group.command()
    @click.option('--limit', default=2, help='Number of files to test with')
    @click.option('--max-duration', default=1.0, help='Skip files longer than this many minutes')
    def test_db(limit, max_duration):
        """[DEV] Test database integration with a small batch of files."""
        db_path = _get_db()
        memo_files = get_memo_data(db_path)

        print(f"🧪 Testing database integration with {limit} files (max {max_duration} min duration)")

        # Take just a few files for testing
        test_files = memo_files[:limit]

        if not test_files:
            print("No files found to test with")
            return

        print(f"Selected files:")
        for i, memo in enumerate(test_files, 1):
            duration_min = memo.duration_seconds / 60.0
            print(f"  {i}. {memo.plain_title} ({duration_min:.1f} min)")

        # Use a test database file in user data directory
        test_db_path = get_user_data_dir() / 'test_memo_transcriptions.db'
        organiser = MemoOrganiser(db_path=str(test_db_path))

        print(f"📁 Voice Memos DB: {db_path}")
        print(f"🧪 Test DB: {test_db_path}")

        print("\nProcessing files...")
        results = organiser.organise_memos(test_files, transcribe=True, max_duration_minutes=max_duration)

        # Show results
        print(f"\nResults:")
        for result in results:
            status_emoji = "✅" if result.status == "success" else "❌" if result.status == "failed" else "⏭️"
            print(f"  {status_emoji} {result.status}: {result.plain_title}")
            if result.status == 'success':
                print(f"    Transcript: {result.transcription[:100]}...")

        # Show database stats
        stats = organiser.db.get_processing_stats()
        print(f"\nDatabase stats: {stats}")

        print(f"\n✨ Test complete! Run 'memo-transcriber test-db --limit {limit}' again to see caching in action.")

    @main_group.command()
    @click.option('--db-path', default=None, help='Path to test database')
    def dev_db_stats(db_path):
        """[DEV] Show test database statistics."""
        if db_path is None:
            db_path = get_user_data_dir() / 'test_memo_transcriptions.db'

        try:
            db = MemoDatabase(str(db_path))
            stats = db.get_processing_stats()

            print(f"🗄️  Test Database: {db_path}")
            print("=" * 50)

            # Transcription statistics
            if 'transcriptions' in stats and stats['transcriptions']:
                print("\nTranscription Summary:")
                for status, data in stats['transcriptions'].items():
                    count = data['count']
                    avg_time = data.get('avg_time', 0) or 0
                    total_duration = data.get('total_duration', 0) or 0
                    print(f"  {status.capitalize()}: {count} files")
                    if avg_time > 0:
                        print(f"    Avg processing time: {avg_time:.2f}s")
                    if total_duration > 0:
                        print(f"    Total audio duration: {total_duration/60:.1f} minutes")
            else:
                print("\nNo transcriptions found in test database")

            # Get unexported count
            unexported = db.get_unexported_transcriptions()
            if unexported:
                print(f"\nUnexported transcriptions: {len(unexported)} files ready for export")

        except Exception as e:
            print(f"Error reading test database: {e}")

    @main_group.command()
    def dev_clean():
        """[DEV] Clean up test databases and temporary files."""
        import os
        import glob

        # Clean from user data directory
        user_data = get_user_data_dir()
        test_files = [
            user_data / 'test_memo_transcriptions.db',
            user_data / 'test_memo_transcriptions.db-journal'
        ]

        # Also clean current directory (legacy)
        test_files.extend([
            'test_memo_transcriptions.db',
            'test_memo_transcriptions.db-journal'
        ])

        cleaned = []
        for file_path in test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned.append(str(file_path))
            except OSError as e:
                print(f"Could not remove {file_path}: {e}")

        if cleaned:
            print("🧹 Cleaned up test files:")
            for file_path in cleaned:
                print(f"  - {file_path}")
        else:
            print("No test files to clean up")

    print("🔧 Development commands loaded")