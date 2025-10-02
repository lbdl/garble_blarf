"""
Comparator CLI - Tool for comparing transcription models.

Allows transcribing the same voice memo with multiple models and comparing accuracy.
"""
import sys
import time
from typing import Optional, List
import click
from pathlib import Path
from .database import MemoDatabase, ModelTranscriptionRecord, ComparisonRecord
from .voicememo_db import cli_get_db_path, cli_get_rec_path
from .memo_data import get_memo_data
from .transcriber import transcribe_file
from .model_config import TranscriptionModel, list_available_models
from .comparison import compare_transcriptions


def _get_db():
    """Get Voice Memos database path."""
    db_path = cli_get_db_path()
    if not db_path[0]:
        print(f"{db_path[1]}")
        sys.exit(1)
    else:
        return str(db_path[1])


@click.group()
def main() -> None:
    """Comparator - Multi-model transcription comparison tool."""
    pass


@main.command()
@click.argument('memo_uuid')
@click.option('--models', required=True, help='Comma-separated list of models (e.g., whisper-base,faster-whisper-base)')
def transcribe_models(memo_uuid: str, models: str) -> None:
    """Transcribe a memo with multiple models for comparison."""
    # Parse models
    model_list = [m.strip() for m in models.split(',')]

    # Validate models
    available = [m[0] for m in list_available_models()]
    for model_name in model_list:
        if model_name not in available:
            print(f"❌ Invalid model: {model_name}")
            print(f"\nAvailable models: {', '.join(available)}")
            sys.exit(1)

    # Get memo data from Voice Memos database
    voice_db_path = _get_db()
    memo_files = get_memo_data(voice_db_path)

    # Find the memo
    memo = None
    for m in memo_files:
        if m.uuid == memo_uuid:
            memo = m
            break

    if not memo:
        print(f"❌ Memo not found: {memo_uuid}")
        sys.exit(1)

    print(f"📝 {memo.plain_title}")
    print(f"   UUID: {memo_uuid}")
    print(f"   Duration: {memo.duration_seconds:.1f}s")
    print(f"   Models: {', '.join(model_list)}")
    print("=" * 70)

    # Get recordings path
    recordings_path = cli_get_rec_path()
    audio_file = recordings_path / memo.file_path

    if not audio_file.exists():
        print(f"❌ Audio file not found: {audio_file}")
        sys.exit(1)

    # Initialize database
    db = MemoDatabase()
    file_hash = db.get_file_hash(str(audio_file))

    # Transcribe with each model
    for model_name in model_list:
        # Check if already transcribed
        existing = db.get_model_transcription_by_model(memo_uuid, model_name)
        if existing and existing.file_hash == file_hash:
            print(f"\n⏭️  {model_name}: Already transcribed (skipping)")
            continue

        print(f"\n🤖 Transcribing with {model_name}...")
        model = TranscriptionModel(model_name)

        start_time = time.time()
        try:
            transcription = transcribe_file(str(audio_file), model=model)
            processing_time = time.time() - start_time

            # Save to database
            record = ModelTranscriptionRecord(
                memo_uuid=memo_uuid,
                model_used=model_name,
                transcription=transcription,
                status='success',
                processing_time_seconds=processing_time,
                file_hash=file_hash,
                plain_title=memo.plain_title,
                folder_name=memo.folder,
                file_path=memo.file_path,
                duration_seconds=memo.duration_seconds,
                recording_date=memo.recording_date
            )

            trans_id = db.save_model_transcription(record)

            print(f"   ✅ Success (ID: {trans_id})")
            print(f"   Time: {processing_time:.2f}s")
            print(f"   Preview: {transcription[:80]}...")

        except Exception as e:
            processing_time = time.time() - start_time

            # Save error to database
            record = ModelTranscriptionRecord(
                memo_uuid=memo_uuid,
                model_used=model_name,
                transcription='',
                status='failed',
                error_message=str(e),
                processing_time_seconds=processing_time,
                file_hash=file_hash,
                plain_title=memo.plain_title,
                folder_name=memo.folder,
                file_path=memo.file_path,
                duration_seconds=memo.duration_seconds,
                recording_date=memo.recording_date
            )

            db.save_model_transcription(record)

            print(f"   ❌ Failed: {e}")

    print("\n" + "=" * 70)
    print("✅ Transcription complete")


@main.command()
@click.argument('memo_uuid')
def list_transcriptions(memo_uuid: str) -> None:
    """List all model transcriptions for a memo."""
    db = MemoDatabase()
    transcriptions = db.get_model_transcriptions_for_memo(memo_uuid)

    if not transcriptions:
        print(f"No transcriptions found for memo: {memo_uuid}")
        print("\nTo transcribe:")
        print(f"  comparator transcribe-models {memo_uuid} --models whisper-base,faster-whisper-base")
        return

    print(f"Transcriptions for memo: {memo_uuid}")
    print("=" * 70)

    for trans in transcriptions:
        ref_marker = " 📌 REFERENCE" if trans.is_reference else ""
        status_emoji = "✅" if trans.status == "success" else "❌"

        print(f"\n{status_emoji} {trans.model_used}{ref_marker}")
        print(f"   ID: {trans.id}")
        print(f"   Status: {trans.status}")

        if trans.processing_time_seconds:
            print(f"   Processing time: {trans.processing_time_seconds:.2f}s")

        if trans.status == 'success':
            word_count = len(trans.transcription.split())
            print(f"   Word count: {word_count}")
            print(f"   Preview: {trans.transcription[:80]}...")
        elif trans.error_message:
            print(f"   Error: {trans.error_message}")


@main.command()
@click.argument('memo_uuid')
@click.option('--text', help='Reference transcription text')
@click.option('--id', 'trans_id', type=int, help='Mark existing transcription as reference by ID')
def set_reference(memo_uuid: str, text: Optional[str], trans_id: Optional[int]) -> None:
    """Set reference (ground truth) transcription for a memo."""
    db = MemoDatabase()

    if text and trans_id:
        print("❌ Error: Specify either --text or --id, not both")
        sys.exit(1)

    if not text and not trans_id:
        print("❌ Error: Must specify either --text or --id")
        sys.exit(1)

    if trans_id:
        # Mark existing transcription as reference
        trans = db.get_model_transcription(trans_id)
        if not trans:
            print(f"❌ Transcription not found: ID {trans_id}")
            sys.exit(1)

        if trans.memo_uuid != memo_uuid:
            print(f"❌ Transcription ID {trans_id} does not belong to memo {memo_uuid}")
            sys.exit(1)

        db.mark_model_transcription_as_reference(trans_id)
        print(f"✅ Marked as reference: {trans.model_used} (ID: {trans_id})")
        print(f"   {trans.transcription[:100]}...")

    elif text:
        # Create new reference transcription
        # Get memo info
        voice_db_path = _get_db()
        memo_files = get_memo_data(voice_db_path)
        memo = None
        for m in memo_files:
            if m.uuid == memo_uuid:
                memo = m
                break

        if not memo:
            print(f"❌ Memo not found: {memo_uuid}")
            sys.exit(1)

        # Unmark any existing reference
        existing_ref = db.get_reference_for_memo(memo_uuid)
        if existing_ref:
            db.mark_model_transcription_as_reference(0)  # Unmark

        # Create new reference record
        record = ModelTranscriptionRecord(
            memo_uuid=memo_uuid,
            model_used='reference',
            transcription=text,
            status='success',
            is_reference=1,
            plain_title=memo.plain_title,
            folder_name=memo.folder,
            file_path=memo.file_path,
            duration_seconds=memo.duration_seconds,
            recording_date=memo.recording_date
        )

        trans_id = db.save_model_transcription(record)
        print(f"✅ Reference transcription created (ID: {trans_id})")
        print(f"   Word count: {len(text.split())}")
        print(f"   Preview: {text[:100]}...")


@main.command()
@click.argument('memo_uuid')
def compare_all(memo_uuid: str) -> None:
    """Compare all model transcriptions against the reference."""
    db = MemoDatabase()

    # Get reference
    reference = db.get_reference_for_memo(memo_uuid)
    if not reference:
        print(f"❌ No reference transcription set for memo: {memo_uuid}")
        print("\nTo set reference:")
        print(f"  comparator set-reference {memo_uuid} --text \"correct transcription\"")
        print(f"  comparator set-reference {memo_uuid} --id <transcription-id>")
        return

    # Get all transcriptions
    transcriptions = db.get_model_transcriptions_for_memo(memo_uuid)

    # Filter out reference
    hypotheses = [t for t in transcriptions if t.id != reference.id]

    if not hypotheses:
        print(f"No model transcriptions to compare for memo: {memo_uuid}")
        print("\nTo transcribe:")
        print(f"  comparator transcribe-models {memo_uuid} --models whisper-base,faster-whisper-base")
        return

    print(f"📊 Comparing against reference: {reference.model_used}")
    print(f"   ID: {reference.id}")
    print(f"   Words: {len(reference.transcription.split())}")
    print("=" * 70)

    # Compare each hypothesis
    for hyp in hypotheses:
        if hyp.status != 'success':
            print(f"\n⏭️  {hyp.model_used}: Skipped (status: {hyp.status})")
            continue

        print(f"\n🤖 {hyp.model_used} (ID: {hyp.id})")

        # Run comparison
        results = compare_transcriptions(
            reference.transcription,
            hyp.transcription,
            normalize=True
        )

        # Display results
        print(f"   WER: {results['wer']:.2%}")
        print(f"   CER: {results['cer']:.2%}")
        print(f"   Edits: {results['total_edits']} (S:{results['substitutions']} D:{results['deletions']} I:{results['insertions']})")
        print(f"   Words: {results['word_count_hyp']} ({results['word_count_diff']:+d})")
        print(f"   Jaccard: {results['jaccard_similarity']:.2%}")
        print(f"   Cosine: {results['cosine_similarity']:.2%}")

        # Save to database
        comparison = ComparisonRecord(
            reference_id=reference.id,
            hypothesis_id=hyp.id,
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
            cosine_similarity=results['cosine_similarity']
        )

        db.save_model_comparison(comparison)

    print("\n" + "=" * 70)
    print("✅ Comparison complete")


@main.command()
@click.argument('memo_uuid')
def show_results(memo_uuid: str) -> None:
    """Show comparison results for a memo."""
    db = MemoDatabase()

    # Get reference
    reference = db.get_reference_for_memo(memo_uuid)
    if not reference:
        print(f"❌ No reference transcription set for memo: {memo_uuid}")
        return

    # Get comparisons
    comparisons = db.get_comparisons_for_memo(memo_uuid)

    if not comparisons:
        print(f"No comparisons found for memo: {memo_uuid}")
        print("\nRun comparisons first:")
        print(f"  comparator compare-all {memo_uuid}")
        return

    print(f"📊 Comparison Results")
    print(f"   Memo: {memo_uuid}")
    print(f"   Reference: {reference.model_used} (ID: {reference.id})")
    print("=" * 70)

    # Collect results
    results = []
    for comp, ref_model, hyp_model in comparisons:
        results.append({
            'model': hyp_model,
            'wer': comp.wer,
            'cer': comp.cer,
            'jaccard': comp.jaccard_similarity,
            'cosine': comp.cosine_similarity
        })

    # Sort by WER (lower is better)
    results.sort(key=lambda x: x['wer'])

    print("\nModel Performance (sorted by WER):")
    print("-" * 70)

    for i, r in enumerate(results):
        rank_emoji = "🏆" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        print(f"\n{rank_emoji} {r['model']}")
        print(f"   WER: {r['wer']:.2%}")
        print(f"   CER: {r['cer']:.2%}")
        print(f"   Jaccard: {r['jaccard']:.2%}")
        print(f"   Cosine: {r['cosine']:.2%}")

    if results:
        best = results[0]
        print("\n" + "=" * 70)
        print(f"🏆 Best model: {best['model']} (WER: {best['wer']:.2%})")


if __name__ == '__main__':
    main()
