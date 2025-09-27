"""
cli implementaion for package:
    exposes:
        get_db_path() via example()
"""
import sys
import click
from .voice_memos_printer import VoiceMemosPrinter
from .voicememo_db import cli_get_db_path, cli_get_rec_path, get_schema
from .memo_data import get_memo_data
from .memo_organiser import MemoOrganiser
from .database import MemoDatabase, get_user_data_dir
from pathlib import Path
from .transcriber import transcribe_file as transcribe_audio

def _get_db():
    """Get Voice Memos database path."""
    db_path = cli_get_db_path()
    if not db_path[0]:
        print(f"{db_path[1]}")
        sys.exit(1)
    else:
        return str(db_path[1])

def _get_default_transcription_db():
    """Get default transcription database path."""
    return str(get_user_data_dir() / "memo_transcriptions.db")

@click.group
def main():
    pass

@main.command
def db_schema():
    get_schema()

@main.command
def example():
    db_path = _get_db()
    VoiceMemosPrinter.example_usage_patterns(db_path)

@main.command
def filetree():
    db_path = _get_db()
    records = get_memo_data(db_path)
    VoiceMemosPrinter.print_memo_files(records)

@main.command
def test_transcribe():
    fp_base = cli_get_rec_path()
    testfile = "20180114 132606-76050490.m4a"
    testfile2 = "20170421 092405-852A1FFE.m4a"
    fp = fp_base / testfile
    fp2 = fp_base / testfile2
    res = transcribe_audio(str(fp2))
    print(f"{res}")

@main.command()
@click.option('--db-path', default=None, help='Path to transcription database')
def db_stats(db_path):
    """Show database statistics and processing history."""
    if db_path is None:
        db_path = _get_default_transcription_db()

    try:
        db = MemoDatabase(db_path)
        stats = db.get_processing_stats()

        print(f"📊 Database: {db_path}")
        print("=" * 70)

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
            print("\nNo transcriptions found in database")

        # Export statistics
        if 'exports' in stats and stats['exports']:
            print("\nExport Summary:")
            for status, data in stats['exports'].items():
                count = data['count']
                print(f"  {status.capitalize()}: {count} files")
        else:
            print("\nNo exports recorded yet")

        # Get unexported count
        unexported = db.get_unexported_transcriptions()
        if unexported:
            print(f"\nUnexported transcriptions: {len(unexported)} files ready for export")

    except Exception as e:
        print(f"Error reading database: {e}")

@main.command()
@click.option('--db-path', default=None, help='Path to transcription database')
@click.option('--status', help='Filter by status (success, failed, skipped)')
@click.option('--limit', default=10, help='Maximum number of records to show')
def list_cached(db_path, status, limit):
    """List cached transcriptions from database."""
    if db_path is None:
        db_path = _get_default_transcription_db()

    try:
        db = MemoDatabase(db_path)
        records = db.get_all_transcriptions(status_filter=status)

        if not records:
            status_msg = f" with status '{status}'" if status else ""
            print(f"No transcriptions found{status_msg}")
            return

        # Limit results
        if len(records) > limit:
            print(f"Showing first {limit} of {len(records)} records (use --limit to see more)")
            records = records[:limit]

        print(f"Cached Transcriptions ({len(records)} records):")
        print("=" * 70)

        for record in records:
            duration_min = (record.duration_seconds or 0) / 60.0
            proc_time = record.processing_time_seconds or 0

            print(f"\n📝 {record.plain_title}")
            print(f"   UUID: {record.uuid}")
            print(f"   Folder: {record.folder_name}")
            print(f"   Status: {record.status}")
            print(f"   Duration: {duration_min:.1f} min")
            if proc_time > 0:
                print(f"   Processing time: {proc_time:.2f}s")
            if record.model_used:
                print(f"   Model: {record.model_used}")
            if record.processed_at:
                print(f"   Processed: {record.processed_at}")

            if record.status == 'success' and record.transcription:
                preview = record.transcription[:100]
                print(f"   Preview: {preview}{'...' if len(record.transcription) > 100 else ''}")
            elif record.status == 'failed' and record.error_message:
                print(f"   Error: {record.error_message}")

    except Exception as e:
        print(f"Error reading database: {e}")

@main.command()
@click.option('--transcribe/--no-transcribe', default=True, help='Whether to transcribe audio files')
@click.option('--folder', help='Filter by specific folder')
@click.option('--max-duration', default=8.0, help='Skip files longer than this many minutes')
@click.option('--db-path', default=None, help='Path to transcription database')
def organise(transcribe, folder, max_duration, db_path):
    """Organise voice memos with transcriptions."""
    voice_memos_db = _get_db()
    memo_files = get_memo_data(voice_memos_db)

    if db_path is None:
        db_path = _get_default_transcription_db()

    print(f"📁 Voice Memos DB: {voice_memos_db}")
    print(f"💾 Transcription DB: {db_path}")

    organiser = MemoOrganiser(db_path=db_path)
    organised = organiser.organise_memos(memo_files, transcribe=transcribe, max_duration_minutes=max_duration)

    # Filter by folder if specified
    if folder:
        organised = [memo for memo in organised if memo.folder == folder]

    # Print results
    for memo in organised:
        print(f"📝 {memo.plain_title}")
        print(f"   Status: {memo.status}")
        print(f"   Folder: {memo.folder}")
        if memo.status == 'success':
            print(f"   Transcript: {memo.transcription[:100]}...")
        elif memo.status == 'failed':
            print(f"   Error: {memo.transcription}")
        print()

    # Print summary
    summary = organiser.get_transcription_summary(organised)
    print(f"Summary: {summary['success']} success, {summary['failed']} failed, {summary['skipped']} skipped")

@main.command()
def check_duration():
    """Check ZDURATION values to understand the units."""
    db_path = _get_db()
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            ZCUSTOMLABEL as title,
            ZDURATION as duration_raw,
            ZDATE as date_timestamp
        FROM ZCLOUDRECORDING
        WHERE ZDURATION IS NOT NULL
        ORDER BY ZDURATION DESC
        LIMIT 10
    """)

    print("Sample ZDURATION values from database:")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"Title: {row['title'] or 'Untitled'}")
        print(f"ZDURATION: {row['duration_raw']}")
        print(f"Date: {row['date_timestamp']}")
        print("-" * 30)

    conn.close()


# Load development commands if in dev mode
import os
if os.getenv('MEMO_DEV_MODE') or os.path.exists('.dev') or os.path.exists('pyproject.toml'):
    try:
        from .dev_commands import register_dev_commands
        register_dev_commands(main)
    except ImportError:
        pass  # Dev commands not available in production build

