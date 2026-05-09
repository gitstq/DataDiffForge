"""
Simple regex-based YAML parser.

Implements a minimal YAML parser that handles common cases:
- Mappings (key: value)
- Sequences (- item)
- Strings (quoted and unquoted)
- Numbers (int and float)
- Booleans (true/false/yes/no)
- Null values (null/~)
- Nested structures (2-space indent)

Does NOT handle all YAML edge cases (anchors, aliases, complex tags, etc.).
"""

import re
from typing import Any, List, Optional, Tuple

from .base import ParserInterface


class YamlParser(ParserInterface):
    """
    Simple YAML parser using regex-based line-by-line parsing.

    Supports common YAML constructs but is not a full YAML 1.2 implementation.
    Suitable for configuration files and simple data structures.
    """

    @property
    def format_name(self) -> str:
        """Return 'yaml'."""
        return "yaml"

    @property
    def file_extensions(self) -> list:
        """Return ['.yaml', '.yml']."""
        return [".yaml", ".yml"]

    def load(self, content: str) -> Any:
        """
        Parse YAML content into a Python data structure.

        Args:
            content: YAML string content.

        Returns:
            Parsed Python data structure (dict, list, or primitive).
        """
        lines = content.split('\n')
        # Remove empty lines and comments, but preserve them for indentation tracking
        processed_lines: List[Tuple[int, str]] = []
        for line in lines:
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            indent = len(line) - len(stripped)
            processed_lines.append((indent, stripped))

        if not processed_lines:
            return {}

        result, _ = self._parse_block(processed_lines, 0, 0)
        return result

    def dump(self, data: Any, indent: int = 0) -> str:
        """
        Serialize a Python data structure to a YAML string.

        Args:
            data: Python data structure to serialize.
            indent: Current indentation level (for recursion).

        Returns:
            YAML formatted string.
        """
        lines = self._dump_value(data, indent)
        # Remove trailing empty line if present
        result = '\n'.join(lines)
        if result.endswith('\n'):
            result = result[:-1]
        return result + '\n'

    def _parse_block(
        self,
        lines: List[Tuple[int, str]],
        start: int,
        base_indent: int,
    ) -> Tuple[Any, int]:
        """
        Parse a block of YAML lines at a given indentation level.

        Args:
            lines: List of (indent, content) tuples.
            start: Starting index in the lines list.
            base_indent: Expected indentation level for this block.

        Returns:
            A tuple of (parsed_value, next_index).
        """
        if start >= len(lines):
            return None, start

        # Check if this block is a sequence (starts with -)
        if lines[start][1].startswith('- '):
            return self._parse_sequence(lines, start, base_indent)

        # Otherwise, it's a mapping
        return self._parse_mapping(lines, start, base_indent)

    def _parse_mapping(
        self,
        lines: List[Tuple[int, str]],
        start: int,
        base_indent: int,
    ) -> Tuple[dict, int]:
        """
        Parse a YAML mapping block.

        Args:
            lines: List of (indent, content) tuples.
            start: Starting index.
            base_indent: Expected indentation level.

        Returns:
            A tuple of (parsed_dict, next_index).
        """
        result = {}
        i = start

        while i < len(lines):
            indent, content = lines[i]

            # If indentation is less than base, we've exited this block
            if indent < base_indent:
                break

            # If indentation is greater, it belongs to a sub-block (handled by caller)
            if indent > base_indent:
                i += 1
                continue

            # Parse key: value
            match = re.match(r'^([^:]+?):\s*(.*)', content)
            if not match:
                i += 1
                continue

            key = self._parse_scalar(match.group(1).strip())
            value_str = match.group(2).strip()

            if not value_str:
                # Value is on the next line(s) - could be a nested block
                if i + 1 < len(lines) and lines[i + 1][0] > indent:
                    value, i = self._parse_block(lines, i + 1, lines[i + 1][0])
                    result[key] = value
                else:
                    result[key] = None
                    i += 1
            elif value_str.startswith('|') or value_str.startswith('>'):
                # Multi-line string (simplified handling)
                multiline_lines = []
                i += 1
                while i < len(lines) and lines[i][0] > indent:
                    multiline_lines.append(lines[i][1])
                    i += 1
                result[key] = '\n'.join(multiline_lines)
            else:
                # Inline value
                result[key] = self._parse_scalar(value_str)
                i += 1

        return result, i

    def _parse_sequence(
        self,
        lines: List[Tuple[int, str]],
        start: int,
        base_indent: int,
    ) -> Tuple[list, int]:
        """
        Parse a YAML sequence block.

        Args:
            lines: List of (indent, content) tuples.
            start: Starting index.
            base_indent: Expected indentation level.

        Returns:
            A tuple of (parsed_list, next_index).
        """
        result = []
        i = start

        while i < len(lines):
            indent, content = lines[i]

            if indent < base_indent:
                break

            if indent > base_indent:
                i += 1
                continue

            if not content.startswith('- '):
                break

            item_str = content[2:].strip()

            if not item_str:
                # Item value is on subsequent lines
                if i + 1 < len(lines) and lines[i + 1][0] > indent:
                    value, i = self._parse_block(lines, i + 1, lines[i + 1][0])
                    result.append(value)
                else:
                    result.append(None)
                    i += 1
            elif item_str.startswith('- '):
                # Nested sequence inline
                sub_items = [self._parse_scalar(item_str[2:].strip())]
                i += 1
                while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith('- '):
                    sub_items.append(self._parse_scalar(lines[i][1][2:].strip()))
                    i += 1
                result.append(sub_items)
            else:
                # Check if this is a mapping item (key: value after -)
                key_match = re.match(r'^([^:]+?):\s*(.*)', item_str)
                if key_match:
                    key = self._parse_scalar(key_match.group(1).strip())
                    val_str = key_match.group(2).strip()
                    if not val_str and i + 1 < len(lines) and lines[i + 1][0] > indent:
                        value, i = self._parse_block(lines, i + 1, lines[i + 1][0])
                        result.append({key: value})
                    else:
                        result.append({key: self._parse_scalar(val_str)})
                        i += 1
                else:
                    result.append(self._parse_scalar(item_str))
                    i += 1

        return result, i

    def _parse_scalar(self, value: str) -> Any:
        """
        Parse a scalar YAML value into the appropriate Python type.

        Handles:
        - Quoted strings (single and double)
        - Numbers (int and float)
        - Booleans (true/false/yes/no/on/off)
        - Null values (null/~)

        Args:
            value: The string value to parse.

        Returns:
            The parsed Python value.
        """
        if not value:
            return ""

        # Quoted string
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        # Null
        if value.lower() in ('null', '~', ''):
            return None

        # Boolean
        if value.lower() in ('true', 'yes', 'on'):
            return True
        if value.lower() in ('false', 'no', 'off'):
            return False

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # Plain string
        return value

    def _dump_value(self, data: Any, indent: int) -> List[str]:
        """
        Serialize a value to YAML lines.

        Args:
            data: The value to serialize.
            indent: Current indentation level.

        Returns:
            List of YAML lines.
        """
        prefix = '  ' * indent

        if data is None:
            return [f"{prefix}null"]

        if isinstance(data, bool):
            return [f"{prefix}{'true' if data else 'false'}"]

        if isinstance(data, int):
            return [f"{prefix}{data}"]

        if isinstance(data, float):
            return [f"{prefix}{data}"]

        if isinstance(data, str):
            # Check if string needs quoting
            if any(c in data for c in ':#{}[],&*?|->!%@`\'"\\'):
                escaped = data.replace("'", "''")
                return [f"{prefix}'{escaped}'"]
            return [f"{prefix}{data}"]

        if isinstance(data, list):
            lines = []
            for item in data:
                if isinstance(item, dict):
                    if item:
                        first_key = list(item.keys())[0]
                        first_val = item[first_key]
                        if isinstance(first_val, (dict, list)):
                            lines.append(f"{prefix}- {first_key}:")
                            sub_lines = self._dump_value(first_val, indent + 2)
                            lines.extend(sub_lines)
                            for key in list(item.keys())[1:]:
                                lines.append(f"{'  ' * (indent + 1)}{key}:")
                                sub_lines = self._dump_value(item[key], indent + 2)
                                lines.extend(sub_lines)
                        else:
                            lines.append(f"{prefix}- {first_key}: {self._format_scalar(first_val)}")
                            for key in list(item.keys())[1:]:
                                lines.append(f"{'  ' * (indent + 1)}{key}: {self._format_scalar(item[key])}")
                    else:
                        lines.append(f"{prefix}- {{}}")
                elif isinstance(item, list):
                    lines.append(f"{prefix}-")
                    sub_lines = self._dump_value(item, indent + 1)
                    lines.extend(sub_lines)
                else:
                    lines.append(f"{prefix}- {self._format_scalar(item)}")
            return lines

        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                formatted_key = self._format_scalar(str(key))
                if isinstance(value, dict):
                    if value:
                        lines.append(f"{prefix}{formatted_key}:")
                        sub_lines = self._dump_value(value, indent + 1)
                        lines.extend(sub_lines)
                    else:
                        lines.append(f"{prefix}{formatted_key}: {{}}")
                elif isinstance(value, list):
                    if value:
                        lines.append(f"{prefix}{formatted_key}:")
                        sub_lines = self._dump_value(value, indent + 1)
                        lines.extend(sub_lines)
                    else:
                        lines.append(f"{prefix}{formatted_key}: []")
                else:
                    lines.append(f"{prefix}{formatted_key}: {self._format_scalar(value)}")
            return lines

        # Fallback
        return [f"{prefix}{data}"]

    def _format_scalar(self, value: Any) -> str:
        """
        Format a scalar value for YAML output.

        Args:
            value: The value to format.

        Returns:
            Formatted string representation.
        """
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            if any(c in value for c in ':#{}[],&*?|->!%@`\'"\\ \t\n'):
                escaped = value.replace("'", "''")
                return f"'{escaped}'"
            return value
        return str(value)
