"""
ANSI color codes and terminal detection utilities.

Provides color constants for terminal output and helper functions
for detecting terminal capabilities.
"""

import os
import sys
from typing import Optional


class Color:
    """
    ANSI color code constants for terminal output.

    Each attribute contains the ANSI escape sequence for the
    corresponding color or style.
    """

    # Reset
    RESET = "\033[0m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    # Semantic aliases for diff output
    ADDED = GREEN       # Green for additions
    REMOVED = RED       # Red for removals
    MODIFIED = YELLOW   # Yellow for modifications
    HEADER = BOLD + CYAN  # Bold cyan for headers
    PATH = BLUE         # Blue for paths
    VALUE = WHITE       # White for values
    DIM_TEXT = GRAY     # Gray for less important text


def supports_color() -> bool:
    """
    Detect if the current terminal supports ANSI color codes.

    Checks:
    - NO_COLOR environment variable
    - Platform (Windows needs special handling)
    - Whether stdout is a TTY

    Returns:
        True if colors are supported, False otherwise.
    """
    # Respect NO_COLOR environment variable
    if os.environ.get("NO_COLOR"):
        return False

    # Check if stdout is a TTY
    if not hasattr(sys.stdout, 'isatty'):
        return False

    if not sys.stdout.isatty():
        return False

    # On Windows, check for ANSI support
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Enable ANSI escape sequences on Windows 10+
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False

    return True


def colorize(text: str, color_code: str, use_color: Optional[bool] = None) -> str:
    """
    Wrap text with ANSI color codes.

    Args:
        text: The text to colorize.
        color_code: ANSI color code string.
        use_color: Whether to use color (None for auto-detection).

    Returns:
        The colorized text, or plain text if color is disabled.
    """
    if use_color is None:
        use_color = supports_color()

    if use_color:
        return f"{color_code}{text}{Color.RESET}"
    return text


def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences from a string.

    Args:
        text: The text with potential ANSI codes.

    Returns:
        The text with all ANSI codes removed.
    """
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)
