"""Utilities for packaging the project into a downloadable archive."""

from __future__ import annotations

import argparse
import datetime as dt
import zipfile
from pathlib import Path
from typing import Iterable, Sequence

EXCLUDED_DIRECTORIES = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "dist",
}

EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp"}


def iter_project_files(project_root: Path, include_tests: bool) -> Iterable[Path]:
    """Yield project files eligible for archiving."""

    for path in project_root.rglob("*"):
        if path.is_dir():
            continue
        if any(
            part in EXCLUDED_DIRECTORIES
            for part in path.relative_to(project_root).parts
        ):
            continue
        if not include_tests and "tests" in path.relative_to(project_root).parts:
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        yield path


def create_project_archive(
    project_root: Path,
    output_dir: Path | None = None,
    filename: str | None = None,
    include_tests: bool = True,
    extra_excludes: Sequence[str] | None = None,
) -> Path:
    """Create a zip archive of the project and return its path."""

    project_root = project_root.resolve()
    excludes = set(EXCLUDED_DIRECTORIES)
    if not include_tests:
        excludes.add("tests")
    if extra_excludes:
        excludes.update(extra_excludes)
    if output_dir is None:
        output_dir = project_root / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)
    if filename is None:
        timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"{project_root.name}_{timestamp}.zip"
    archive_path = output_dir / filename
    with zipfile.ZipFile(
        archive_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for file_path in iter_project_files(project_root, include_tests=include_tests):
            relative_path = file_path.relative_to(project_root)
            if any(part in excludes for part in relative_path.parts):
                continue
            archive.write(file_path, arcname=str(relative_path))
    return archive_path


def _build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""

    parser = argparse.ArgumentParser(description="Package the project for download.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project directory to archive.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory where the archive will be written.",
    )
    parser.add_argument(
        "--filename", type=str, default=None, help="Optional custom archive filename."
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Exclude the tests directory from the archive.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional directory names to exclude.",
    )
    return parser


def main() -> None:
    """Entry point for command-line usage."""

    parser = _build_parser()
    args = parser.parse_args()
    archive_path = create_project_archive(
        project_root=args.project_root,
        output_dir=args.output_dir,
        filename=args.filename,
        include_tests=not args.skip_tests,
        extra_excludes=args.exclude,
    )
    print(archive_path)


if __name__ == "__main__":  # pragma: no cover - CLI execution guard
    main()
