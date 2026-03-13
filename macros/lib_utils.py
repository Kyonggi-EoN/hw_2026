"""
Shared utility functions for KLayout library registration.
Used by register_libraries.lym and tests/test_register_libraries.py.
"""
import os
import glob
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
