"""
Memo Organiser - Processes voice memo files and creates structured transcription data.
"""

from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path
import time
import uuid
import re
from datetime import datetime
from .memo_data import VoiceMemoFile
from .transcriber import transcribe_file
from .voicememo_db import cli_get_rec_path
from .database import MemoDatabase, TranscriptionRecord

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


@dataclass
class OrganisedMemo:
    """Structured memo data with transcription.

    Attributes:
        file_path: Full path to the audio file on disk
        plain_title: Human-readable title/name of the memo
        folder: Name of the folder containing this memo
        uuid: Unique identifier for the recording
        transcription: Transcribed text content or error message
        status: Processing status ('success', 'failed', 'skipped')
        date: Recording date as formatted string
    """
    file_path: str
    plain_title: str
    folder: str
    uuid: str
    transcription: str
    status: str  # 'success', 'failed', 'skipped'
    date: str

    def __str__(self) -> str:
        return (f"Memo: '{self.plain_title}' "
                f"[{self.status}] "
                f"({len(self.transcription)} chars)")


class MemoOrganiser:
    """Organises voice memos with transcriptions."""

    def __init__(self, recordings_base_path: str = '', output: str = 'Documents/transcriptions', db_path: str = 'memo_transcriptions.db'):
        """Initialize with optional custom recordings path, output folder, and database path"""
        self.recordings_base = Path(recordings_base_path) if recordings_base_path else cli_get_rec_path()
        self.output_base = Path(output)
        self.db = MemoDatabase(db_path)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')
        # Limit length
        return sanitized[:200] if len(sanitized) > 200 else sanitized

    def _generate_output_path(self, memo: VoiceMemoFile) -> str:
        """Generate output file path based on folder structure and memo title."""
        folder_name = self._sanitize_filename(memo.memo_folder)
        file_name = self._sanitize_filename(memo.plain_title) + '.txt'
        return str(Path(folder_name) / file_name)

    def organise_memos(self, memo_files: List[VoiceMemoFile],
                      transcribe: bool = True,
                      skip_missing: bool = True,
                      framework: bool = True,
                      max_duration_minutes: float = 8.0) -> List[OrganisedMemo]:
        """
        Organise memo files with transcriptions.

        Args:
            memo_files: List of VoiceMemoFile objects
            transcribe: Whether to transcribe audio files
            skip_missing: Whether to skip files that cannot be found (they may not be synced)
            framework: True for Apple Speech framework, False for local model
            max_duration_minutes: Skip files longer than this (in minutes)

        Returns:
            List of OrganisedMemo objects
        """
        organised = []

        # Start processing batch tracking
        batch_id = str(uuid.uuid4())
        if transcribe:
            self.db.start_processing_batch(
                batch_id=batch_id,
                total_files=len(memo_files),
                settings={
                    'skip_missing': skip_missing,
                    'framework': framework,
                    'max_duration_minutes': max_duration_minutes
                },
                model_used='apple_speech' if framework else 'local_whisper'
            )

        # Create single progress bar if tqdm is available
        if HAS_TQDM and transcribe:
            progress_bar = tqdm(total=len(memo_files), desc="", unit="file", position=1, leave=True)
            iterator = memo_files
        else:
            progress_bar = None
            iterator = memo_files
            if transcribe:
                print(f"Processing {len(memo_files)} memo files...")

        start_time = time.time()
        processed_count = 0
        success_count = failed_count = skipped_count = 0
        total_processing_time = 0.0

        for memo in iterator:
            # Generate output path for this memo
            output_file_path = self._generate_output_path(memo)

            # Check duration first (convert to minutes)
            duration_minutes = memo.duration_seconds / 60.0
            if duration_minutes > max_duration_minutes:
                transcription_msg = f"Skipped: too long ({duration_minutes:.1f} min > {max_duration_minutes} min)"

                # Save to database
                if transcribe:
                    self.db.save_transcription(TranscriptionRecord(
                        uuid=memo.uuid,
                        plain_title=memo.plain_title,
                        folder_name=memo.memo_folder,
                        file_path=memo.f_path,
                        output_file_path=output_file_path,
                        transcription=transcription_msg,
                        status="skipped",
                        duration_seconds=memo.duration_seconds,
                        recording_date=memo.recording_date,
                        processed_at=datetime.now().isoformat()
                    ))
                    skipped_count += 1

                organised.append(OrganisedMemo(
                    file_path=memo.f_path,
                    plain_title=memo.plain_title,
                    folder=memo.memo_folder,
                    uuid=memo.uuid,
                    transcription=transcription_msg,
                    status="skipped",
                    date=memo.recording_date
                ))
                if progress_bar:
                    progress_bar.update(1)
                continue

            # Construct full file path
            full_path = self.recordings_base / memo.f_path

            # Check if already processed in database
            if transcribe and self.db.is_file_processed(memo.uuid, str(full_path)):
                # Load from database
                existing_record = self.db.get_transcription(memo.uuid)
                if existing_record:
                    if progress_bar:
                        progress_bar.write(f"Cached: {memo.plain_title}")
                        progress_bar.update(1)

                    organised.append(OrganisedMemo(
                        file_path=existing_record.file_path,
                        plain_title=existing_record.plain_title,
                        folder=existing_record.folder_name,
                        uuid=existing_record.uuid,
                        transcription=existing_record.transcription,
                        status=existing_record.status,
                        date=existing_record.recording_date
                    ))

                    if existing_record.status == 'success':
                        success_count += 1
                    elif existing_record.status == 'failed':
                        failed_count += 1
                    else:
                        skipped_count += 1
                    continue

            # Check if file exists
            if not full_path.exists():
                # TODO: this is largely pointless skip if missing is a bit shite, remove
                if skip_missing:
                    transcription_msg = f"skipping: file not found, may not be synced?"
                    if transcribe:
                        self.db.save_transcription(TranscriptionRecord(
                            uuid=memo.uuid,
                            plain_title=memo.plain_title,
                            folder_name=memo.memo_folder,
                            file_path=memo.f_path,
                            output_file_path=output_file_path,
                            transcription=transcription_msg,
                            status="skipped",
                            duration_seconds=memo.duration_seconds,
                            recording_date=memo.recording_date,
                            processed_at=datetime.now().isoformat()
                        ))
                        skipped_count += 1

                    organised.append(OrganisedMemo(
                        file_path=str(full_path),
                        plain_title=memo.plain_title,
                        folder=memo.memo_folder,
                        uuid=memo.uuid,
                        transcription=transcription_msg,
                        status="skipped",
                        date=memo.recording_date
                    ))
                    if progress_bar:
                        progress_bar.update(1)
                    continue
                else:
                    transcription_msg = f"File not found: {full_path}, may not be synced"
                    if transcribe:
                        self.db.save_transcription(TranscriptionRecord(
                            uuid=memo.uuid,
                            plain_title=memo.plain_title,
                            folder_name=memo.memo_folder,
                            file_path=memo.f_path,
                            output_file_path=output_file_path,
                            transcription=transcription_msg,
                            status="failed",
                            error_message=transcription_msg,
                            duration_seconds=memo.duration_seconds,
                            recording_date=memo.recording_date,
                            processed_at=datetime.now().isoformat()
                        ))
                        failed_count += 1

                    organised.append(OrganisedMemo(
                        file_path=str(full_path),
                        plain_title=memo.plain_title,
                        folder=memo.memo_folder,
                        uuid=memo.uuid,
                        transcription=transcription_msg,
                        status="failed",
                        date=memo.recording_date
                    ))
                    if progress_bar:
                        progress_bar.update(1)
                    continue

            # Get transcription if requested
            transcription = ""
            status = "success"

            if transcribe:
                processed_count += 1

                # Display current file name above progress bar
                if progress_bar:
                    # Use tqdm.write to print above the progress bar
                    progress_bar.write(f"Processing: {memo.plain_title}")
                else:
                    elapsed = time.time() - start_time
                    if processed_count > 1:
                        avg_time = elapsed / (processed_count - 1)
                        remaining = avg_time * (len(memo_files) - processed_count)
                        print(f"[{processed_count}/{len(memo_files)}] Transcribing: {memo.plain_title} "
                              f"(~{remaining:.0f}s remaining)")
                    else:
                        print(f"[{processed_count}/{len(memo_files)}] Transcribing: {memo.plain_title}")

                # Time the transcription
                transcription_start = time.time()
                try:
                    transcription = transcribe_file(str(full_path))
                    transcription_time = time.time() - transcription_start
                    total_processing_time += transcription_time

                    # Check if transcription indicates an error
                    if transcription.startswith(("Transcription error:", "Recognition failed:", "Speech recognition not available")):
                        status = "failed"
                        failed_count += 1
                    else:
                        status = "success"
                        success_count += 1

                except Exception as e:
                    transcription_time = time.time() - transcription_start
                    total_processing_time += transcription_time
                    transcription = f"Transcription error: {str(e)}"
                    status = "failed"
                    failed_count += 1

                # Save transcription to database
                file_hash = self.db.get_file_hash(str(full_path))
                self.db.save_transcription(TranscriptionRecord(
                    uuid=memo.uuid,
                    plain_title=memo.plain_title,
                    folder_name=memo.memo_folder,
                    file_path=memo.f_path,
                    output_file_path=output_file_path,
                    transcription=transcription,
                    status=status,
                    error_message=transcription if status == "failed" else None,
                    duration_seconds=memo.duration_seconds,
                    recording_date=memo.recording_date,
                    processed_at=datetime.now().isoformat(),
                    file_hash=file_hash,
                    model_used='apple_speech' if framework else 'local_whisper',
                    processing_time_seconds=transcription_time
                ))

            else:
                transcription = "[Transcription not requested]"
                status = "skipped"
                skipped_count += 1

            # Update progress bar
            if progress_bar:
                progress_bar.update(1)

            organised.append(OrganisedMemo(
                file_path=str(full_path),
                plain_title=memo.plain_title,
                folder=memo.memo_folder,
                uuid=memo.uuid,
                transcription=transcription,
                status=status,
                date=memo.recording_date
            ))

        # Close progress bar
        if progress_bar:
            progress_bar.close()

        # Finish batch tracking
        if transcribe and processed_count > 0:
            avg_processing_time = total_processing_time / processed_count if processed_count > 0 else 0.0
            self.db.finish_processing_batch(
                batch_id=batch_id,
                success_count=success_count,
                failed_count=failed_count,
                skipped_count=skipped_count,
                avg_time=avg_processing_time
            )

        return organised

    def organise_and_filter(self, memo_files: List[VoiceMemoFile],
                          folder_filter: str = None,
                          status_filter: str = None) -> List[OrganisedMemo]:
        """
        Organise memos and filter by folder or status.

        Args:
            memo_files: List of VoiceMemoFile objects
            folder_filter: Only include memos from this folder
            status_filter: Only include memos with this status ('success', 'failed', 'skipped')

        Returns:
            Filtered list of OrganisedMemo objects
        """
        organised = self.organise_memos(memo_files)

        filtered = organised

        if folder_filter:
            filtered = [memo for memo in filtered if memo.folder == folder_filter]

        if status_filter:
            filtered = [memo for memo in filtered if memo.status == status_filter]

        return filtered

    def get_transcription_summary(self, organised_memos: List[OrganisedMemo]) -> Dict[str, int]:
        """Get summary statistics for transcriptions."""
        summary = {
            'total': len(organised_memos),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'total_chars': 0
        }

        for memo in organised_memos:
            summary[memo.status] += 1
            if memo.status == 'success':
                summary['total_chars'] += len(memo.transcription)

        return summary

    def save_transcriptions_to_dict(self, organised_memos: List[OrganisedMemo]) -> Dict[str, Dict]:
        """Convert organised memos to dictionary format for JSON export."""
        # TODO add the recording date
        return {
            memo.uuid: {
                'title': memo.plain_title,
                'folder': memo.folder,
                'file_path': memo.file_path,
                'transcription': memo.transcription,
                'status': memo.status,
                'char_count': len(memo.transcription)
            }
            for memo in organised_memos
        }
