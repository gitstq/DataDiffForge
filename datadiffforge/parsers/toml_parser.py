"""
Simple regex-based TOML parser.

Implements a minimal TOML parser that handles common cases:
- [sections] and [sections.subsections]
- key = value pairs
- String values (double-quoted, single-quoted)
- Integer and float numbers
- Boolean values (true/false)
- Arrays (inline)
- Inline tables
- Comments (#)

Does NOT handle all TOML edge cases (multi-line strings, arrays of tables, etc.).
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from .base import ParserInterface


class TomlParser(ParserInterface):
    """
    Simple TOML parser using regex-based line-by-line parsing.

    Supports common TOML constructs but is not a full TOML 1.0 implementation.
    Suitable for configuration files like pyproject.toml, Cargo.toml, etc.
    """

    @property
    def format_name(self) -> str:
        """Return 'toml'."""
        return "toml"

    @property
    def file_extensions(self) -> list:
        """Return ['.toml']."""
        return [".toml"]

    def load(self, content: str) -> Any:
        """
        Parse TOML content into a Python dictionary.

        Args:
            content: TOML string content.

        Returns:
            Parsed Python dictionary.
        """
        result: Dict[str, Any] = {}
        current_section: List[str] = []

        for line in content.split('\n'):
            # Strip comments (but not inside strings)
            stripped = self._strip_comment(line).strip()

            if not stripped:
                continue

            # Section header: [section] or [section.subsection]
            section_match = re.match(r'^\[([^\]]+)\]$', stripped)
            if section_match:
                section_path = section_match.group(1).strip()
                current_section = [s.strip() for s in section_path.split('.')]
                # Ensure the section path exists in result
                self._ensure_path(result, current_section)
                continue

            # Key-value pair: key = value
            kv_match = re.match(r'^([^=]+?)\s*=\s*(.+)$', stripped)
            if kv_match:
                key = kv_match.group(1).strip()
                value_str = kv_match.group(2).strip()
                value = self._parse_value(value_str)

                # Set the value at the current section path
                self._set_nested(result, current_section + [key], value)
                continue

        return result

    def dump(self, data: Any) -> str:
        """
        Serialize a Python dictionary to TOML format.

        Args:
            data: Python dictionary to serialize.

        Returns:
            TOML formatted string.
        """
        lines = []
        self._dump_section(data, [], lines)
        result = '\n'.join(lines)
        # Ensure file ends with newline
        if result and not result.endswith('\n'):
            result += '\n'
        return result

    def _parse_value(self, value_str: str) -> Any:
        """
        Parse a TOML value string into the appropriate Python type.

        Args:
            value_str: The value string to parse.

        Returns:
            Parsed Python value.
        """
        value_str = value_str.strip()

        # String: double-quoted
        if value_str.startswith('"') and value_str.endswith('"'):
            return self._unescape_string(value_str[1:-1])

        # String: single-quoted (literal string in TOML)
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]

        # Boolean
        if value_str == 'true':
            return True
        if value_str == 'false':
            return False

        # Array
        if value_str.startswith('[') and value_str.endswith(']'):
            return self._parse_array(value_str)

        # Inline table
        if value_str.startswith('{') and value_str.endswith('}'):
            return self._parse_inline_table(value_str)

        # Integer
        try:
            return int(value_str)
        except ValueError:
            pass

        # Float
        try:
            return float(value_str)
        except ValueError:
            pass

        # Bare string (unquoted)
        return value_str

    def _parse_array(self, value_str: str) -> List[Any]:
        """
        Parse a TOML inline array.

        Args:
            value_str: The array string (e.g., "[1, 2, 3]").

        Returns:
            List of parsed values.
        """
        # Remove outer brackets
        inner = value_str[1:-1].strip()
        if not inner:
            return []

        # Split by commas, respecting nested structures
        items = self._split_by_comma(inner)
        return [self._parse_value(item.strip()) for item in items]

    def _parse_inline_table(self, value_str: str) -> Dict[str, Any]:
        """
        Parse a TOML inline table.

        Args:
            value_str: The inline table string (e.g., "{a = 1, b = 2}").

        Returns:
            Parsed dictionary.
        """
        inner = value_str[1:-1].strip()
        if not inner:
            return {}

        result = {}
        items = self._split_by_comma(inner)
        for item in items:
            item = item.strip()
            kv_match = re.match(r'^([^=]+?)\s*=\s*(.+)$', item)
            if kv_match:
                key = kv_match.group(1).strip()
                value = self._parse_value(kv_match.group(2).strip())
                result[key] = value

        return result

    @staticmethod
    def _split_by_comma(s: str) -> List[str]:
        """
        Split a string by commas, respecting nested brackets and quotes.

        Args:
            s: The string to split.

        Returns:
            List of string segments.
        """
        parts = []
        current = []
        depth_bracket = 0
        depth_brace = 0
        in_double_quote = False
        in_single_quote = False
        i = 0

        while i < len(s):
            c = s[i]

            if in_double_quote:
                current.append(c)
                if c == '\\' and i + 1 < len(s):
                    current.append(s[i + 1])
                    i += 2
                    continue
                if c == '"':
                    in_double_quote = False
                i += 1
                continue

            if in_single_quote:
                current.append(c)
                if c == "'":
                    in_single_quote = False
                i += 1
                continue

            if c == '"':
                in_double_quote = True
                current.append(c)
            elif c == "'":
                in_single_quote = True
                current.append(c)
            elif c == '[':
                depth_bracket += 1
                current.append(c)
            elif c == ']':
                depth_bracket -= 1
                current.append(c)
            elif c == '{':
                depth_brace += 1
                current.append(c)
            elif c == '}':
                depth_brace -= 1
                current.append(c)
            elif c == ',' and depth_bracket == 0 and depth_brace == 0:
                parts.append(''.join(current))
                current = []
            else:
                current.append(c)

            i += 1

        if current:
            parts.append(''.join(current))

        return parts

    @staticmethod
    def _strip_comment(line: str) -> str:
        """
        Strip inline comments from a TOML line.

        Handles # comments that are not inside strings.

        Args:
            line: The line to strip comments from.

        Returns:
            The line with comments removed.
        """
        in_double_quote = False
        in_single_quote = False
        i = 0

        while i < len(line):
            c = line[i]

            if in_double_quote:
                if c == '\\' and i + 1 < len(line):
                    i += 2
                    continue
                if c == '"':
                    in_double_quote = False
                i += 1
                continue

            if in_single_quote:
                if c == "'":
                    in_single_quote = False
                i += 1
                continue

            if c == '"':
                in_double_quote = True
            elif c == "'":
                in_single_quote = True
            elif c == '#':
                return line[:i]

            i += 1

        return line

    @staticmethod
    def _unescape_string(s: str) -> str:
        """
        Process TOML escape sequences in a double-quoted string.

        Args:
            s: The string with escape sequences.

        Returns:
            The unescaped string.
        """
        result = []
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                next_c = s[i + 1]
                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"',
                    'b': '\b',
                    'f': '\f',
                }
                result.append(escape_map.get(next_c, next_c))
                i += 2
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)

    @staticmethod
    def _ensure_path(data: dict, path: List[str]) -> None:
        """
        Ensure that a nested path exists in a dictionary.

        Creates intermediate dictionaries as needed.

        Args:
            data: The dictionary to modify.
            path: List of keys forming the path.
        """
        current = data
        for key in path:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

    @staticmethod
    def _set_nested(data: dict, path: List[str], value: Any) -> None:
        """
        Set a value at a nested path in a dictionary.

        Args:
            data: The dictionary to modify.
            path: List of keys forming the path.
            value: The value to set.
        """
        current = data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value

    def _dump_section(self, data: Any, path: List[str], lines: List[str]) -> None:
        """
        Recursively dump a section of data as TOML.

        Args:
            data: The data to dump.
            path: Current section path.
            lines: List to append output lines to.
        """
        if not isinstance(data, dict):
            return

        # Separate simple values from nested dicts
        simple_items: List[Tuple[str, Any]] = []
        nested_items: List[Tuple[str, Any]] = []

        for key, value in data.items():
            if isinstance(value, dict) and value:
                nested_items.append((key, value))
            else:
                simple_items.append((key, value))

        # Write section header if we're in a subsection
        if path:
            section_name = '.'.join(path)
            lines.append(f"[{section_name}]")

        # Write simple key-value pairs
        for key, value in simple_items:
            lines.append(f"{key} = {self._format_value(value)}")

        # Add blank line between sections if we have nested items
        if nested_items and simple_items:
            lines.append('')

        # Recursively write nested sections
        for i, (key, value) in enumerate(nested_items):
            self._dump_section(value, path + [key], lines)
            if i < len(nested_items) - 1:
                lines.append('')

    def _format_value(self, value: Any) -> str:
        """
        Format a Python value as a TOML value string.

        Args:
            value: The value to format.

        Returns:
            TOML-formatted string representation.
        """
        if value is None:
            return '""'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return str(value)
        if isinstance(value, str):
            # Escape and quote the string
            escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
            return f'"{escaped}"'
        if isinstance(value, list):
            items = [self._format_value(item) for item in value]
            return f"[{', '.join(items)}]"
        if isinstance(value, dict):
            items = [f"{k} = {self._format_value(v)}" for k, v in value.items()]
            return '{' + ', '.join(items) + '}'
        return f'"{value}"'
