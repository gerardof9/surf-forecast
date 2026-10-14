"""Filesystem roots for configuration, cache, snapshots, and fixtures."""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
REPO_ROOT = SRC_DIR.parent


def repo_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents, REPO_ROOT):
        if (candidate / "pyproject.toml").is_file() and (candidate / "config").is_dir():
            return candidate
    return REPO_ROOT


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
