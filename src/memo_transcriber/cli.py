"""
cli implementaion for package:
    exposes:
        get_db_path() via example()
"""
import sys
import click
from .voice_memos_printer import VoiceMemosPrinter
from .voicememo_db import cli_get_db_path, cli_get_rec_path
from .memo_data import get_memo_data
from .memo_organiser import MemoOrganiser
from pathlib import Path
from .transcriber import transcribe_file as transcribe_audio

def _get_db():
    db_path = cli_get_db_path()
    if not db_path[0]:
        print(f"{db_path[1]}")
        sys.exit(1)
    else:
        return str(db_path[1])

@click.group
def main():
    pass

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
def transcribe_file():
    fp_base = cli_get_rec_path()
    testfile = "20180114 132606-76050490.m4a"
    testfile2 = "20170421 092405-852A1FFE.m4a"
    fp = fp_base / testfile
    fp2 = fp_base / testfile2
    res = transcribe_audio(str(fp2))
    print(f"{res}")

@main.command()
@click.option('--transcribe/--no-transcribe', default=True, help='Whether to transcribe audio files')
@click.option('--folder', help='Filter by specific folder')
@click.option('--max-duration', default=8.0, help='Skip files longer than this many minutes')
def organise(transcribe, folder, max_duration):
    """Organise voice memos with transcriptions."""
    db_path = _get_db()
    memo_files = get_memo_data(db_path)

    organiser = MemoOrganiser()
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

