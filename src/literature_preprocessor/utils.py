from __future__ import annotations

import re
from pathlib import Path


WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def resolve_directory(path: str | Path) -> Path:
    """Return an absolute directory path without requiring it to exist."""
    return Path(path).expanduser().resolve()


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if needed and return its absolute path."""
    directory = resolve_directory(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def safe_path_part(name: str) -> str:
    """Sanitize one path component for cross-platform output paths."""
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")
    if not sanitized:
        return "_"
    if sanitized.upper() in WINDOWS_RESERVED_NAMES:
        return f"_{sanitized}"
    return sanitized


def safe_relative_markdown_path(pdf_path: Path, input_dir: Path) -> Path:
    """Build a sanitized Markdown relative path that mirrors the PDF tree."""
    relative = pdf_path.resolve().relative_to(input_dir.resolve())
    parts = [safe_path_part(part) for part in relative.parts]
    safe_relative = Path(*parts).with_suffix(".md")
    return safe_relative


def output_path_for_pdf(pdf_path: Path, input_dir: Path, output_dir: Path) -> Path:
    """Return the Markdown output path for a PDF under an output directory."""
    return output_dir / safe_relative_markdown_path(pdf_path, input_dir)


def is_nonempty_file(path: Path) -> bool:
    """Return True when a path exists and contains at least one byte."""
    return path.is_file() and path.stat().st_size > 0

