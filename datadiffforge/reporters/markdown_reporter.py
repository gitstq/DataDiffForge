"""
Markdown reporter for DataDiffForge.

Produces Markdown formatted diff output with tables and code blocks.
"""

from typing import TYPE_CHECKING

from .base import ReporterInterface

if TYPE_CHECKING:
    from ..core.types import DiffResult


class MarkdownReporter(ReporterInterface):
    """
    Reporter that produces Markdown formatted output.

    Features:
    - Table-based summary statistics
    - Code-fenced change details
    - Clean, readable Markdown formatting
    """

    @property
    def format_name(self) -> str:
        """Return 'markdown'."""
        return "markdown"

    def report(self, result: "DiffResult", **kwargs) -> str:
        """
        Format a DiffResult as a Markdown document.

        Args:
            result: The diff result to format.
            **kwargs: Additional options:
                - stat_only: If True, show only statistics.

        Returns:
            Markdown formatted string.
        """
        stat_only = kwargs.get('stat_only', False)
        lines = []

        # Title
        lines.append(f"# Diff: {result.left_label} vs {result.right_label}")
        lines.append("")

        if not result.has_changes:
            lines.append("_No differences found._")
            return '\n'.join(lines)

        # Summary table
        lines.append("## Summary")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Changes | {result.total_changes} |")
        if result.added_count:
            lines.append(f"| Added | {result.added_count} |")
        if result.removed_count:
            lines.append(f"| Removed | {result.removed_count} |")
        if result.modified_count:
            lines.append(f"| Modified | {result.modified_count} |")
        if result.type_changed_count:
            lines.append(f"| Type Changed | {result.type_changed_count} |")
        lines.append(f"| Max Depth | {result.max_depth} |")
        lines.append("")

        if stat_only:
            return '\n'.join(lines)

        # Changes
        lines.append("## Changes")
        lines.append("")

        # Group changes by type
        op_groups = {}
        for change in result.changes:
            op = change.op.value
            if op not in op_groups:
                op_groups[op] = []
            op_groups[op].append(change)

        # Added changes
        if 'added' in op_groups:
            lines.append("### Added")
            lines.append("")
            lines.append("| Path | Value |")
            lines.append("|------|-------|")
            for change in op_groups['added']:
                path = self._escape_md(change.path)
                value = self._escape_md(self._format_value(change.new_value))
                lines.append(f"| `{path}` | `{value}` |")
            lines.append("")

        # Removed changes
        if 'removed' in op_groups:
            lines.append("### Removed")
            lines.append("")
            lines.append("| Path | Value |")
            lines.append("|------|-------|")
            for change in op_groups['removed']:
                path = self._escape_md(change.path)
                value = self._escape_md(self._format_value(change.old_value))
                lines.append(f"| `{path}` | `{value}` |")
            lines.append("")

        # Modified changes
        if 'modified' in op_groups:
            lines.append("### Modified")
            lines.append("")
            lines.append("| Path | Old Value | New Value |")
            lines.append("|------|-----------|-----------|")
            for change in op_groups['modified']:
                path = self._escape_md(change.path)
                old_val = self._escape_md(self._format_value(change.old_value))
                new_val = self._escape_md(self._format_value(change.new_value))
                lines.append(f"| `{path}` | `{old_val}` | `{new_val}` |")
            lines.append("")

        # Type changed
        if 'type_changed' in op_groups:
            lines.append("### Type Changed")
            lines.append("")
            lines.append("| Path | Old Type | New Type |")
            lines.append("|------|----------|----------|")
            for change in op_groups['type_changed']:
                path = self._escape_md(change.path)
                old_type = self._escape_md(change.old_type or "unknown")
                new_type = self._escape_md(change.new_type or "unknown")
                lines.append(f"| `{path}` | `{old_type}` | `{new_type}` |")
            lines.append("")

        return '\n'.join(lines)

    @staticmethod
    def _escape_md(text: str) -> str:
        """
        Escape Markdown special characters in a string.

        Args:
            text: The text to escape.

        Returns:
            Markdown-escaped string.
        """
        if not isinstance(text, str):
            text = str(text)
        # Escape pipe characters in table cells
        return text.replace('|', '\\|')

    @staticmethod
    def _format_value(value) -> str:
        """
        Format a value for Markdown display.

        Args:
            value: The value to format.

        Returns:
            String representation.
        """
        if value is None:
            return "null"
        if isinstance(value, str):
            if len(value) > 60:
                return f'"{value[:60]}..."'
            return f'"{value}"'
        if isinstance(value, bool):
            return "true" if value else "false"
        return repr(value)
