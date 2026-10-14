"""Filesystem roots for configuration, cache, snapshots, and fixtures."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
REPO_ROOT = SRC_DIR.parent


def _frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_dir() -> Path | None:
    meipass = getattr(sys, "_MEIPASS", None)
    return Path(meipass) if meipass else None


def repo_root() -> Path:
    if _frozen():
        return Path(sys.executable).resolve().parent
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents, REPO_ROOT):
        if (candidate / "pyproject.toml").is_file() and (candidate / "config").is_dir():
            return candidate
    return REPO_ROOT


def ensure_runtime_layout() -> None:
    """Copy bundled default config next to the .exe on first run."""
    bundled = bundle_dir()
    if bundled is None:
        return
    destination = repo_root() / "config"
    source = bundled / "config"
    if destination.is_dir() or not source.is_dir():
        return
    shutil.copytree(source, destination)


def config_dir() -> Path:
    return repo_root() / "config"


def data_dir() -> Path:
    return repo_root() / "data"


def cache_dir() -> Path:
    path = data_dir() / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def snapshots_dir() -> Path:
    path = data_dir() / "snapshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


def fixtures_dir() -> Path:
    return repo_root() / "fixtures"
