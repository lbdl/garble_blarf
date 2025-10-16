"""
cli implementaion for package:
    exposes:
        get_db_path() via example()
"""
import sys
from typing import Optional
import click
from .voice_memos_printer import VoiceMemosPrinter
from .voicememo_db import cli_get_db_path, cli_get_rec_path, get_schema
from .memo_data import get_memo_data
from .memo_organiser import MemoOrganiser
from .database import MemoDatabase, get_user_data_dir, ComparisonRecord
from pathlib import Path
from .transcriber import transcribe_file as transcribe_audio
from .model_config import TranscriptionModel, list_available_models, get_default_model
from .comparison import compare_transcriptions

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
def db_schema() -> None:
    get_schema()

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
def example() -> None:
    db_path = _get_db()
    VoiceMemosPrinter.example_usage_patterns(db_path)

@main.command()
def filetree() -> None:
    db_path = _get_db()
    records = get_memo_data(db_path)
    VoiceMemosPrinter.print_memo_files(records)

@main.command()
def test_transcribe() -> None:
    fp_base = cli_get_rec_path()
    testfile = "20180114 132606-76050490.m4a"
    testfile2 = "20170421 092405-852A1FFE.m4a"
    fp = fp_base / testfile
    fp2 = fp_base / testfile2
    res = transcribe_audio(str(fp2))
    print(f"{res}")

@main.command()
@click.option('--db-path', default=None, help='Path to transcription database')
def db_stats(db_path: Optional[str]) -> None:
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
@click.option('--limit', default=10, help='Maximum number of records to show, 0 = shoe all records')
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

        print(f"📤 Exporting transcriptions...")
        print(f"   Format: {export_format}")
        print(f"   Output: {output_dir}")
        print(f"   Database: {db_path}")
        print("=" * 70)

        # Export transcriptions
        stats = organiser.export_transcriptions(
            format=export_format,
            only_unexported=not export_all,
            force=force,
            status_filter=status
        )

        # Print summary
        print("\n" + "=" * 70)
        print(f"📊 Export Summary:")
        print(f"   Total: {stats['total']}")
        print(f"   Exported: {stats['exported']}")
        print(f"   Skipped: {stats['skipped']}")
        print(f"   Failed: {stats['failed']}")

        if stats['exported'] > 0:
            print(f"\n✅ Successfully exported {stats['exported']} files to {output_dir}")

    except Exception as e:
        print(f"❌ Export failed: {e}")


@main.command()
@click.option('--output', default='memo_transcriber_schema.er', help='Output file path for ERD')
@click.option('--render', is_flag=True, help='Also render to SVG/PNG if erd tool is available')
def generate_erd(output: str, render: bool) -> None:
    """Generate ERD (Entity Relationship Diagram) of the database schema."""
    try:
        # Use default database path for schema (doesn't need data)
        db = MemoDatabase()
        erd_path = db.generate_erd(output)

        print(f"📊 ERD markup generated: {erd_path}")

        if render:
            # Try to render with erd tool
            import subprocess
            try:
                # Try SVG first
                svg_path = erd_path.replace('.er', '.svg')
                result = subprocess.run(['erd', '-f', 'svg', '-i', erd_path, '-o', svg_path],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"🎨 SVG diagram rendered: {svg_path}")
                else:
                    print(f"⚠️  Could not render SVG: {result.stderr}")

                # Try PNG as fallback
                png_path = erd_path.replace('.er', '.png')
                result = subprocess.run(['erd', '-f', 'png', '-i', erd_path, '-o', png_path],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"🎨 PNG diagram rendered: {png_path}")
                else:
                    print(f"⚠️  Could not render PNG: {result.stderr}")

            except FileNotFoundError:
                print("⚠️  'erd' tool not found. Install with: brew install erd")
                print("   Or manually render with: erd -f svg -i schema.er -o schema.svg")
        else:
            print("💡 To render: erd -f svg -i schema.er -o schema.svg")
            print("   Install erd tool: brew install erd")

    except Exception as e:
        print(f"Error generating ERD: {e}")


@main.command()
@click.argument('uuid')
@click.option('--db-path', default=None, help='Path to transcription database')
def mark_reference(uuid: str, db_path: Optional[str]) -> None:
    """Mark a transcription as a reference (ground truth) for comparison."""
    if db_path is None:
        db_path = _get_default_transcription_db()

    try:
        db = MemoDatabase(db_path)

        # Check if transcription exists
        record = db.get_transcription(uuid)
        if not record:
            print(f"❌ No transcription found with UUID: {uuid}")
            return

        if record.status != 'success':
            print(f"⚠️  Warning: This transcription has status '{record.status}' (not 'success')")
            if not click.confirm("Mark as reference anyway?"):
                return

        db.mark_as_reference(uuid)
        print(f"✅ Marked as reference: {record.plain_title}")
        print(f"   UUID: {uuid}")

    except Exception as e:
        print(f"❌ Error: {e}")


@main.command()
@click.option('--db-path', default=None, help='Path to transcription database')
def list_references(db_path: Optional[str]) -> None:
    """List all reference transcriptions."""
    if db_path is None:
        db_path = _get_default_transcription_db()

    try:
        db = MemoDatabase(db_path)
        references = db.get_reference_transcriptions()

        if not references:
            print("No reference transcriptions found.")
            print("\nTo mark a transcription as reference:")
            print("  memo-transcriber mark-reference <uuid>")
            return

        print(f"Reference Transcriptions ({len(references)}):")
        print("=" * 70)

        for ref in references:
            duration_min = (ref.duration_seconds or 0) / 60.0
            word_count = len(ref.transcription.split())

            print(f"\n📌 {ref.plain_title}")
            print(f"   UUID: {ref.uuid}")
            print(f"   Folder: {ref.folder_name}")
            print(f"   Model: {ref.model_used or 'unknown'}")
            print(f"   Duration: {duration_min:.1f} min")
            print(f"   Word count: {word_count}")
            print(f"   Processed: {ref.processed_at}")

            # Show comparison count if any
            comparisons = db.get_comparisons_for_reference(ref.uuid)
            if comparisons:
                print(f"   Comparisons: {len(comparisons)}")

    except Exception as e:
        print(f"❌ Error: {e}")


@main.command()
@click.argument('reference_uuid')
@click.argument('hypothesis_uuid')
@click.option('--db-path', default=None, help='Path to transcription database')
@click.option('--notes', help='Optional notes about this comparison')
def compare(reference_uuid: str, hypothesis_uuid: str, db_path: Optional[str], notes: Optional[str]) -> None:
    """Compare two transcriptions and calculate accuracy metrics."""
    if db_path is None:
        db_path = _get_default_transcription_db()

    try:
        db = MemoDatabase(db_path)

        # Get both transcriptions
        reference = db.get_transcription(reference_uuid)
        hypothesis = db.get_transcription(hypothesis_uuid)

        if not reference:
            print(f"❌ Reference transcription not found: {reference_uuid}")
            return

        if not hypothesis:
            print(f"❌ Hypothesis transcription not found: {hypothesis_uuid}")
            return

        print(f"📊 Comparing transcriptions...")
        print(f"   Reference: {reference.plain_title} ({reference.model_used or 'unknown'})")
        print(f"   Hypothesis: {hypothesis.plain_title} ({hypothesis.model_used or 'unknown'})")
        print("=" * 70)

        # Run comparison
        results = compare_transcriptions(
            reference.transcription,
            hypothesis.transcription,
            normalize=True
        )

        # Display results
        print(f"\n📈 Accuracy Metrics:")
        print(f"   Word Error Rate (WER): {results['wer']:.2%}")
        print(f"   Character Error Rate (CER): {results['cer']:.2%}")
        print(f"\n📝 Edit Operations:")
        print(f"   Substitutions: {results['substitutions']}")
        print(f"   Deletions: {results['deletions']}")
        print(f"   Insertions: {results['insertions']}")
        print(f"   Total edits: {results['total_edits']}")
        print(f"\n📊 Word Counts:")
        print(f"   Reference: {results['word_count_ref']} words")
        print(f"   Hypothesis: {results['word_count_hyp']} words")
        print(f"   Difference: {results['word_count_diff']:+d} ({results['word_count_diff_pct']:+.1f}%)")
        print(f"\n🔍 Similarity Scores:")
        print(f"   Jaccard similarity: {results['jaccard_similarity']:.2%}")
        print(f"   Cosine similarity: {results['cosine_similarity']:.2%}")

        # Save to database
        comparison_record = ComparisonRecord(
            reference_uuid=reference_uuid,
            hypothesis_uuid=hypothesis_uuid,
            wer=results['wer'],
            cer=results['cer'],
            substitutions=results['substitutions'],
            deletions=results['deletions'],
            insertions=results['insertions'],
            total_edits=results['total_edits'],
            word_count_ref=results['word_count_ref'],
            word_count_hyp=results['word_count_hyp'],
            word_count_diff=results['word_count_diff'],
            word_count_diff_pct=results['word_count_diff_pct'],
            jaccard_similarity=results['jaccard_similarity'],
            cosine_similarity=results['cosine_similarity'],
            notes=notes
        )

        comparison_id = db.save_comparison(comparison_record)
        print(f"\n✅ Comparison saved (ID: {comparison_id})")

    except Exception as e:
        print(f"❌ Error: {e}")


@main.command()
@click.argument('reference_uuid')
@click.option('--db-path', default=None, help='Path to transcription database')
def comparison_summary(reference_uuid: str, db_path: Optional[str]) -> None:
    """Show comparison summary for a reference transcription, grouped by model."""
    if db_path is None:
        db_path = _get_default_transcription_db()

    try:
        db = MemoDatabase(db_path)

        # Get reference
        reference = db.get_transcription(reference_uuid)
        if not reference:
            print(f"❌ Reference transcription not found: {reference_uuid}")
            return

        print(f"📊 Comparison Summary for: {reference.plain_title}")
        print(f"   UUID: {reference_uuid}")
        print("=" * 70)

        # Get summary by model
        summary = db.get_comparison_summary_by_model(reference_uuid)

        if not summary:
            print("\nNo comparisons found for this reference.")
            print("\nTo compare transcriptions:")
            print("  memo-transcriber compare <reference-uuid> <hypothesis-uuid>")
            return

        print(f"\nModel Performance (sorted by WER, lower is better):")
        print("-" * 70)

        for model_stats in summary:
            model = model_stats['model_used'] or 'unknown'
            count = model_stats['comparison_count']
            avg_wer = model_stats['avg_wer']
            min_wer = model_stats['min_wer']
            max_wer = model_stats['max_wer']
            avg_cer = model_stats['avg_cer']
            avg_jaccard = model_stats['avg_jaccard']
            avg_cosine = model_stats['avg_cosine']

            print(f"\n🤖 {model} ({count} comparison{'s' if count != 1 else ''})")
            print(f"   WER: {avg_wer:.2%} (min: {min_wer:.2%}, max: {max_wer:.2%})")
            print(f"   CER: {avg_cer:.2%}")
            print(f"   Jaccard similarity: {avg_jaccard:.2%}")
            print(f"   Cosine similarity: {avg_cosine:.2%}")

        # Find best model
        best_model = summary[0]
        print("\n" + "=" * 70)
        print(f"🏆 Best performing model: {best_model['model_used']} (WER: {best_model['avg_wer']:.2%})")

    except Exception as e:
        print(f"❌ Error: {e}")


# Load development commands if in dev mode
import os
if os.getenv('MEMO_DEV_MODE') or os.path.exists('.dev') or os.path.exists('pyproject.toml'):
    try:
        from .dev_commands import register_dev_commands
        register_dev_commands(main)
    except ImportError:
        pass  # Dev commands not available in production build

