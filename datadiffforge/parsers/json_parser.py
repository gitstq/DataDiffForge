"""
JSON parser with comment stripping support.

Uses the standard json module but adds support for stripping
single-line (# and //) and multi-line (/* ... */) comments
before parsing.
"""

import json
import re
from typing import Any

from .base import ParserInterface


class JsonParser(ParserInterface):
    """
    JSON parser that supports comments in JSON files.

    Strips the following comment styles before parsing:
    - Single-line: # comment
    - Single-line: // comment
    - Multi-line: /* comment */
    """

    @property
    def format_name(self) -> str:
        """Return 'json'."""
        return "json"

    @property
    def file_extensions(self) -> list:
        """Return ['.json']."""
        return [".json"]

    def load(self, content: str) -> Any:
        """
        Parse JSON content, stripping comments first.

        Args:
            content: JSON string content, possibly with comments.

        Returns:
            Parsed Python data structure.

        Raises:
            json.JSONDecodeError: If the content is not valid JSON after stripping comments.
        """
        stripped = self._strip_comments(content)
        return json.loads(stripped)

    def dump(self, data: Any) -> str:
        """
        Serialize data to a formatted JSON string.

        Args:
            data: Python data structure to serialize.

        Returns:
            Formatted JSON string with 2-space indentation.
        """
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)

    @staticmethod
    def _strip_comments(content: str) -> str:
        """
        Remove comments from JSON content.

        Handles:
        - # single-line comments
        - // single-line comments
        - /* ... */ multi-line comments

        Preserves strings that contain comment-like sequences.

        Args:
            content: The JSON content with comments.

        Returns:
            The JSON content with comments removed.
        """
        result = []
        i = 0
        length = len(content)

        while i < length:
            # Check if we're inside a string
            if content[i] == '"':
                # Find the end of the string, handling escape sequences
                j = i + 1
                while j < length:
                    if content[j] == '\\':
                        j += 2  # Skip escaped character
                        continue
                    if content[j] == '"':
                        break
                    j += 1
                # Include the entire string
                result.append(content[i:j + 1])
                i = j + 1
                continue

            # Check for single-line comment: #
            if content[i] == '#' and (i == 0 or content[i - 1] != '\\'):
                # Skip to end of line
                while i < length and content[i] != '\n':
                    i += 1
                continue

            # Check for single-line comment: //
            if (content[i] == '/' and i + 1 < length and content[i + 1] == '/'
                    and (i == 0 or content[i - 1] != '\\')):
                # Skip to end of line
                while i < length and content[i] != '\n':
                    i += 1
                continue

            # Check for multi-line comment: /* ... */
            if (content[i] == '/' and i + 1 < length and content[i + 1] == '*'):
                # Find closing */
                j = i + 2
                while j + 1 < length and not (content[j] == '*' and content[j + 1] == '/'):
                    j += 1
                i = j + 2  # Skip past */
                continue

            # Regular character
            result.append(content[i])
            i += 1

        return ''.join(result)
