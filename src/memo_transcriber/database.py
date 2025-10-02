"""
Database management for memo transcriber - handles transcription cache, processing metadata, and export tracking.
"""

import sqlite3
import hashlib
import time
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


def get_user_data_dir() -> Path:
    """Get the user data directory for memo transcriber."""
    data_dir = Path.home() / '.local' / 'share' / 'memo-transcriber'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@dataclass
class TranscriptionRecord:
    """Database record for a transcribed memo.

    Attributes:
        uuid: Unique identifier for the voice memo recording
        plain_title: Human-readable title/name of the memo
        folder_name: Name of the folder containing this memo
        file_path: Relative path to the source audio file
        output_file_path: Path where organized file will be written
        transcription: Transcribed text content
        status: Processing status ('success', 'failed', 'skipped')
        error_message: Error details if processing failed
        duration_seconds: Length of the recording in seconds
        recording_date: Date when the recording was created
        processed_at: When transcription was completed
        file_hash: Hash of audio file for change detection
        model_used: Which transcription model/method was used
        processing_time_seconds: How long transcription took
    """
    uuid: str
    plain_title: str
    folder_name: str
    file_path: str
    output_file_path: str
    transcription: str
    status: str
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    recording_date: Optional[str] = None
    processed_at: Optional[str] = None
    file_hash: Optional[str] = None
    model_used: Optional[str] = None
    processing_time_seconds: Optional[float] = None


@dataclass
class ExportRecord:
    """Database record for file export tracking.

    Attributes:
        id: Auto-increment ID for the export record
        uuid: Reference to the transcription record
        output_file_path: Path where file was exported
        exported_at: When export was completed
        file_size_bytes: Size of exported file for verification
        checksum: File content hash for integrity verification
        export_status: Export result ('success', 'failed', 'pending')
        error_message: Error details if export failed
        export_format: File format ('txt', 'md', 'json', etc.)
    """
    uuid: str
    output_file_path: str
    export_status: str
    id: Optional[int] = None
    exported_at: Optional[str] = None
    file_size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    export_format: str = 'txt'


@dataclass
class ProcessingBatch:
    """Database record for processing batch metadata.

    Attributes:
        batch_id: Unique identifier for the processing batch
        started_at: When processing began
        completed_at: When processing finished
        total_files: Number of files in this batch
        success_count: Number of successfully processed files
        failed_count: Number of failed files
        skipped_count: Number of skipped files
        settings_json: Processing parameters as JSON string
        model_used: Which transcription model was used
        avg_processing_time: Average processing time per file
        id: Auto-increment ID for the batch record
    """
    batch_id: str
    total_files: int
    success_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    id: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    settings_json: Optional[str] = None
    model_used: Optional[str] = None
    avg_processing_time: Optional[float] = None


@dataclass
class ComparisonRecord:
    """Database record for transcription comparison results.

    Attributes:
        id: Auto-increment ID
        reference_uuid: UUID of the reference (ground truth) transcription
        hypothesis_uuid: UUID of the hypothesis (test) transcription
        wer: Word Error Rate (0.0 to 1.0+)
        cer: Character Error Rate (0.0 to 1.0+)
        substitutions: Number of word substitutions
        deletions: Number of word deletions
        insertions: Number of word insertions
        total_edits: Total edit operations needed
        word_count_ref: Word count in reference
        word_count_hyp: Word count in hypothesis
        word_count_diff: Difference in word counts
        word_count_diff_pct: Percentage difference in word counts
        jaccard_similarity: Jaccard similarity score (0.0 to 1.0)
        cosine_similarity: Cosine similarity score (0.0 to 1.0)
        compared_at: When comparison was performed
        notes: Optional notes about the comparison
    """
    reference_uuid: str
    hypothesis_uuid: str
    wer: float
    cer: float
    substitutions: int
    deletions: int
    insertions: int
    total_edits: int
    word_count_ref: int
    word_count_hyp: int
    word_count_diff: int
    word_count_diff_pct: float
    jaccard_similarity: float
    cosine_similarity: float
    id: Optional[int] = None
    compared_at: Optional[str] = None
    notes: Optional[str] = None


class MemoDatabase:
    """Manages SQLite database for memo transcription data."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection and create tables if needed."""
        if db_path is None:
            # Use user data directory by default
            self.db_path = get_user_data_dir() / "memo_transcriptions.db"
        else:
            # Allow custom path (for testing, etc.)
            self.db_path = Path(db_path)
        self.init_database()

    def init_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS transcriptions (
                    uuid TEXT PRIMARY KEY,
                    plain_title TEXT NOT NULL,
                    folder_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    output_file_path TEXT NOT NULL,
                    transcription TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    duration_seconds REAL,
                    recording_date TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_hash TEXT,
                    model_used TEXT,
                    processing_time_seconds REAL,
                    is_reference INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS file_exports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    output_file_path TEXT NOT NULL,
                    exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size_bytes INTEGER,
                    checksum TEXT,
                    export_status TEXT NOT NULL,
                    error_message TEXT,
                    export_format TEXT DEFAULT 'txt',
                    FOREIGN KEY (uuid) REFERENCES transcriptions(uuid)
                );

                CREATE TABLE IF NOT EXISTS processing_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    total_files INTEGER,
                    success_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    skipped_count INTEGER DEFAULT 0,
                    settings_json TEXT,
                    model_used TEXT,
                    avg_processing_time REAL
                );

                CREATE TABLE IF NOT EXISTS transcription_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reference_uuid TEXT NOT NULL,
                    hypothesis_uuid TEXT NOT NULL,
                    wer REAL NOT NULL,
                    cer REAL NOT NULL,
                    substitutions INTEGER NOT NULL,
                    deletions INTEGER NOT NULL,
                    insertions INTEGER NOT NULL,
                    total_edits INTEGER NOT NULL,
                    word_count_ref INTEGER NOT NULL,
                    word_count_hyp INTEGER NOT NULL,
                    word_count_diff INTEGER NOT NULL,
                    word_count_diff_pct REAL NOT NULL,
                    jaccard_similarity REAL NOT NULL,
                    cosine_similarity REAL NOT NULL,
                    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (reference_uuid) REFERENCES transcriptions(uuid),
                    FOREIGN KEY (hypothesis_uuid) REFERENCES transcriptions(uuid)
                );

                CREATE INDEX IF NOT EXISTS idx_transcriptions_status ON transcriptions(status);
                CREATE INDEX IF NOT EXISTS idx_transcriptions_folder ON transcriptions(folder_name);
                CREATE INDEX IF NOT EXISTS idx_transcriptions_reference ON transcriptions(is_reference);
                CREATE INDEX IF NOT EXISTS idx_file_exports_uuid ON file_exports(uuid);
                CREATE INDEX IF NOT EXISTS idx_file_exports_status ON file_exports(export_status);
                CREATE INDEX IF NOT EXISTS idx_comparisons_reference ON transcription_comparisons(reference_uuid);
                CREATE INDEX IF NOT EXISTS idx_comparisons_hypothesis ON transcription_comparisons(hypothesis_uuid);
            """)

    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA-256 hash of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (FileNotFoundError, PermissionError):
            return None

    def is_file_processed(self, uuid: str, file_path: str) -> bool:
        """Check if file has been processed and hasn't changed."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT file_hash, status FROM transcriptions
                WHERE uuid = ? AND status = 'success'
            """, (uuid,))

            row = cursor.fetchone()
            if not row:
                return False

            # Check if file hash matches (file hasn't changed)
            current_hash = self.get_file_hash(file_path)
            return current_hash == row['file_hash']

    def save_transcription(self, record: TranscriptionRecord) -> None:
        """Save or update a transcription record."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO transcriptions (
                    uuid, plain_title, folder_name, file_path, output_file_path,
                    transcription, status, error_message, duration_seconds,
                    recording_date, processed_at, file_hash, model_used,
                    processing_time_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.uuid, record.plain_title, record.folder_name,
                record.file_path, record.output_file_path, record.transcription,
                record.status, record.error_message, record.duration_seconds,
                record.recording_date, record.processed_at, record.file_hash,
                record.model_used, record.processing_time_seconds
            ))

    def get_transcription(self, uuid: str) -> Optional[TranscriptionRecord]:
        """Retrieve a transcription record by UUID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM transcriptions WHERE uuid = ?", (uuid,))
            row = cursor.fetchone()

            if row:
                return TranscriptionRecord(**dict(row))
            return None

    def get_all_transcriptions(self, status_filter: Optional[str] = None) -> List[TranscriptionRecord]:
        """Get all transcription records, optionally filtered by status."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if status_filter:
                cursor.execute("SELECT * FROM transcriptions WHERE status = ? ORDER BY processed_at DESC", (status_filter,))
            else:
                cursor.execute("SELECT * FROM transcriptions ORDER BY processed_at DESC")

            return [TranscriptionRecord(**dict(row)) for row in cursor.fetchall()]

    def start_processing_batch(self, batch_id: str, total_files: int, settings: Dict[str, Any], model_used: str) -> None:
        """Record the start of a processing batch."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO processing_metadata (
                    batch_id, total_files, settings_json, model_used
                ) VALUES (?, ?, ?, ?)
            """, (batch_id, total_files, json.dumps(settings), model_used))

    def finish_processing_batch(self, batch_id: str, success_count: int, failed_count: int, skipped_count: int, avg_time: float) -> None:
        """Update processing batch with completion data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE processing_metadata
                SET completed_at = CURRENT_TIMESTAMP,
                    success_count = ?,
                    failed_count = ?,
                    skipped_count = ?,
                    avg_processing_time = ?
                WHERE batch_id = ?
            """, (success_count, failed_count, skipped_count, avg_time, batch_id))

    def record_export(self, export_record: ExportRecord) -> int:
        """Record a file export attempt."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_exports (
                    uuid, output_file_path, file_size_bytes, checksum,
                    export_status, error_message, export_format
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                export_record.uuid, export_record.output_file_path,
                export_record.file_size_bytes, export_record.checksum,
                export_record.export_status, export_record.error_message,
                export_record.export_format
            ))
            return cursor.lastrowid

    def get_unexported_transcriptions(self) -> List[TranscriptionRecord]:
        """Get all successful transcriptions that haven't been exported yet."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT t.* FROM transcriptions t
                LEFT JOIN file_exports e ON t.uuid = e.uuid AND e.export_status = 'success'
                WHERE t.status = 'success' AND e.uuid IS NULL
                ORDER BY t.processed_at
            """)

            return [TranscriptionRecord(**dict(row)) for row in cursor.fetchall()]

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get overall processing statistics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get transcription stats
            cursor.execute("""
                SELECT
                    status,
                    COUNT(*) as count,
                    AVG(processing_time_seconds) as avg_time,
                    SUM(duration_seconds) as total_duration
                FROM transcriptions
                GROUP BY status
            """)
            transcription_stats = {row['status']: dict(row) for row in cursor.fetchall()}

            # Get export stats
            cursor.execute("""
                SELECT
                    export_status,
                    COUNT(*) as count
                FROM file_exports
                GROUP BY export_status
            """)
            export_stats = {row['export_status']: dict(row) for row in cursor.fetchall()}

            return {
                'transcriptions': transcription_stats,
                'exports': export_stats
            }

    def mark_as_reference(self, uuid: str) -> None:
        """Mark a transcription as a reference (ground truth) transcription."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE transcriptions
                SET is_reference = 1
                WHERE uuid = ?
            """, (uuid,))

    def unmark_as_reference(self, uuid: str) -> None:
        """Remove reference marking from a transcription."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE transcriptions
                SET is_reference = 0
                WHERE uuid = ?
            """, (uuid,))

    def get_reference_transcriptions(self) -> List[TranscriptionRecord]:
        """Get all transcriptions marked as reference."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM transcriptions
                WHERE is_reference = 1
                ORDER BY plain_title
            """)

            return [TranscriptionRecord(**dict(row)) for row in cursor.fetchall()]

    def save_comparison(self, comparison: ComparisonRecord) -> int:
        """Save a transcription comparison result."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transcription_comparisons (
                    reference_uuid, hypothesis_uuid, wer, cer,
                    substitutions, deletions, insertions, total_edits,
                    word_count_ref, word_count_hyp, word_count_diff,
                    word_count_diff_pct, jaccard_similarity, cosine_similarity,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comparison.reference_uuid, comparison.hypothesis_uuid,
                comparison.wer, comparison.cer,
                comparison.substitutions, comparison.deletions,
                comparison.insertions, comparison.total_edits,
                comparison.word_count_ref, comparison.word_count_hyp,
                comparison.word_count_diff, comparison.word_count_diff_pct,
                comparison.jaccard_similarity, comparison.cosine_similarity,
                comparison.notes
            ))
            return cursor.lastrowid

    def get_comparisons_for_reference(self, reference_uuid: str) -> List[ComparisonRecord]:
        """Get all comparisons for a specific reference transcription."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM transcription_comparisons
                WHERE reference_uuid = ?
                ORDER BY compared_at DESC
            """, (reference_uuid,))

            return [ComparisonRecord(**dict(row)) for row in cursor.fetchall()]

    def get_comparison_summary_by_model(self, reference_uuid: str) -> List[Dict[str, Any]]:
        """Get comparison summary grouped by model for a reference transcription."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    t.model_used,
                    COUNT(*) as comparison_count,
                    AVG(c.wer) as avg_wer,
                    MIN(c.wer) as min_wer,
                    MAX(c.wer) as max_wer,
                    AVG(c.cer) as avg_cer,
                    AVG(c.jaccard_similarity) as avg_jaccard,
                    AVG(c.cosine_similarity) as avg_cosine
                FROM transcription_comparisons c
                JOIN transcriptions t ON c.hypothesis_uuid = t.uuid
                WHERE c.reference_uuid = ?
                GROUP BY t.model_used
                ORDER BY avg_wer
            """, (reference_uuid,))

            return [dict(row) for row in cursor.fetchall()]

