from __future__ import annotations

from pathlib import Path


def find_pdf_files(input_dir: Path, recursive: bool = True) -> list[Path]:
    """Find PDF files in a directory, optionally scanning subdirectories."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    pattern = "**/*.pdf" if recursive else "*.pdf"
    return sorted(path for path in input_dir.glob(pattern) if path.is_file())

