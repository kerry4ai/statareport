#!/usr/bin/env python3
"""
Detect Stata installation on the system.
Supports Windows, macOS, and Linux.
Looks for StataMP, StataSE, StataIC executables
in PATH and common installation directories.
"""

import os
import shutil
import sys
from pathlib import Path

# Platform-specific executable names
STATA_EXECUTABLES = {
    "win32": [
        "StataMP-64.exe",
        "StataSE-64.exe",
        "StataMP.exe",
        "StataSE.exe",
        "Stata-64.exe",
        "Stata.exe",
    ],
    "darwin": [
        "StataMP",
        "StataSE",
        "Stata",
    ],
    "linux": [
        "stata-mp",
        "stata-se",
        "stata",
    ],
}

# Platform-specific common installation directories
COMMON_PATHS = {
    "win32": [
        r"C:\Program Files\Stata",
        r"C:\Program Files (x86)\Stata",
        r"D:\Program\StataNow19",
        r"D:\Program\StataNow",
        r"D:\Program\Stata19",
        r"D:\Program\Stata18MP",
        r"D:\Program\Stata18",
        r"D:\Program\Stata17",
        r"D:\Program\Stata16",
        r"D:\Program\Stata15",
    ],
    "darwin": [
        "/Applications/Stata/StataMP.app/Contents/MacOS",
        "/Applications/Stata/StataSE.app/Contents/MacOS",
        "/Applications/Stata/Stata.app/Contents/MacOS",
        "/Applications/StataNow/StataMP.app/Contents/MacOS",
        "/Applications/StataNow/StataSE.app/Contents/MacOS",
        "/Applications/StataNow/Stata.app/Contents/MacOS",
        "/Applications/Stata19/StataMP.app/Contents/MacOS",
        "/Applications/Stata18/StataMP.app/Contents/MacOS",
        "/Applications/Stata17/StataMP.app/Contents/MacOS",
    ],
    "linux": [
        "/usr/local/stata19",
        "/usr/local/stata18",
        "/usr/local/stata17",
        "/usr/local/stata16",
        "/usr/local/stata15",
        "/usr/local/stata",
        "/opt/stata19",
        "/opt/stata18",
        "/opt/stata",
        os.path.expanduser("~/stata19"),
        os.path.expanduser("~/stata18"),
        os.path.expanduser("~/stata"),
    ],
}


def _get_platform():
    """Return the platform key used by this module."""
    if sys.platform.startswith("win"):
        return "win32"
    elif sys.platform == "darwin":
        return "darwin"
    else:
        return "linux"


def find_stata_in_path():
    """Check if Stata is available in system PATH."""
    platform = _get_platform()
    for exe in STATA_EXECUTABLES.get(platform, []):
        found = shutil.which(exe)
        if found:
            return found
    return None


def find_stata_in_common_dirs():
    """Search common Stata installation directories."""
    platform = _get_platform()
    found_paths = []
    for base in COMMON_PATHS.get(platform, []):
        base_path = Path(base)
        if not base_path.exists():
            continue
        for exe in STATA_EXECUTABLES.get(platform, []):
            # Search recursively up to 3 levels on Windows,
            # 1 level on macOS/Linux (paths are already specific)
            max_depth = 3 if platform == "win32" else 1
            for p in _rglob_depth(base_path, exe, max_depth):
                if p.is_file() and os.access(str(p), os.X_OK):
                    found_paths.append(str(p))
                elif p.is_file() and platform == "win32":
                    # Windows executables don't need X_OK
                    found_paths.append(str(p))
    return found_paths


def _rglob_depth(path, pattern, max_depth):
    """Recursive glob with a depth limit."""
    if max_depth < 1:
        return
    try:
        for item in path.iterdir():
            if item.is_file() and item.name == pattern:
                yield item
            elif item.is_dir() and max_depth > 1:
                yield from _rglob_depth(item, pattern, max_depth - 1)
    except PermissionError:
        pass


def detect_stata():
    """
    Detect Stata installation.
    Returns the full path to the first found executable, or None.
    Priority: PATH > common directories > MP over SE over IC.
    """
    # First check PATH
    path_result = find_stata_in_path()
    if path_result:
        return path_result

    # Then search common directories
    common_results = find_stata_in_common_dirs()
    if common_results:
        # Prefer MP over SE, 64-bit over 32-bit
        platform = _get_platform()
        if platform == "win32":
            priority = [
                "StataMP-64",
                "StataSE-64",
                "StataMP",
                "StataSE",
                "Stata-64",
                "Stata",
            ]
        elif platform == "darwin":
            priority = ["StataMP", "StataSE", "Stata"]
        else:
            priority = ["stata-mp", "stata-se", "stata"]

        for pref in priority:
            for p in common_results:
                if pref in Path(p).name:
                    return p
        return common_results[0]

    return None


def main():
    stata_path = detect_stata()
    if stata_path:
        print(f"STATA_FOUND: {stata_path}")
        return 0
    else:
        print("STATA_NOT_FOUND")
        print(f"Searched PATH and common directories for platform: {_get_platform()}")
        for p in COMMON_PATHS.get(_get_platform(), []):
            print(f"  - {p}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
