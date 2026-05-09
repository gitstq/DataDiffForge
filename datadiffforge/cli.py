"""
CLI entry point for DataDiffForge.

Provides command-line interface for diff, merge, snapshot, compare-snapshots,
and watch commands using argparse.
"""

import argparse
import os
import sys
import time
from typing import List, Optional

from .core.differ import diff
from .core.merger import merge_with_report
from .reporters.terminal import TerminalReporter
from .reporters.json_reporter import JsonReporter
from .reporters.html_reporter import HtmlReporter
from .reporters.markdown_reporter import MarkdownReporter
from .utils.file_utils import (
    load_file,
    save_file,
    save_snapshot,
    write_output,
    detect_format,
)
from .utils.color import supports_color


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the main argument parser with all subcommands.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="datadiff",
        description="DataDiffForge - A lightweight structured data diff and intelligent merge engine.",
        epilog="Examples:\n"
               "  datadiff diff file1.json file2.json\n"
               "  datadiff diff config.yaml config2.yaml -f html -o diff.html\n"
               "  datadiff merge left.json right.json -s smart -o merged.json\n"
               "  datadiff snapshot data.json -l backup\n"
               "  datadiff watch config.yaml config-live.yaml -n 5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"DataDiffForge {__import__('datadiffforge').__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- diff command ---
    diff_parser = subparsers.add_parser(
        "diff",
        help="Compute differences between two files",
        description="Compare two structured data files and show differences.",
    )
    diff_parser.add_argument("file1", help="Path to the first (left) file")
    diff_parser.add_argument("file2", help="Path to the second (right) file")
    diff_parser.add_argument(
        "-f", "--format",
        choices=["terminal", "json", "html", "markdown"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    diff_parser.add_argument(
        "-i", "--ignore",
        action="append",
        default=[],
        metavar="PATH",
        help="Path pattern to ignore (can be specified multiple times)",
    )
    diff_parser.add_argument(
        "-d", "--depth",
        type=int,
        default=None,
        help="Maximum comparison depth (default: unlimited)",
    )
    diff_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (default: stdout)",
    )
    diff_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    diff_parser.add_argument(
        "--stat",
        action="store_true",
        help="Show statistics only",
    )

    # --- merge command ---
    merge_parser = subparsers.add_parser(
        "merge",
        help="Intelligently merge two files",
        description="Merge two structured data files using configurable strategies.",
    )
    merge_parser.add_argument("file1", help="Path to the first (left) file")
    merge_parser.add_argument("file2", help="Path to the second (right) file")
    merge_parser.add_argument(
        "-s", "--strategy",
        choices=["keep-both", "left-wins", "right-wins", "smart"],
        default="smart",
        help="Merge strategy (default: smart)",
    )
    merge_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (default: stdout)",
    )
    merge_parser.add_argument(
        "-f", "--format",
        default=None,
        help="Output format for merged result (auto-detected from output path or json)",
    )
    merge_parser.add_argument(
        "-b", "--base",
        default=None,
        help="Base file for three-way merge",
    )

    # --- snapshot command ---
    snapshot_parser = subparsers.add_parser(
        "snapshot",
        help="Create a snapshot of a file",
        description="Save a timestamped snapshot of a data file.",
    )
    snapshot_parser.add_argument("file", help="Path to the file to snapshot")
    snapshot_parser.add_argument(
        "-o", "--output-dir",
        default="./snapshots",
        help="Directory to save snapshot (default: ./snapshots)",
    )
    snapshot_parser.add_argument(
        "-l", "--label",
        default=None,
        help="Snapshot label",
    )

    # --- compare-snapshots command ---
    compare_parser = subparsers.add_parser(
        "compare-snapshots",
        help="Compare two snapshot files",
        description="Compare two snapshot files and show differences.",
    )
    compare_parser.add_argument("snapshot1", help="Path to the first snapshot")
    compare_parser.add_argument("snapshot2", help="Path to the second snapshot")
    compare_parser.add_argument(
        "-f", "--format",
        choices=["terminal", "json", "html", "markdown"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    compare_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    # --- watch command ---
    watch_parser = subparsers.add_parser(
        "watch",
        help="Watch two files for changes",
        description="Continuously monitor two files and report differences.",
    )
    watch_parser.add_argument("file1", help="Path to the first file")
    watch_parser.add_argument("file2", help="Path to the second file")
    watch_parser.add_argument(
        "-n", "--interval",
        type=float,
        default=2.0,
        help="Check interval in seconds (default: 2)",
    )
    watch_parser.add_argument(
        "-f", "--format",
        choices=["terminal", "json", "html", "markdown"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    watch_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    return parser


def _get_reporter(format_name: str, use_color: bool = True):
    """
    Get the appropriate reporter instance for the given format.

    Args:
        format_name: The output format name.
        use_color: Whether to use color (for terminal reporter).

    Returns:
        A reporter instance.
    """
    reporters = {
        "terminal": lambda: TerminalReporter(use_color=use_color),
        "json": JsonReporter,
        "html": HtmlReporter,
        "markdown": MarkdownReporter,
    }
    if format_name not in reporters:
        raise ValueError(f"Unknown format: '{format_name}'")
    return reporters[format_name]()


def _cmd_diff(args: argparse.Namespace) -> int:
    """
    Handle the 'diff' command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        left_data = load_file(args.file1)
        right_data = load_file(args.file2)
    except Exception as e:
        print(f"Error loading files: {e}", file=sys.stderr)
        return 1

    # Determine color setting
    use_color = not args.no_color

    # Compute diff
    result = diff(
        left_data,
        right_data,
        left_label=args.file1,
        right_label=args.file2,
        ignore_paths=args.ignore if args.ignore else None,
        max_depth=args.depth,
    )

    # Get reporter and generate output
    reporter = _get_reporter(args.format, use_color=use_color)
    output = reporter.report(result, stat_only=args.stat)

    # Write output
    write_output(output, args.output)
    return 0


def _cmd_merge(args: argparse.Namespace) -> int:
    """
    Handle the 'merge' command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        left_data = load_file(args.file1)
        right_data = load_file(args.file2)
        base_data = None
        if args.base:
            base_data = load_file(args.base)
    except Exception as e:
        print(f"Error loading files: {e}", file=sys.stderr)
        return 1

    # Perform merge
    merge_result = merge_with_report(
        left=left_data,
        right=right_data,
        base=base_data,
        strategy=args.strategy,
        left_label=args.file1,
        right_label=args.file2,
    )

    # Determine output format
    output_format = args.format
    if output_format is None and args.output:
        try:
            output_format = detect_format(args.output)
        except ValueError:
            output_format = "json"
    if output_format is None:
        output_format = "json"

    # Serialize merged data
    try:
        output = save_file(merge_result["merged"], args.output, format_name=output_format)
    except Exception:
        # If save_file doesn't return content, dump manually
        import json
        output_content = json.dumps(merge_result["merged"], indent=2, ensure_ascii=False, default=str)
        write_output(output_content, args.output)

    # Print conflict summary to stderr
    if merge_result["conflict_count"] > 0:
        print(
            f"Merge completed with {merge_result['conflict_count']} conflict(s) "
            f"(strategy: {args.strategy})",
            file=sys.stderr,
        )
    else:
        print(
            f"Merge completed successfully with no conflicts (strategy: {args.strategy})",
            file=sys.stderr,
        )

    return 0


def _cmd_snapshot(args: argparse.Namespace) -> int:
    """
    Handle the 'snapshot' command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        data = load_file(args.file)
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        return 1

    try:
        # Detect format from source file
        fmt = detect_format(args.file)
        filepath = save_snapshot(data, args.output_dir, label=args.label, format_name=fmt)
        print(f"Snapshot saved: {filepath}")
        return 0
    except Exception as e:
        print(f"Error saving snapshot: {e}", file=sys.stderr)
        return 1


def _cmd_compare_snapshots(args: argparse.Namespace) -> int:
    """
    Handle the 'compare-snapshots' command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        left_data = load_file(args.snapshot1)
        right_data = load_file(args.snapshot2)
    except Exception as e:
        print(f"Error loading snapshot files: {e}", file=sys.stderr)
        return 1

    use_color = not args.no_color

    result = diff(
        left_data,
        right_data,
        left_label=args.snapshot1,
        right_label=args.snapshot2,
    )

    reporter = _get_reporter(args.format, use_color=use_color)
    output = reporter.report(result)
    write_output(output)
    return 0


def _cmd_watch(args: argparse.Namespace) -> int:
    """
    Handle the 'watch' command.

    Continuously monitors two files and reports differences
    at the specified interval.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    use_color = not args.no_color

    print(f"Watching {args.file1} and {args.file2} (interval: {args.interval}s)")
    print("Press Ctrl+C to stop.\n")

    prev_mtime1 = None
    prev_mtime2 = None

    try:
        while True:
            # Check file modification times
            try:
                mtime1 = os.path.getmtime(args.file1)
                mtime2 = os.path.getmtime(args.file2)
            except OSError as e:
                print(f"Error accessing files: {e}", file=sys.stderr)
                time.sleep(args.interval)
                continue

            # If either file changed, compute diff
            if mtime1 != prev_mtime1 or mtime2 != prev_mtime2:
                if prev_mtime1 is not None:  # Skip first iteration
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n--- Changes detected at {timestamp} ---")

                    try:
                        left_data = load_file(args.file1)
                        right_data = load_file(args.file2)

                        result = diff(
                            left_data,
                            right_data,
                            left_label=args.file1,
                            right_label=args.file2,
                        )

                        reporter = _get_reporter(args.format, use_color=use_color)
                        output = reporter.report(result)
                        print(output)
                    except Exception as e:
                        print(f"Error computing diff: {e}", file=sys.stderr)

                prev_mtime1 = mtime1
                prev_mtime2 = mtime2

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nWatch stopped.")
        return 0


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the DataDiffForge CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    # Dispatch to the appropriate command handler
    handlers = {
        "diff": _cmd_diff,
        "merge": _cmd_merge,
        "snapshot": _cmd_snapshot,
        "compare-snapshots": _cmd_compare_snapshots,
        "watch": _cmd_watch,
    }

    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
