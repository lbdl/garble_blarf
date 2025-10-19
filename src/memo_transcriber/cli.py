"""
cli implementaion for package:
    exposes:
        get_db_path() via example()
"""
import sys
from typing import Optional
import click
from .voicememo_db import cli_get_db_path
from .memo_data import get_memo_data
from .memo_organiser import MemoOrganiser
from .database import MemoDatabase, get_user_data_dir
from .model_config import TranscriptionModel, list_available_models, get_default_model
from .voice_memos_printer import VoiceMemosPrinter
from .cli_output import CliPrinter, OutputStyle

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

@click.group()
def main() -> None:
    pass

@main.command()
def list_models() -> None:
    """List all available transcription models."""
    from .model_config import MODEL_INFO

    print("Available Transcription Models:")
    print("=" * 70)

    for model, info in MODEL_INFO.items():
        print(f"\n🤖 {model.value}")
        print(f"   Name: {info.display_name}")
        print(f"   Engine: {info.engine}")
        print(f"   Speed: {info.relative_speed}")
        print(f"   Accuracy: {info.relative_accuracy}")
        print(f"   Description: {info.description}")

    print("\n" + "=" * 70)
    print(f"Default model: {get_default_model().value}")
    print("\nUsage: memo-transcriber organise --model <model-name>")

@main.command()
def filetree() -> None:
    """Display memo file structure and organization."""
    db_path = _get_db()
    records = get_memo_data(db_path)
    VoiceMemosPrinter.print_memo_files(records)

@main.command()
@click.option('--db-path', default=None, help='Path to transcription database')
def db_stats(db_path: Optional[str]) -> None:
    """Show database statistics and processing history."""
    if db_path is None:
        db_path = _get_default_transcription_db()

    try:
        db = MemoDatabase(db_path)
        stats = db.get_processing_stats()

        CliPrinter.section_start(f"Database: {db_path}", OutputStyle.STATS)

        # Transcription statistics
        if 'transcriptions' in stats and stats['transcriptions']:
            CliPrinter.blank_line()
            CliPrinter.info("Transcription Summary:")
            for status, data in stats['transcriptions'].items():
                count = data['count']
                avg_time = data.get('avg_time', 0) or 0
                total_duration = data.get('total_duration', 0) or 0
                CliPrinter.kv(f"{status.capitalize()}", f"{count} files", indent_level=1)
                if avg_time > 0:
                    CliPrinter.kv("Avg processing time", f"{avg_time:.2f}s", indent_level=2)
                if total_duration > 0:
                    CliPrinter.kv("Total audio duration", f"{total_duration/60:.1f} minutes", indent_level=2)
        else:
            CliPrinter.blank_line()
            CliPrinter.info("No transcriptions found in database")

        # Export statistics
        if 'exports' in stats and stats['exports']:
            CliPrinter.blank_line()
            CliPrinter.info("Export Summary:")
            for status, data in stats['exports'].items():
                count = data['count']
                CliPrinter.kv(f"{status.capitalize()}", f"{count} files", indent_level=1)
        else:
            CliPrinter.blank_line()
            CliPrinter.info("No exports recorded yet")

        # Get unexported count
        unexported = db.get_unexported_transcriptions()
        if unexported:
            CliPrinter.blank_line()
            CliPrinter.info(f"Unexported transcriptions: {len(unexported)} files ready for export")

    except Exception as e:
        CliPrinter.error("Error reading database", e)

@main.command()
@click.option('--db-path', default=None, help='Path to transcription database')
@click.option('--status', help='Filter by status (success, failed, skipped)')
@click.option('--limit', default=10, help='Maximum number of records to show, 0 = show all records')
@click.option('--compact', is_flag=True, help='Show compact view with just title and status')
def list_cached(db_path: Optional[str], status: Optional[str], limit: int, compact: bool) -> None:
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

        # Limit results 0 == show all
        if len(records) > limit and limit != 0:
            print(f"Showing first {limit} of {len(records)} records (use --limit to see more)")
            records = records[:limit]

        if compact:
            # Compact view: just title (or first 5 words if untitled) and status
            print(f"Cached Transcriptions ({len(records)} records):")
            print("=" * 70)

            for record in records:
                # Check if title is generic "New Recording X" pattern
                is_untitled = record.plain_title.startswith("New Recording")

                if is_untitled and record.status == 'success' and record.transcription:
                    # Show first ~5 words of transcription
                    words = record.transcription.split()[:5]
                    display_title = ' '.join(words) + ('...' if len(record.transcription.split()) > 5 else '')
                else:
                    display_title = record.plain_title

                # Status emoji
                status_emoji = {
                    'success': '✅',
                    'failed': '❌',
                    'skipped': '⏭️'
                }.get(record.status, '❓')

                print(f"{status_emoji} {display_title} [{record.status}]")
        else:
            # Detailed view
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
@click.option('--model', default=None, help='Transcription model (apple, whisper-base, faster-whisper-base, etc.)')
def organise(transcribe: bool, folder: Optional[str], max_duration: float, db_path: Optional[str], model: Optional[str]) -> None:
    """Organise voice memos with transcriptions."""
    voice_memos_db = _get_db()
    memo_files = get_memo_data(voice_memos_db)

    if db_path is None:
        db_path = _get_default_transcription_db()

    # Parse model selection
    transcription_model = None
    if model:
        try:
            transcription_model = TranscriptionModel(model)
        except ValueError:
            print(f"❌ Invalid model: {model}")
            print("\nAvailable models:")
            for model_name, display_name in list_available_models():
                print(f"  - {model_name}: {display_name}")
            sys.exit(1)
    else:
        # set in model_config.py
        transcription_model = get_default_model()

    print(f"📁 Voice Memos DB: {voice_memos_db}")
    print(f"💾 Transcription DB: {db_path}")
    print(f"🤖 Model: {transcription_model.value}")

    organiser = MemoOrganiser(db_path=db_path)
    organised = organiser.organise_memos(memo_files, transcribe=transcribe, max_duration_minutes=max_duration, model=transcription_model)

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
@click.option('--format', 'export_format', default='md', type=click.Choice(['txt', 'md', 'json']), help='Export format (default: md)')
@click.option('--output-dir', default='Documents/transcriptions', help='Output directory for exported files')
@click.option('--all', 'export_all', is_flag=True, help='Export all transcriptions, not just unexported')
@click.option('--force', is_flag=True, help='Overwrite existing files even if unchanged')
@click.option('--status', default='success', help='Filter by status (success, failed, skipped)')
@click.option('--db-path', default=None, help='Path to transcription database')
def export(export_format: str, output_dir: str, export_all: bool, force: bool, status: str, db_path: Optional[str]) -> None:
    """Export transcriptions to files on disk."""
    if db_path is None:
        db_path = _get_default_transcription_db()

    try:
        # Initialize organiser with output directory
        organiser = MemoOrganiser(output=output_dir, db_path=db_path)

        CliPrinter.header("Exporting transcriptions...", OutputStyle.EXPORT)
        CliPrinter.kv("Format", export_format)
        CliPrinter.kv("Output", output_dir)
        CliPrinter.kv("Database", db_path)
        CliPrinter.separator()

        # Export transcriptions
        stats = organiser.export_transcriptions(
            format=export_format,
            only_unexported=not export_all,
            force=force,
            status_filter=status
        )

        # Print summary
        CliPrinter.blank_line()
        CliPrinter.separator()
        CliPrinter.header("Export Summary:", OutputStyle.STATS)
        CliPrinter.kv("Total", stats['total'])
        CliPrinter.kv("Exported", stats['exported'])
        CliPrinter.kv("Skipped", stats['skipped'])
        CliPrinter.kv("Failed", stats['failed'])

        if stats['exported'] > 0:
            CliPrinter.blank_line()
            CliPrinter.success(f"Successfully exported {stats['exported']} files to {output_dir}")

    except Exception as e:
        CliPrinter.error("Export failed", e)


# Load development commands if in dev mode
import os
if os.getenv('MEMO_DEV_MODE') or os.path.exists('.dev') or os.path.exists('pyproject.toml'):
    try:
        from .dev_commands import register_dev_commands
        register_dev_commands(main)
    except ImportError:
        pass  # Dev commands not available in production build

