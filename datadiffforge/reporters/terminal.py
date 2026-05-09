"""
Terminal reporter for DataDiffForge.

Produces colored diff output with +/- indicators, tree structure,
and summary statistics suitable for terminal display.
"""

from typing import TYPE_CHECKING, Optional

from .base import ReporterInterface
from ..utils.color import Color, colorize

if TYPE_CHECKING:
    from ..core.types import DiffResult, Change, DiffOp


class TerminalReporter(ReporterInterface):
    """
    Reporter that produces colored terminal output.

    Features:
    - Color-coded change indicators (+ green, - red, ~ yellow)
    - Tree-like path display
    - Summary statistics
    - Configurable color support
    """

    def __init__(self, use_color: Optional[bool] = None) -> None:
        """
        Initialize the terminal reporter.

        Args:
            use_color: Whether to use colored output.
                       None for auto-detection based on terminal.
        """
        self.use_color = use_color

    @property
    def format_name(self) -> str:
        """Return 'terminal'."""
        return "terminal"

    def report(self, result: "DiffResult", **kwargs) -> str:
        """
        Format a DiffResult as colored terminal output.

        Args:
            result: The diff result to format.
            **kwargs: Additional options:
                - stat_only: If True, show only statistics.

        Returns:
            Formatted terminal output string.
        """
        stat_only = kwargs.get('stat_only', False)
        lines = []

        # Header
        lines.append(self._header(
            f"Diff: {result.left_label} vs {result.right_label}"
        ))
        lines.append("")

        if not result.has_changes:
            lines.append(colorize("  No differences found.", Color.DIM_TEXT, self.use_color))
            return '\n'.join(lines)

        if stat_only:
            lines.append(self._format_stats(result))
            return '\n'.join(lines)

        # Changes
        for change in result.changes:
            lines.append(self._format_change(change))

        # Separator
        lines.append("")

        # Summary
        lines.append(self._format_stats(result))

        return '\n'.join(lines)

    def _format_change(self, change: "Change") -> str:
        """
        Format a single change for terminal display.

        Args:
            change: The change to format.

        Returns:
            Formatted change string.
        """
        op = change.op

        if op.value == "added":
            indicator = colorize("+", Color.ADDED, self.use_color)
            path_str = colorize(change.path, Color.PATH, self.use_color)
            value_str = colorize(self._format_value(change.new_value), Color.ADDED, self.use_color)
            return f"  {indicator} {path_str}: {value_str}"

        elif op.value == "removed":
            indicator = colorize("-", Color.REMOVED, self.use_color)
            path_str = colorize(change.path, Color.PATH, self.use_color)
            value_str = colorize(self._format_value(change.old_value), Color.REMOVED, self.use_color)
            return f"  {indicator} {path_str}: {value_str}"

        elif op.value == "type_changed":
            indicator = colorize("~", Color.MODIFIED, self.use_color)
            path_str = colorize(change.path, Color.PATH, self.use_color)
            old_type = colorize(change.old_type or "unknown", Color.REMOVED, self.use_color)
            new_type = colorize(change.new_type or "unknown", Color.ADDED, self.use_color)
            return f"  {indicator} {path_str}: type {old_type} -> {new_type}"

        else:  # modified
            indicator = colorize("~", Color.MODIFIED, self.use_color)
            path_str = colorize(change.path, Color.PATH, self.use_color)
            old_val = colorize(self._format_value(change.old_value), Color.REMOVED, self.use_color)
            new_val = colorize(self._format_value(change.new_value), Color.ADDED, self.use_color)
            return f"  {indicator} {path_str}: {old_val} -> {new_val}"

    def _format_stats(self, result: "DiffResult") -> str:
        """
        Format summary statistics.

        Args:
            result: The diff result.

        Returns:
            Formatted statistics string.
        """
        lines = []
        lines.append(colorize("Summary:", Color.HEADER, self.use_color))
        lines.append(f"  Total changes: {result.total_changes}")

        if result.added_count:
            lines.append(f"  {colorize('+ Added:', Color.ADDED, self.use_color)} {result.added_count}")
        if result.removed_count:
            lines.append(f"  {colorize('- Removed:', Color.REMOVED, self.use_color)} {result.removed_count}")
        if result.modified_count:
            lines.append(f"  {colorize('~ Modified:', Color.MODIFIED, self.use_color)} {result.modified_count}")
        if result.type_changed_count:
            lines.append(f"  {colorize('* Type changed:', Color.MODIFIED, self.use_color)} {result.type_changed_count}")

        lines.append(f"  Max depth: {result.max_depth}")

        return '\n'.join(lines)

    def _header(self, text: str) -> str:
        """
        Format a header line.

        Args:
            text: The header text.

        Returns:
            Formatted header string.
        """
        return colorize(f"=== {text} ===", Color.HEADER, self.use_color)

    @staticmethod
    def _format_value(value) -> str:
        """
        Format a value for display.

        Args:
            value: The value to format.

        Returns:
            String representation of the value.
        """
        if value is None:
            return "null"
        if isinstance(value, str):
            if len(value) > 80:
                return f'"{value[:80]}..."'
            return f'"{value}"'
        if isinstance(value, bool):
            return "true" if value else "false"
        return repr(value)
