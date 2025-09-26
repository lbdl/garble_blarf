"""
Memo Organiser - Processes voice memo files and creates structured transcription data.
"""

from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path
import time
from .memo_data import VoiceMemoFile
from .transcriber import transcribe_file
from .voicememo_db import cli_get_rec_path

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


@dataclass
class OrganisedMemo:
    """Structured memo data with transcription."""
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

    def __init__(self, recordings_base_path: str = '', output: str = 'Documents/transcripions'):
        """Initialize with optional custom recordings path and output folder"""
        self.recordings_base = Path(recordings_base_path) if recordings_base_path else cli_get_rec_path()
        self.recordings_base = output

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

        for memo in iterator:
            # Check duration first (convert to minutes)
            duration_minutes = memo.duration_seconds / 60.0
            if duration_minutes > max_duration_minutes:
                organised.append(OrganisedMemo(
                    file_path=memo.f_path,
                    plain_title=memo.plain_title,
                    folder=memo.memo_folder,
                    uuid=memo.uuid,
                    transcription=f"Skipped: too long ({duration_minutes:.1f} min > {max_duration_minutes} min)",
                    status="skipped",
                    date=memo.recording_date
                ))
                if progress_bar:
                    progress_bar.update(1)
                continue

            # Construct full file path
            full_path = self.recordings_base / memo.f_path

            # Check if file exists
            if not full_path.exists():
                # TODO: this is largely pointless skip if missing is a bit shite, remove
                if skip_missing:
                    organised.append(OrganisedMemo(
                        file_path=str(full_path),
                        plain_title=memo.plain_title,
                        folder=memo.memo_folder,
                        uuid=memo.uuid,
                        transcription=f"skipping: file not found, may not be synced?",
                        status="skipped",
                        date=memo.recording_date
                    ))
                    if progress_bar:
                        progress_bar.update(1)
                    continue
                else:
                    organised.append(OrganisedMemo(
                        file_path=str(full_path),
                        plain_title=memo.plain_title,
                        folder=memo.memo_folder,
                        uuid=memo.uuid,
                        transcription=f"File not found: {full_path}, may not be synced",
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

                try:
                    transcription = transcribe_file(str(full_path))

                    # Check if transcription indicates an error
                    if transcription.startswith(("Transcription error:", "Recognition failed:", "Speech recognition not available")):
                        status = "failed"
                except Exception as e:
                    transcription = f"Transcription error: {str(e)}"
                    status = "failed"
            else:
                transcription = "[Transcription not requested]"
                status = "skipped"

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
