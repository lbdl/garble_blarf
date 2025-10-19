"""
Development and testing commands for memo transcriber.
This module is excluded from production builds.
"""

from typing import Optional
import click
from .voicememo_db import cli_get_db_path, cli_get_rec_path, get_schema
from .memo_data import get_memo_data
from .memo_organiser import MemoOrganiser
from .database import MemoDatabase, get_user_data_dir, ComparisonRecord
from .voice_memos_printer import VoiceMemosPrinter
from .transcriber import transcribe_file as transcribe_audio
from .comparison import compare_transcriptions
from .cli_output import CliPrinter, OutputStyle
from .printer import Printer


def _get_db() -> str:
    """Helper to get Voice Memos database path."""
    db_path = cli_get_db_path()
    if not db_path[0]:
        print(f"{db_path[1]}")
        import sys
        sys.exit(1)
    else:
        return str(db_path[1])


def _get_default_transcription_db() -> str:
    """Get default transcription database path."""
    return str(get_user_data_dir() / "memo_transcriptions.db")


def register_dev_commands(main_group: click.Group) -> None:
    """Register development commands with the main CLI group."""
    @main_group.command()
    def check_duration() -> None:
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

    @main_group.command()
    @click.option('--limit', default=2, help='Number of files to test with')
    @click.option('--max-duration', default=1.0, help='Skip files longer than this many minutes')
    def test_db(limit: int, max_duration: float) -> None:
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
    def dev_db_stats(db_path: Optional[str]) -> None:
        """[DEV] Show test database statistics."""
        if db_path is None:
            db_path = get_user_data_dir() / 'test_memo_transcriptions.db'

        try:
            db = MemoDatabase(str(db_path))
            stats = db.get_processing_stats()

            # Print header with DATABASE emoji
            Printer.print_db_stats_header(str(db_path), emoji=OutputStyle.DATABASE)

            # Print transcription statistics
            Printer.print_transcription_stats(stats)

            # Print unexported count
            unexported = db.get_unexported_transcriptions()
            Printer.print_unexported_count(len(unexported))

        except Exception as e:
            CliPrinter.error("Error reading test database", e)

    @main_group.command()
    def dev_clean() -> None:
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

    # === Inspection Commands ===

    @main_group.command()
    def db_schema() -> None:
        """[DEV] Show Voice Memos database schema."""
        get_schema()

    @main_group.command()
    def example() -> None:
        """[DEV] Show example usage patterns from Voice Memos DB."""
        db_path = _get_db()
        VoiceMemosPrinter.example_usage_patterns(db_path)

    @main_group.command()
    def test_transcribe() -> None:
        """[DEV] Test transcription with hardcoded files."""
        fp_base = cli_get_rec_path()
        testfile = "20180114 132606-76050490.m4a"
        testfile2 = "20170421 092405-852A1FFE.m4a"
        fp = fp_base / testfile
        fp2 = fp_base / testfile2
        res = transcribe_audio(str(fp2))
        print(f"{res}")

    @main_group.command()
    @click.option('--output', default='memo_transcriber_schema.er', help='Output file path for ERD')
    @click.option('--render', is_flag=True, help='Also render to SVG/PNG if erd tool is available')
    def generate_erd(output: str, render: bool) -> None:
        """[DEV] Generate ERD (Entity Relationship Diagram) of the database schema."""
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

    # === Legacy Comparison Commands (BROKEN - see database.py ComparisonRecord) ===

    @main_group.command()
    @click.argument('uuid')
    @click.option('--db-path', default=None, help='Path to transcription database')
    def mark_reference(uuid: str, db_path: Optional[str]) -> None:
        """[DEV/LEGACY] Mark a transcription as a reference (ground truth) for comparison.

        ⚠️  WARNING: This uses the old transcriptions table. Use 'comparator' CLI instead.
        """
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

    @main_group.command()
    @click.option('--db-path', default=None, help='Path to transcription database')
    def list_references(db_path: Optional[str]) -> None:
        """[DEV/LEGACY] List all reference transcriptions.

        ⚠️  WARNING: This uses the old transcriptions table. Use 'comparator' CLI instead.
        """
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

    @main_group.command()
    @click.argument('reference_uuid')
    @click.argument('hypothesis_uuid')
    @click.option('--db-path', default=None, help='Path to transcription database')
    @click.option('--notes', help='Optional notes about this comparison')
    def compare(reference_uuid: str, hypothesis_uuid: str, db_path: Optional[str], notes: Optional[str]) -> None:
        """[DEV/LEGACY] Compare two transcriptions and calculate accuracy metrics.

        ⚠️  WARNING: BROKEN - ComparisonRecord expects integer IDs, not UUIDs.
        Use 'comparator' CLI instead.
        """
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

            # Save to database - NOTE: This will likely fail due to ComparisonRecord expecting IDs not UUIDs
            print("\n⚠️  WARNING: Attempting to save (this may fail due to schema mismatch)")
            comparison_record = ComparisonRecord(
                reference_id=reference_uuid,  # WRONG: expects int, not UUID string
                hypothesis_id=hypothesis_uuid,  # WRONG: expects int, not UUID string
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

    @main_group.command()
    @click.argument('reference_uuid')
    @click.option('--db-path', default=None, help='Path to transcription database')
    def comparison_summary(reference_uuid: str, db_path: Optional[str]) -> None:
        """[DEV/LEGACY] Show comparison summary for a reference transcription, grouped by model.

        ⚠️  WARNING: Depends on broken 'compare' command. Use 'comparator' CLI instead.
        """
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

    print("🔧 Development commands loaded")
