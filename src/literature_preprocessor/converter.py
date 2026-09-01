from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import pymupdf4llm

from literature_preprocessor.utils import is_nonempty_file


@dataclass(frozen=True)
class ConversionResult:
    """Structured result for one PDF conversion attempt."""

    pdf_path: Path
    markdown_path: Path
    success: bool
    skipped: bool
    error: str
    elapsed_seconds: float


def convert_pdf_to_markdown(
    pdf_path: Path,
    markdown_path: Path,
    overwrite: bool = False,
) -> ConversionResult:
    """Convert one PDF to Markdown with PyMuPDF4LLM."""
    start_time = time.perf_counter()

    if not overwrite and is_nonempty_file(markdown_path):
        return ConversionResult(
            pdf_path=pdf_path,
            markdown_path=markdown_path,
            success=True,
            skipped=True,
            error="",
            elapsed_seconds=0.0,
        )

    try:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_text = pymupdf4llm.to_markdown(str(pdf_path))
        markdown_path.write_text(markdown_text, encoding="utf-8", newline="\n")
        elapsed = time.perf_counter() - start_time
        return ConversionResult(
            pdf_path=pdf_path,
            markdown_path=markdown_path,
            success=True,
            skipped=False,
            error="",
            elapsed_seconds=elapsed,
        )
    except Exception as exc:
        elapsed = time.perf_counter() - start_time
        return ConversionResult(
            pdf_path=pdf_path,
            markdown_path=markdown_path,
            success=False,
            skipped=False,
            error=f"{type(exc).__name__}: {exc}",
            elapsed_seconds=elapsed,
        )

