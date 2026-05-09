"""
CSV parser with header detection and type inference.

Uses the standard csv module with enhancements for automatic
type detection and header row identification.
"""

import csv
import io
from typing import Any, List, Optional

from .base import ParserInterface


class CsvParser(ParserInterface):
    """
    CSV parser with automatic header detection and type inference.

    Features:
    - Auto-detects header rows by checking if all values are strings
    - Infers column types (int, float, bool, string)
    - Supports comma, semicolon, and tab delimiters
    - Returns data as a list of dicts (one per row)
    """

    @property
    def format_name(self) -> str:
        """Return 'csv'."""
        return "csv"

    @property
    def file_extensions(self) -> list:
        """Return ['.csv', '.tsv']."""
        return [".csv", ".tsv"]

    def load(self, content: str) -> Any:
        """
        Parse CSV content into a list of dictionaries.

        Automatically detects headers and infers value types.

        Args:
            content: CSV string content.

        Returns:
            A list of dicts, where each dict represents a row.
        """
        # Detect delimiter
        delimiter = self._detect_delimiter(content)

        reader = csv.reader(io.StringIO(content), delimiter=delimiter)
        rows = list(reader)

        if not rows:
            return []

        # Filter out completely empty rows
        rows = [row for row in rows if any(cell.strip() for cell in row)]

        if not rows:
            return []

        # Detect if first row is a header
        has_header = self._detect_header(rows)

        if has_header:
            headers = [h.strip() for h in rows[0]]
            data_rows = rows[1:]
        else:
            # Generate column names
            headers = [f"column_{i}" for i in range(len(rows[0]))]
            data_rows = rows

        # Convert rows to list of dicts with type inference
        result = []
        for row in data_rows:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = self._infer_type(row[i].strip())
                else:
                    row_dict[header] = None
            result.append(row_dict)

        return result

    def dump(self, data: Any) -> str:
        """
        Serialize a list of dictionaries to CSV format.

        Args:
            data: A list of dicts to serialize.

        Returns:
            CSV formatted string.
        """
        if not data:
            return ""

        # Collect all headers from all rows
        headers: List[str] = []
        seen = set()
        for row in data:
            if isinstance(row, dict):
                for key in row.keys():
                    if key not in seen:
                        headers.append(key)
                        seen.add(key)

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(headers)

        # Write data rows
        for row in data:
            if isinstance(row, dict):
                csv_row = [self._format_value(row.get(h)) for h in headers]
            else:
                csv_row = [self._format_value(row)]
            writer.writerow(csv_row)

        return output.getvalue()

    @staticmethod
    def _detect_delimiter(content: str) -> str:
        """
        Detect the delimiter used in CSV content.

        Checks for comma, semicolon, and tab delimiters by counting
        their occurrences in the first few lines.

        Args:
            content: CSV content string.

        Returns:
            The detected delimiter character.
        """
        first_lines = content.split('\n')[:5]
        first_line = first_lines[0] if first_lines else ""

        # Count potential delimiters
        counts = {
            ',': first_line.count(','),
            ';': first_line.count(';'),
            '\t': first_line.count('\t'),
        }

        # Return the most common delimiter
        return max(counts, key=counts.get) if any(counts.values()) else ','

    @staticmethod
    def _detect_header(rows: List[List[str]]) -> bool:
        """
        Detect if the first row is a header row.

        A row is considered a header if all its non-empty values are strings
        that don't look like numbers or booleans.

        Args:
            rows: List of parsed CSV rows.

        Returns:
            True if the first row appears to be a header.
        """
        if len(rows) < 2:
            return False

        header = rows[0]
        sample_row = rows[1]

        # Check if header values are all strings (not parseable as numbers/bools)
        for cell in header:
            cell = cell.strip()
            if not cell:
                continue
            # If it can be parsed as a number, it's probably not a header
            try:
                float(cell)
                return False
            except ValueError:
                pass
            # If it's a boolean word, probably not a header
            if cell.lower() in ('true', 'false', 'yes', 'no'):
                return False

        # Check if header values look different from data values
        # Headers tend to be non-numeric strings
        header_types = set()
        for cell in header:
            cell = cell.strip()
            if cell:
                try:
                    float(cell)
                    header_types.add('number')
                except ValueError:
                    header_types.add('string')

        data_types = set()
        for cell in sample_row:
            cell = cell.strip()
            if cell:
                try:
                    float(cell)
                    data_types.add('number')
                except ValueError:
                    data_types.add('string')

        # If header is all strings and data has numbers, likely a header
        if header_types == {'string'} and 'number' in data_types:
            return True

        # If all header values are unique and data values are not, likely a header
        header_vals = [c.strip() for c in header if c.strip()]
        if len(header_vals) == len(set(header_vals)) and len(header_vals) > 1:
            return True

        return False

    @staticmethod
    def _infer_type(value: str) -> Any:
        """
        Infer the Python type of a string value.

        Attempts to parse as: bool, int, float, then falls back to string.

        Args:
            value: The string value to infer type for.

        Returns:
            The value converted to the appropriate Python type.
        """
        if not value:
            return None

        # Boolean
        if value.lower() in ('true', 'yes'):
            return True
        if value.lower() in ('false', 'no'):
            return False

        # Integer
        try:
            int_val = int(value)
            # Make sure it's not a float-like string (e.g., "1.0")
            if '.' not in value:
                return int_val
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # String
        return value

    @staticmethod
    def _format_value(value: Any) -> str:
        """
        Format a Python value for CSV output.

        Args:
            value: The value to format.

        Returns:
            String representation suitable for CSV.
        """
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)
