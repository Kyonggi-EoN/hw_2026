"""
Shared utility functions for KLayout library registration.
Used by register_libraries.lym and tests/test_register_libraries.py.
"""
import os
from pathlib import Path

LFS_POINTER_MAX_BYTES = 200  # Git LFS pointer files are ~150 bytes


def find_repo_root(start):
    for ancestor in Path(start).resolve().parents:
        if (ancestor / ".git").is_dir():
            return str(ancestor)
    return None


def is_lfs_pointer(filepath):
    return os.path.getsize(filepath) < LFS_POINTER_MAX_BYTES


def get_layout_files(layouts_dir):
    """
    Collect .oas and .gds files from layouts_dir.
    .oas takes priority over .gds for the same stem.
    Returns sorted list of absolute paths.
    """
    p = Path(layouts_dir)
    oas = sorted(p.glob("*.oas"))
    gds = sorted(p.glob("*.gds"))
    oas_names = {f.stem for f in oas}
    gds_filtered = [f for f in gds if f.stem not in oas_names]
    return [str(f) for f in oas + gds_filtered]


def get_library_groups(target_dirs):
    """
    Walk target directories and group layout files by their containing directory.
    """
    groups = {}
    for base_dir in target_dirs:
        if not os.path.isdir(base_dir):
            continue

        for root, dirs, files in os.walk(base_dir):
            dirs.sort()
            layout_files = get_layout_files(root)
            if layout_files:
                lib_name = Path(root).name
                groups.setdefault(lib_name, []).extend(layout_files)

    return groups
