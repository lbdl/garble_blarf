"""
High-level printing functions for CLI commands.
Uses cli_output utilities for consistent formatting.
"""
from typing import Dict, Any, Optional, List
from .cli_output import CliPrinter, OutputStyle


class Printer:
    """High-level printing functions for CLI commands."""

    @staticmethod
    def print_export_header(export_format: str, output_dir: str, db_path: str) -> None:
        """Print the header section for export command.

        Args:
            export_format: The export format (txt, md, json)
            output_dir: The output directory path
            db_path: The database path
        """
        CliPrinter.header("Exporting transcriptions...", OutputStyle.EXPORT)
        CliPrinter.kv("Format", export_format)
        CliPrinter.kv("Output", output_dir)
        CliPrinter.kv("Database", db_path)
        CliPrinter.separator()

    @staticmethod
    def print_export_summary(stats: Dict[str, int], output_dir: str) -> None:
        """Print the summary section after export.

        Args:
            stats: Dictionary with 'total', 'exported', 'skipped', 'failed' counts
            output_dir: The output directory path where files were exported
        """
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

    @staticmethod
    def print_export_error(exception: Exception) -> None:
        """Print an error message for export failures.

        Args:
            exception: The exception that was raised
        """
        CliPrinter.error("Export failed", exception)

    @staticmethod
    def print_db_stats_header(db_path: str, emoji: str = OutputStyle.STATS) -> None:
        """Print the header section for database statistics.

        Args:
            db_path: The database path
            emoji: The emoji to use in the header (defaults to STATS)
        """
        CliPrinter.section_start(f"Database: {db_path}", emoji)

    @staticmethod
    def print_transcription_stats(stats: Dict[str, Any]) -> None:
        """Print transcription statistics section.

        Args:
            stats: Statistics dictionary with transcription data
        """
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

    @staticmethod
    def print_export_stats(stats: Dict[str, Any]) -> None:
        """Print export statistics section.

        Args:
            stats: Statistics dictionary with export data
        """
        if 'exports' in stats and stats['exports']:
            CliPrinter.blank_line()
            CliPrinter.info("Export Summary:")
            for status, data in stats['exports'].items():
                count = data['count']
                CliPrinter.kv(f"{status.capitalize()}", f"{count} files", indent_level=1)
        else:
            CliPrinter.blank_line()
            CliPrinter.info("No exports recorded yet")

    @staticmethod
    def print_unexported_count(count: int) -> None:
        """Print the count of unexported transcriptions.

        Args:
            count: Number of unexported transcriptions
        """
        if count > 0:
            CliPrinter.blank_line()
            CliPrinter.info(f"Unexported transcriptions: {count} files ready for export")

    @staticmethod
    def print_no_transcriptions_found(status_filter: Optional[str] = None) -> None:
        """Print message when no transcriptions are found.

        Args:
            status_filter: Optional status filter that was applied
        """
        status_msg = f" with status '{status_filter}'" if status_filter else ""
        CliPrinter.info(f"No transcriptions found{status_msg}")

    @staticmethod
    def print_list_limit_message(shown: int, total: int) -> None:
        """Print message about limited results.

        Args:
            shown: Number of records being shown
            total: Total number of records available
        """
        CliPrinter.info(f"Showing first {shown} of {total} records (use --limit to see more)")

    @staticmethod
    def print_cached_header(count: int) -> None:
        """Print header for cached transcriptions list.

        Args:
            count: Number of records being displayed
        """
        CliPrinter.header(f"Cached Transcriptions ({count} records):")
        CliPrinter.separator()

    @staticmethod
    def print_transcription_compact(record: Any) -> None:
        """Print a single transcription record in compact format.

        Args:
            record: TranscriptionRecord with attributes: plain_title, status, transcription
        """
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
            'success': OutputStyle.SUCCESS,
            'failed': OutputStyle.ERROR,
            'skipped': OutputStyle.SKIP
        }.get(record.status, OutputStyle.UNKNOWN)

        print(f"{status_emoji} {display_title} [{record.status}]")

    @staticmethod
    def print_transcription_detailed(record: Any) -> None:
        """Print a single transcription record in detailed format.

        Args:
            record: TranscriptionRecord with full attributes
        """
        duration_min = (record.duration_seconds or 0) / 60.0
        proc_time = record.processing_time_seconds or 0

        CliPrinter.blank_line()
        CliPrinter.header(record.plain_title, OutputStyle.NOTE)
        CliPrinter.kv("UUID", record.uuid)
        CliPrinter.kv("Folder", record.folder_name)
        CliPrinter.kv("Status", record.status)
        CliPrinter.kv("Duration", f"{duration_min:.1f} min")

        if proc_time > 0:
            CliPrinter.kv("Processing time", f"{proc_time:.2f}s")
        if record.model_used:
            CliPrinter.kv("Model", record.model_used)
        if record.processed_at:
            CliPrinter.kv("Processed", record.processed_at)

        if record.status == 'success' and record.transcription:
            preview = record.transcription[:100]
            CliPrinter.kv("Preview", f"{preview}{'...' if len(record.transcription) > 100 else ''}")
        elif record.status == 'failed' and record.error_message:
            CliPrinter.kv("Error", record.error_message)

    @staticmethod
    def print_cached_list(records: List[Any], compact: bool = False) -> None:
        """Print a list of cached transcriptions.

        Args:
            records: List of TranscriptionRecord objects
            compact: If True, use compact format; otherwise use detailed format
        """
        Printer.print_cached_header(len(records))

        if compact:
            for record in records:
                Printer.print_transcription_compact(record)
        else:
            for record in records:
                Printer.print_transcription_detailed(record)
