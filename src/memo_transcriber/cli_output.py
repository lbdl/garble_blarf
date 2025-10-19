"""
Consistent CLI output formatting utilities.
Centralizes all print patterns for easier maintenance and testing.
"""
from typing import Dict, Optional, Any


class OutputStyle:
    """Constants for output formatting."""
    SEPARATOR_WIDTH = 70
    INDENT = "   "
    DOUBLE_INDENT = "      "

    # Status emojis
    SUCCESS = "✅"
    ERROR = "❌"
    SKIP = "⏭️"
    UNKNOWN = "❓"
    NOTE = "📝"
    ROBOT = "🤖"
    STATS = "📊"
    EXPORT = "📤"
    FOLDER = "📁"
    DATABASE = "💾"
    TEST = "🧪"
    TROPHY = "🏆"
    PIN = "📌"
    CHART = "📈"
    SEARCH = "🔍"


class CliPrinter:
    """Utility class for consistent CLI output formatting."""

    @staticmethod
    def header(title: str, emoji: str = "") -> None:
        """Print a header line with optional emoji."""
        prefix = f"{emoji} " if emoji else ""
        print(f"{prefix}{title}")

    @staticmethod
    def separator(char: str = "=", width: int = OutputStyle.SEPARATOR_WIDTH) -> None:
        """Print a separator line."""
        print(char * width)

    @staticmethod
    def kv(key: str, value: Any, indent_level: int = 1) -> None:
        """Print a key-value pair with indentation."""
        indent = OutputStyle.INDENT * indent_level
        print(f"{indent}{key}: {value}")

    @staticmethod
    def status(status: str, message: str, use_emoji: bool = True) -> None:
        """Print a status message with appropriate emoji."""
        if use_emoji:
            emoji_map = {
                'success': OutputStyle.SUCCESS,
                'failed': OutputStyle.ERROR,
                'error': OutputStyle.ERROR,
                'skipped': OutputStyle.SKIP,
            }
            emoji = emoji_map.get(status.lower(), OutputStyle.UNKNOWN)
            print(f"{emoji} {status}: {message}")
        else:
            print(f"{status}: {message}")

    @staticmethod
    def error(message: str, exception: Optional[Exception] = None) -> None:
        """Print an error message."""
        msg = f"{OutputStyle.ERROR} {message}"
        if exception:
            msg += f": {exception}"
        print(msg)

    @staticmethod
    def success(message: str) -> None:
        """Print a success message."""
        print(f"{OutputStyle.SUCCESS} {message}")

    @staticmethod
    def info(message: str, emoji: str = "") -> None:
        """Print an informational message with optional emoji."""
        prefix = f"{emoji} " if emoji else ""
        print(f"{prefix}{message}")

    @staticmethod
    def summary(stats: Dict[str, Any], title: str = "Summary", emoji: str = OutputStyle.STATS) -> None:
        """Print a summary section with stats."""
        print(f"\n{emoji} {title}:")
        for key, value in stats.items():
            CliPrinter.kv(key.replace('_', ' ').capitalize(), value)

    @staticmethod
    def section_start(title: str, emoji: str = "", width: int = OutputStyle.SEPARATOR_WIDTH) -> None:
        """Start a new output section with header and separator."""
        CliPrinter.header(title, emoji)
        CliPrinter.separator("=", width)

    @staticmethod
    def section_end(width: int = OutputStyle.SEPARATOR_WIDTH) -> None:
        """End a section with separator."""
        print()
        CliPrinter.separator("=", width)

    @staticmethod
    def blank_line() -> None:
        """Print a blank line for spacing."""
        print()
