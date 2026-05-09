"""
Reporters package for DataDiffForge.

Provides format-specific reporters for terminal, JSON, HTML, and Markdown output.
"""

from .base import ReporterInterface
from .terminal import TerminalReporter
from .json_reporter import JsonReporter
from .html_reporter import HtmlReporter
from .markdown_reporter import MarkdownReporter

__all__ = [
    "ReporterInterface",
    "TerminalReporter",
    "JsonReporter",
    "HtmlReporter",
    "MarkdownReporter",
]
