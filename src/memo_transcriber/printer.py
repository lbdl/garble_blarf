"""
High-level printing functions for CLI commands.
Uses cli_output utilities for consistent formatting.
"""
from typing import Dict, Any, Optional, List, Callable
from .cli_output import CliPrinter, OutputStyle


# Constants
STATUS_EMOJI_MAP = {
    'success': OutputStyle.SUCCESS,
    'failed': OutputStyle.ERROR,
    'skipped': OutputStyle.SKIP
}


class Printer:
    """High-level printing functions for CLI commands."""

    # ============================================
    # Private Helper Methods
    # ============================================

    @staticmethod
    def _truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to max_length and add ellipsis if needed.

        Args:
            text: The text to truncate
            max_length: Maximum length before truncation

        Returns:
            Truncated text with '...' suffix if needed
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    @staticmethod
    def _print_stats_section(
        stats: Dict[str, Any],
        section_key: str,
        section_title: str,
        empty_message: str,
        detail_formatter: Optional[Callable[[Dict[str, Any]], List[tuple]]] = None
    ) -> None:
        """Generic function to print a statistics section.

        Args:
            stats: Full statistics dictionary
            section_key: Key to access this section in stats dict
            section_title: Title to display for this section
            empty_message: Message to show if section is empty
            detail_formatter: Optional function to extract additional details from data dict
        """
        if section_key in stats and stats[section_key]:
            CliPrinter.blank_line()
            CliPrinter.info(section_title)
            for status, data in stats[section_key].items():
                count = data['count']
                CliPrinter.kv(f"{status.capitalize()}", f"{count} files", indent_level=1)

                # Print additional details if formatter provided
                if detail_formatter:
                    details = detail_formatter(data)
                    for key, value in details:
                        CliPrinter.kv(key, value, indent_level=2)
        else:
            CliPrinter.blank_line()
            CliPrinter.info(empty_message)

    @staticmethod
    def _print_dict_as_kvs(data: Dict[str, Any], indent_level: int = 1) -> None:
        """Print dictionary items as key-value pairs.

        Args:
            data: Dictionary to print
            indent_level: Indentation level for output
        """
        for key, value in data.items():
            display_key = key.replace('_', ' ').capitalize()
            CliPrinter.kv(display_key, value, indent_level=indent_level)

    # ============================================
    # Export Command Functions
    # ============================================

    @staticmethod
    def print_export_header(export_format: str, output_dir: str, db_path: str) -> None:
        """Print the header section for export command."""
        CliPrinter.header("Exporting transcriptions...", OutputStyle.EXPORT)
        CliPrinter.kv("Format", export_format)
        CliPrinter.kv("Output", output_dir)
        CliPrinter.kv("Database", db_path)
        CliPrinter.separator()

    @staticmethod
    def print_export_summary(stats: Dict[str, int], output_dir: str) -> None:
        """Print the summary section after export."""
        CliPrinter.blank_line()
        CliPrinter.separator()
        CliPrinter.header("Export Summary:", OutputStyle.STATS)
        Printer._print_dict_as_kvs(stats)

        if stats.get('exported', 0) > 0:
            CliPrinter.blank_line()
            CliPrinter.success(f"Successfully exported {stats['exported']} files to {output_dir}")

    @staticmethod
    def print_export_error(exception: Exception) -> None:
        """Print an error message for export failures."""
        CliPrinter.error("Export failed", exception)

    # ============================================
    # Database Stats Functions
    # ============================================

    @staticmethod
    def print_db_stats_header(db_path: str, emoji: str = OutputStyle.STATS) -> None:
        """Print the header section for database statistics."""
        CliPrinter.section_start(f"Database: {db_path}", emoji)

    @staticmethod
    def print_transcription_stats(stats: Dict[str, Any]) -> None:
        """Print transcription statistics section."""
        def format_transcription_details(data: Dict[str, Any]) -> List[tuple]:
            """Extract additional transcription details."""
            details = []
            avg_time = data.get('avg_time', 0) or 0
            total_duration = data.get('total_duration', 0) or 0

            if avg_time > 0:
                details.append(("Avg processing time", f"{avg_time:.2f}s"))
            if total_duration > 0:
                details.append(("Total audio duration", f"{total_duration/60:.1f} minutes"))

            return details

        Printer._print_stats_section(
            stats=stats,
            section_key='transcriptions',
            section_title="Transcription Summary:",
            empty_message="No transcriptions found in database",
            detail_formatter=format_transcription_details
        )

    @staticmethod
    def print_export_stats(stats: Dict[str, Any]) -> None:
        """Print export statistics section."""
        Printer._print_stats_section(
            stats=stats,
            section_key='exports',
            section_title="Export Summary:",
            empty_message="No exports recorded yet"
        )

    @staticmethod
    def print_unexported_count(count: int) -> None:
        """Print the count of unexported transcriptions."""
        if count > 0:
            CliPrinter.blank_line()
            CliPrinter.info(f"Unexported transcriptions: {count} files ready for export")

    # ============================================
    # List Cached Functions
    # ============================================

    @staticmethod
    def print_no_transcriptions_found(status_filter: Optional[str] = None) -> None:
        """Print message when no transcriptions are found."""
        status_msg = f" with status '{status_filter}'" if status_filter else ""
        CliPrinter.info(f"No transcriptions found{status_msg}")

    @staticmethod
    def print_list_limit_message(shown: int, total: int) -> None:
        """Print message about limited results."""
        CliPrinter.info(f"Showing first {shown} of {total} records (use --limit to see more)")

    @staticmethod
    def print_cached_header(count: int) -> None:
        """Print header for cached transcriptions list."""
        CliPrinter.header(f"Cached Transcriptions ({count} records):")
        CliPrinter.separator()

    @staticmethod
    def print_transcription_compact(record: Any) -> None:
        """Print a single transcription record in compact format."""
        # Check if title is generic "New Recording X" pattern
        is_untitled = record.plain_title.startswith("New Recording")

        if is_untitled and record.status == 'success' and record.transcription:
            # Show first ~5 words of transcription
            words = record.transcription.split()[:5]
            display_title = ' '.join(words) + ('...' if len(record.transcription.split()) > 5 else '')
        else:
            display_title = record.plain_title

        # Get status emoji
        status_emoji = STATUS_EMOJI_MAP.get(record.status, OutputStyle.UNKNOWN)
        print(f"{status_emoji} {display_title} [{record.status}]")

    @staticmethod
    def print_transcription_detailed(record: Any) -> None:
        """Print a single transcription record in detailed format."""
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
            CliPrinter.kv("Preview", Printer._truncate_text(record.transcription))
        elif record.status == 'failed' and record.error_message:
            CliPrinter.kv("Error", record.error_message)

    @staticmethod
    def print_cached_list(records: List[Any], compact: bool = False) -> None:
        """Print a list of cached transcriptions."""
        Printer.print_cached_header(len(records))

        print_func = Printer.print_transcription_compact if compact else Printer.print_transcription_detailed
        for record in records:
            print_func(record)

    # ============================================
    # List Models Functions
    # ============================================

    @staticmethod
    def print_models_list(model_info_dict: Dict[Any, Any], default_model: Any) -> None:
        """Print list of available transcription models."""
        CliPrinter.header("Available Transcription Models:")
        CliPrinter.separator()

        for model, info in model_info_dict.items():
            CliPrinter.blank_line()
            CliPrinter.header(model.value, OutputStyle.ROBOT)
            CliPrinter.kv("Name", info.display_name)
            CliPrinter.kv("Engine", info.engine)
            CliPrinter.kv("Speed", info.relative_speed)
            CliPrinter.kv("Accuracy", info.relative_accuracy)
            CliPrinter.kv("Description", info.description)

        CliPrinter.blank_line()
        CliPrinter.separator()
        CliPrinter.info(f"Default model: {default_model.value}")
        CliPrinter.blank_line()
        CliPrinter.info("Usage: memo-transcriber organise --model <model-name>")

    @staticmethod
    def print_invalid_model_error(model: str, available_models: List[tuple]) -> None:
        """Print error message for invalid model selection."""
        CliPrinter.error(f"Invalid model: {model}")
        CliPrinter.blank_line()
        CliPrinter.info("Available models:")
        for model_name, display_name in available_models:
            CliPrinter.kv(model_name, display_name, indent_level=1)

    # ============================================
    # Organise Command Functions
    # ============================================

    @staticmethod
    def print_organise_header(voice_memos_db: str, transcription_db: str, model: str) -> None:
        """Print header for organise command."""
        CliPrinter.header(f"Voice Memos DB: {voice_memos_db}", OutputStyle.FOLDER)
        CliPrinter.header(f"Transcription DB: {transcription_db}", OutputStyle.DATABASE)
        CliPrinter.header(f"Model: {model}", OutputStyle.ROBOT)

    @staticmethod
    def print_organised_memo(memo: Any) -> None:
        """Print a single organised memo result."""
        CliPrinter.header(memo.plain_title, OutputStyle.NOTE)
        CliPrinter.kv("Status", memo.status)
        CliPrinter.kv("Folder", memo.folder)

        if memo.status == 'success':
            CliPrinter.kv("Transcript", Printer._truncate_text(memo.transcription))
        elif memo.status == 'failed':
            CliPrinter.kv("Error", memo.transcription)

        CliPrinter.blank_line()

    @staticmethod
    def print_organise_summary(summary: Dict[str, int]) -> None:
        """Print summary of organise operation."""
        CliPrinter.info(
            f"Summary: {summary['success']} success, {summary['failed']} failed, {summary['skipped']} skipped"
        )
