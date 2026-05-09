"""
HTML reporter for DataDiffForge.

Produces a self-contained HTML report with inline CSS styling,
featuring side-by-side comparison and collapsible sections.
"""

from typing import TYPE_CHECKING

from .base import ReporterInterface

if TYPE_CHECKING:
    from ..core.types import DiffResult


class HtmlReporter(ReporterInterface):
    """
    Reporter that produces HTML formatted output.

    Features:
    - Self-contained HTML with inline CSS
    - Color-coded changes (green for additions, red for removals, yellow for modifications)
    - Summary statistics section
    - Clean, modern styling
    """

    @property
    def format_name(self) -> str:
        """Return 'html'."""
        return "html"

    def report(self, result: "DiffResult", **kwargs) -> str:
        """
        Format a DiffResult as an HTML document.

        Args:
            result: The diff result to format.
            **kwargs: Additional options:
                - title: Report title (default: "Diff Report").

        Returns:
            Complete HTML document string.
        """
        title = kwargs.get('title', 'Diff Report')

        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            f'<meta charset="UTF-8">',
            f'<title>{self._escape(title)}</title>',
            '<style>',
            self._get_css(),
            '</style>',
            '</head>',
            '<body>',
            f'<div class="container">',
            f'<h1>{self._escape(title)}</h1>',
            f'<p class="subtitle">{self._escape(result.left_label)} vs {self._escape(result.right_label)}</p>',
        ]

        if not result.has_changes:
            html_parts.append('<div class="no-changes">No differences found.</div>')
        else:
            # Summary section
            html_parts.append(self._format_summary(result))

            # Changes section
            html_parts.append('<div class="changes">')
            html_parts.append('<h2>Changes</h2>')
            for i, change in enumerate(result.changes):
                html_parts.append(self._format_change(change, i))
            html_parts.append('</div>')

        html_parts.extend([
            '</div>',
            '</body>',
            '</html>',
        ])

        return '\n'.join(html_parts)

    def _format_summary(self, result: "DiffResult") -> str:
        """
        Format the summary statistics section.

        Args:
            result: The diff result.

        Returns:
            HTML string for the summary section.
        """
        parts = [
            '<div class="summary">',
            '<h2>Summary</h2>',
            '<table class="stats-table">',
            '<tr><td class="stat-label">Total Changes</td><td class="stat-value">{}</td></tr>'.format(
                result.total_changes),
        ]

        if result.added_count:
            parts.append(
                '<tr><td class="stat-label"><span class="badge badge-added">Added</span></td>'
                '<td class="stat-value">{}</td></tr>'.format(result.added_count))
        if result.removed_count:
            parts.append(
                '<tr><td class="stat-label"><span class="badge badge-removed">Removed</span></td>'
                '<td class="stat-value">{}</td></tr>'.format(result.removed_count))
        if result.modified_count:
            parts.append(
                '<tr><td class="stat-label"><span class="badge badge-modified">Modified</span></td>'
                '<td class="stat-value">{}</td></tr>'.format(result.modified_count))
        if result.type_changed_count:
            parts.append(
                '<tr><td class="stat-label"><span class="badge badge-type">Type Changed</span></td>'
                '<td class="stat-value">{}</td></tr>'.format(result.type_changed_count))

        parts.append(
            '<tr><td class="stat-label">Max Depth</td><td class="stat-value">{}</td></tr>'.format(
                result.max_depth))
        parts.append('</table></div>')

        return '\n'.join(parts)

    def _format_change(self, change, index: int) -> str:
        """
        Format a single change as an HTML element.

        Args:
            change: The change to format.
            index: The change index.

        Returns:
            HTML string for the change.
        """
        op = change.op.value
        op_class = {
            'added': 'change-added',
            'removed': 'change-removed',
            'modified': 'change-modified',
            'type_changed': 'change-type',
        }.get(op, 'change-modified')

        indicator = {
            'added': '+',
            'removed': '-',
            'modified': '~',
            'type_changed': '*',
        }.get(op, '~')

        parts = [
            f'<div class="change {op_class}">',
            f'<div class="change-header">',
            f'<span class="change-indicator">{indicator}</span>',
            f'<span class="change-path">{self._escape(change.path)}</span>',
            f'</div>',
            f'<div class="change-details">',
        ]

        if op == 'added':
            parts.append(
                f'<div class="change-new">{self._escape(self._format_value(change.new_value))}</div>')
        elif op == 'removed':
            parts.append(
                f'<div class="change-old">{self._escape(self._format_value(change.old_value))}</div>')
        elif op == 'type_changed':
            parts.append(
                f'<div class="change-old">{self._escape(change.old_type or "unknown")} '
                f'({self._escape(self._format_value(change.old_value))})</div>')
            parts.append(
                f'<div class="change-new">{self._escape(change.new_type or "unknown")} '
                f'({self._escape(self._format_value(change.new_value))})</div>')
        else:
            parts.append(
                f'<div class="change-old">{self._escape(self._format_value(change.old_value))}</div>')
            parts.append(
                f'<div class="change-new">{self._escape(self._format_value(change.new_value))}</div>')

        parts.extend(['</div>', '</div>'])

        return '\n'.join(parts)

    @staticmethod
    def _get_css() -> str:
        """
        Return the inline CSS styles for the HTML report.

        Returns:
            CSS string.
        """
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 { color: #2c3e50; margin-bottom: 5px; font-size: 24px; }
        .subtitle { color: #7f8c8d; margin-bottom: 20px; font-size: 14px; }
        h2 { color: #2c3e50; margin-bottom: 15px; font-size: 18px; border-bottom: 2px solid #eee; padding-bottom: 8px; }
        .no-changes { color: #27ae60; font-size: 16px; padding: 20px; text-align: center; }
        .summary { margin-bottom: 25px; }
        .stats-table { width: 100%; border-collapse: collapse; }
        .stats-table td { padding: 8px 12px; border-bottom: 1px solid #eee; }
        .stat-label { font-weight: 500; }
        .stat-value { text-align: right; font-family: 'Courier New', monospace; }
        .badge {
            display: inline-block; padding: 2px 8px; border-radius: 3px;
            font-size: 12px; font-weight: 500; color: white;
        }
        .badge-added { background: #27ae60; }
        .badge-removed { background: #e74c3c; }
        .badge-modified { background: #f39c12; }
        .badge-type { background: #9b59b6; }
        .changes { margin-top: 10px; }
        .change {
            margin-bottom: 8px; border-radius: 4px; overflow: hidden;
            border-left: 4px solid #ccc;
        }
        .change-added { border-left-color: #27ae60; background: #f0fff4; }
        .change-removed { border-left-color: #e74c3c; background: #fff5f5; }
        .change-modified { border-left-color: #f39c12; background: #fffbf0; }
        .change-type { border-left-color: #9b59b6; background: #f8f0ff; }
        .change-header { padding: 8px 12px; display: flex; align-items: center; gap: 8px; }
        .change-indicator {
            font-family: 'Courier New', monospace; font-weight: bold; font-size: 14px;
            width: 20px; text-align: center;
        }
        .change-added .change-indicator { color: #27ae60; }
        .change-removed .change-indicator { color: #e74c3c; }
        .change-modified .change-indicator { color: #f39c12; }
        .change-type .change-indicator { color: #9b59b6; }
        .change-path { font-family: 'Courier New', monospace; font-size: 13px; color: #555; }
        .change-details { padding: 4px 12px 8px 40px; font-family: 'Courier New', monospace; font-size: 13px; }
        .change-old { color: #e74c3c; }
        .change-old::before { content: '- '; color: #999; }
        .change-new { color: #27ae60; }
        .change-new::before { content: '+ '; color: #999; }
        """

    @staticmethod
    def _escape(text: str) -> str:
        """
        Escape HTML special characters.

        Args:
            text: The text to escape.

        Returns:
            HTML-escaped string.
        """
        if not isinstance(text, str):
            text = str(text)
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    @staticmethod
    def _format_value(value) -> str:
        """
        Format a value for HTML display.

        Args:
            value: The value to format.

        Returns:
            String representation.
        """
        if value is None:
            return "null"
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return "true" if value else "false"
        return repr(value)
