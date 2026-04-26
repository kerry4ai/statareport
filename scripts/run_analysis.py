#!/usr/bin/env python3
"""
Execute a Stata do-file and generate an HTML report.
Cross-platform wrapper for Stata batch execution.
Supports Windows, macOS, and Linux.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    from detect_stata import detect_stata
except ImportError:
    # Fallback inline detection
    def detect_stata():
        import shutil

        candidates = {
            "win32": [
                "StataMP-64.exe",
                "StataSE-64.exe",
                "StataMP.exe",
                "StataSE.exe",
                "Stata.exe",
            ],
            "darwin": ["StataMP", "StataSE", "Stata"],
            "linux": ["stata-mp", "stata-se", "stata"],
        }
        platform = "win32" if sys.platform.startswith("win") else ("darwin" if sys.platform == "darwin" else "linux")
        for exe in candidates.get(platform, []):
            found = shutil.which(exe)
            if found:
                return found
        return None


def _get_platform_key():
    """Return a simplified platform identifier."""
    if sys.platform.startswith("win"):
        return "win32"
    elif sys.platform == "darwin":
        return "darwin"
    else:
        return "linux"


def build_stata_command(stata_path, dofile_path):
    """
    Build the Stata batch command appropriate for the current platform.

    Windows: StataMP-64.exe /e do "file.do"
    macOS:   /Applications/Stata/StataMP.app/Contents/MacOS/StataMP -b do "file.do"
    Linux:   /usr/local/stata18/stata-mp -b do "file.do"
    """
    platform = _get_platform_key()
    dofile_str = str(dofile_path)

    if platform == "win32":
        # Windows uses /e (execute and exit) or /b (batch with log)
        return [stata_path, "/e", "do", dofile_str]
    else:
        # Unix (macOS/Linux) uses -b do (batch mode) or -e do (execute and exit)
        # -b generates a .log file; -e does not.
        # We use -e to match Windows /e behavior (no auto log).
        return [stata_path, "-e", "do", dofile_str]


def run_stata_dofile(stata_path, dofile_path, working_dir=None):
    """
    Run a Stata do-file in batch mode.

    Args:
        stata_path: Full path to Stata executable
        dofile_path: Full path to .do file
        working_dir: Optional working directory for execution

    Returns:
        subprocess.CompletedProcess instance
    """
    dofile_path = Path(dofile_path).resolve()
    if not dofile_path.exists():
        raise FileNotFoundError(f"Do-file not found: {dofile_path}")

    cmd = build_stata_command(stata_path, dofile_path)

    kwargs = {"capture_output": True, "text": True}
    if working_dir:
        kwargs["cwd"] = str(Path(working_dir).resolve())

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, **kwargs)
    return result


def check_outputs(working_dir, expected_patterns=None):
    """
    Check if expected output files were generated.

    Args:
        working_dir: Directory to search in
        expected_patterns: List of filename glob patterns to check

    Returns:
        dict mapping pattern to (found: bool, matched_files: list)
    """
    if expected_patterns is None:
        expected_patterns = ["*.html"]

    working_dir = Path(working_dir)
    results = {}

    for pattern in expected_patterns:
        matches = list(working_dir.glob(pattern))
        results[pattern] = {"found": bool(matches), "files": [str(m.name) for m in matches]}

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run Stata do-file and generate HTML report"
    )
    parser.add_argument("dofile", help="Path to Stata .do file")
    parser.add_argument(
        "--stata-path",
        help="Path to Stata executable (auto-detected if not provided)",
    )
    parser.add_argument(
        "--working-dir",
        help="Working directory for execution (defaults to dofile directory)",
    )
    parser.add_argument(
        "--check-outputs",
        nargs="+",
        default=["*.html"],
        help="Expected output file patterns to verify (default: *.html)",
    )
    args = parser.parse_args()

    # Detect Stata if not provided
    stata_path = args.stata_path
    if not stata_path:
        stata_path = detect_stata()
        if not stata_path:
            print("ERROR: Stata not found. Please provide --stata-path.")
            print("Searched PATH and common installation directories.")
            sys.exit(1)
        print(f"Auto-detected Stata: {stata_path}")

    # Verify executable exists
    if not Path(stata_path).exists():
        print(f"ERROR: Stata executable not found at: {stata_path}")
        sys.exit(1)

    # Determine working directory
    working_dir = args.working_dir
    if not working_dir:
        working_dir = Path(args.dofile).parent

    # Run the do-file
    try:
        result = run_stata_dofile(stata_path, args.dofile, working_dir)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to run Stata: {e}")
        sys.exit(1)

    # Print outputs
    if result.stdout:
        print("\n--- STDOUT ---")
        print(result.stdout)
    if result.stderr:
        print("\n--- STDERR ---")
        print(result.stderr)

    print(f"\nStata exited with code: {result.returncode}")

    # Check for outputs
    outputs = check_outputs(working_dir, args.check_outputs)
    print("\n--- Output Files ---")
    all_found = True
    for pattern, info in outputs.items():
        status = "FOUND" if info["found"] else "MISSING"
        files_str = ", ".join(info["files"]) if info["files"] else "none"
        print(f"  [{status}] {pattern} -> {files_str}")
        if not info["found"]:
            all_found = False

    if result.returncode != 0:
        print("\nWARNING: Stata returned non-zero exit code.")
        sys.exit(result.returncode)

    if not all_found:
        print("\nWARNING: Some expected output files were not found.")
        sys.exit(2)

    # Return HTML file path if found
    html_files = list(Path(working_dir).glob("*.html"))
    if html_files:
        print(f"\nHTML report(s) generated:")
        for hf in html_files:
            print(f"  - {hf}")

    sys.exit(0)


if __name__ == "__main__":
    main()
