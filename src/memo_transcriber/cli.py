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
from .cli_output import CliPrinter
from .printer import Printer

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

    Printer.print_models_list(MODEL_INFO, get_default_model())

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

        # Print header
        Printer.print_db_stats_header(db_path)

        # Print transcription statistics
        Printer.print_transcription_stats(stats)

        # Print export statistics
        Printer.print_export_stats(stats)

        # Print unexported count
        unexported = db.get_unexported_transcriptions()
        Printer.print_unexported_count(len(unexported))

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
            Printer.print_no_transcriptions_found(status)
            return

        # Limit results 0 == show all
        if len(records) > limit and limit != 0:
            Printer.print_list_limit_message(limit, len(records))
            records = records[:limit]

        # Print the list of cached transcriptions
        Printer.print_cached_list(records, compact=compact)

    except Exception as e:
        CliPrinter.error("Error reading database", e)

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
            Printer.print_invalid_model_error(model, list_available_models())
            sys.exit(1)
    else:
        # set in model_config.py
        transcription_model = get_default_model()

    # Print header
    Printer.print_organise_header(voice_memos_db, db_path, transcription_model.value)

    organiser = MemoOrganiser(db_path=db_path)
    organised = organiser.organise_memos(memo_files, transcribe=transcribe, max_duration_minutes=max_duration, model=transcription_model)

    # Filter by folder if specified
    if folder:
        organised = [memo for memo in organised if memo.folder == folder]

    # Print results
    for memo in organised:
        Printer.print_organised_memo(memo)

    # Print summary
    summary = organiser.get_transcription_summary(organised)
    Printer.print_organise_summary(summary)

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

        # Print header
        Printer.print_export_header(export_format, output_dir, db_path)

        # Export transcriptions
        stats = organiser.export_transcriptions(
            format=export_format,
            only_unexported=not export_all,
            force=force,
            status_filter=status
        )

        # Print summary
        Printer.print_export_summary(stats, output_dir)

    except Exception as e:
        Printer.print_export_error(e)

