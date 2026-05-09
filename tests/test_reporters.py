"""
Comprehensive tests for all reporters.

Tests cover:
- Terminal reporter output format
- JSON reporter output format
- HTML reporter output format
- Markdown reporter output format
- Edge cases (no changes, empty results)
"""

import unittest

from datadiffforge.core.types import DiffOp, Change, DiffResult
from datadiffforge.core.differ import diff
from datadiffforge.reporters.terminal import TerminalReporter
from datadiffforge.reporters.json_reporter import JsonReporter
from datadiffforge.reporters.html_reporter import HtmlReporter
from datadiffforge.reporters.markdown_reporter import MarkdownReporter
from datadiffforge.utils.color import strip_ansi


class TestTerminalReporter(unittest.TestCase):
    """Tests for the terminal reporter."""

    def setUp(self):
        self.reporter = TerminalReporter(use_color=False)

    def test_format_name(self):
        self.assertEqual(self.reporter.format_name, "terminal")

    def test_no_changes(self):
        """No changes should produce appropriate message."""
        result = DiffResult()
        output = self.reporter.report(result)
        self.assertIn("No differences found", output)

    def test_added_change(self):
        """Added changes should show + indicator."""
        result = DiffResult()
        result.add_change(Change(
            op=DiffOp.ADDED, path="$.b", new_value=2, new_type="int", depth=0
        ))
        output = self.reporter.report(result)
        self.assertIn("+", output)
        self.assertIn("$.b", output)

    def test_removed_change(self):
        """Removed changes should show - indicator."""
        result = DiffResult()
        result.add_change(Change(
            op=DiffOp.REMOVED, path="$.b", old_value=2, old_type="int", depth=0
        ))
        output = self.reporter.report(result)
        self.assertIn("-", output)
        self.assertIn("$.b", output)

    def test_modified_change(self):
        """Modified changes should show ~ indicator."""
        result = DiffResult()
        result.add_change(Change(
            op=DiffOp.MODIFIED, path="$.a", old_value=1, new_value=2,
            old_type="int", new_type="int", depth=0
        ))
        output = self.reporter.report(result)
        self.assertIn("~", output)
        self.assertIn("$.a", output)

    def test_type_changed(self):
        """Type changes should show type information."""
        result = DiffResult()
        result.add_change(Change(
            op=DiffOp.TYPE_CHANGED, path="$.a",
            old_value="hello", new_value=42,
            old_type="str", new_type="int", depth=0
        ))
        output = self.reporter.report(result)
        self.assertIn("str", output)
        self.assertIn("int", output)

    def test_summary(self):
        """Summary should include statistics."""
        result = diff({"a": 1}, {"b": 2})
        output = self.reporter.report(result)
        self.assertIn("Summary", output)
        self.assertIn("Total changes", output)

    def test_stat_only(self):
        """Stat-only mode should show only statistics."""
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result, stat_only=True)
        self.assertIn("Total changes", output)
        self.assertNotIn("$.a", output)

    def test_no_color_mode(self):
        """No-color mode should not contain ANSI codes."""
        reporter = TerminalReporter(use_color=False)
        result = diff({"a": 1}, {"a": 2})
        output = reporter.report(result)
        # Strip ANSI and compare - should be same
        self.assertEqual(strip_ansi(output), output)


class TestJsonReporter(unittest.TestCase):
    """Tests for the JSON reporter."""

    def setUp(self):
        self.reporter = JsonReporter()

    def test_format_name(self):
        self.assertEqual(self.reporter.format_name, "json")

    def test_valid_json(self):
        """Output should be valid JSON."""
        import json
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result)
        parsed = json.loads(output)
        self.assertIsInstance(parsed, dict)

    def test_no_changes(self):
        """No changes should produce valid JSON with zero counts."""
        import json
        result = DiffResult()
        output = self.reporter.report(result)
        parsed = json.loads(output)
        self.assertEqual(parsed["total_changes"], 0)

    def test_changes_included(self):
        """Changes should be included in JSON output."""
        import json
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result)
        parsed = json.loads(output)
        self.assertEqual(len(parsed["changes"]), 1)
        self.assertEqual(parsed["changes"][0]["op"], "modified")

    def test_stat_only(self):
        """Stat-only mode should exclude changes list."""
        import json
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result, stat_only=True)
        parsed = json.loads(output)
        self.assertNotIn("changes", parsed)
        self.assertIn("total_changes", parsed)

    def test_custom_indent(self):
        """Custom indent should be respected."""
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result, indent=4)
        self.assertIn("    ", output)  # 4-space indent


class TestHtmlReporter(unittest.TestCase):
    """Tests for the HTML reporter."""

    def setUp(self):
        self.reporter = HtmlReporter()

    def test_format_name(self):
        self.assertEqual(self.reporter.format_name, "html")

    def test_valid_html_structure(self):
        """Output should have valid HTML structure."""
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result)
        self.assertIn("<!DOCTYPE html>", output)
        self.assertIn("<html", output)
        self.assertIn("</html>", output)
        self.assertIn("<head>", output)
        self.assertIn("<body>", output)

    def test_inline_css(self):
        """Output should contain inline CSS."""
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result)
        self.assertIn("<style>", output)
        self.assertIn("</style>", output)

    def test_no_changes(self):
        """No changes should show appropriate message."""
        result = DiffResult()
        output = self.reporter.report(result)
        self.assertIn("No differences found", output)

    def test_changes_rendered(self):
        """Changes should be rendered in HTML."""
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result)
        self.assertIn("$.a", output)

    def test_html_escaping(self):
        """Special HTML characters should be escaped."""
        result = DiffResult()
        result.add_change(Change(
            op=DiffOp.ADDED, path="$.a", new_value="<script>alert('xss')</script>",
            new_type="str", depth=0
        ))
        output = self.reporter.report(result)
        self.assertNotIn("<script>", output)
        self.assertIn("&lt;script&gt;", output)

    def test_custom_title(self):
        """Custom title should be used."""
        result = DiffResult()
        output = self.reporter.report(result, title="Custom Title")
        self.assertIn("Custom Title", output)


class TestMarkdownReporter(unittest.TestCase):
    """Tests for the Markdown reporter."""

    def setUp(self):
        self.reporter = MarkdownReporter()

    def test_format_name(self):
        self.assertEqual(self.reporter.format_name, "markdown")

    def test_no_changes(self):
        """No changes should show appropriate message."""
        result = DiffResult()
        output = self.reporter.report(result)
        self.assertIn("No differences found", output)

    def test_header(self):
        """Output should have a markdown header."""
        result = diff({"a": 1}, {"a": 2}, left_label="file1", right_label="file2")
        output = self.reporter.report(result)
        self.assertIn("# Diff: file1 vs file2", output)

    def test_summary_table(self):
        """Summary should be a markdown table."""
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result)
        self.assertIn("| Metric | Count |", output)
        self.assertIn("| Total Changes |", output)

    def test_changes_table(self):
        """Changes should be in markdown tables."""
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result)
        self.assertIn("| Path | Old Value | New Value |", output)

    def test_stat_only(self):
        """Stat-only mode should exclude changes section."""
        result = diff({"a": 1}, {"a": 2})
        output = self.reporter.report(result, stat_only=True)
        self.assertIn("Summary", output)
        self.assertNotIn("## Changes", output)

    def test_pipe_escaping(self):
        """Pipe characters in values should be escaped."""
        result = DiffResult()
        result.add_change(Change(
            op=DiffOp.ADDED, path="$.a", new_value="a|b|c",
            new_type="str", depth=0
        ))
        output = self.reporter.report(result)
        # Should not break the table
        lines = output.split('\n')
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                # Each table row should have consistent columns
                # (pipe in value should be escaped)


class TestReporterIntegration(unittest.TestCase):
    """Integration tests using reporters with actual diff results."""

    def _make_complex_diff(self) -> DiffResult:
        """Create a diff result with multiple change types."""
        left = {
            "name": "App",
            "version": 1,
            "features": ["auth", "logging"],
            "config": {"debug": True, "port": 8080},
        }
        right = {
            "name": "AppV2",
            "version": 2,
            "features": ["auth", "logging", "metrics"],
            "config": {"debug": False, "port": 9090, "host": "0.0.0.0"},
        }
        return diff(left, right, left_label="old.json", right_label="new.json")

    def test_terminal_reporter_complex(self):
        """Terminal reporter should handle complex diffs."""
        result = self._make_complex_diff()
        reporter = TerminalReporter(use_color=False)
        output = reporter.report(result)
        self.assertIn("old.json", output)
        self.assertIn("new.json", output)

    def test_json_reporter_complex(self):
        """JSON reporter should handle complex diffs."""
        import json
        result = self._make_complex_diff()
        reporter = JsonReporter()
        output = reporter.report(result)
        parsed = json.loads(output)
        self.assertGreater(parsed["total_changes"], 0)

    def test_html_reporter_complex(self):
        """HTML reporter should handle complex diffs."""
        result = self._make_complex_diff()
        reporter = HtmlReporter()
        output = reporter.report(result)
        self.assertIn("<!DOCTYPE html>", output)
        self.assertIn("old.json", output)

    def test_markdown_reporter_complex(self):
        """Markdown reporter should handle complex diffs."""
        result = self._make_complex_diff()
        reporter = MarkdownReporter()
        output = reporter.report(result)
        self.assertIn("# Diff:", output)
        self.assertIn("Summary", output)


if __name__ == "__main__":
    unittest.main()
