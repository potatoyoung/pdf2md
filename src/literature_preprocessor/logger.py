from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path

from literature_preprocessor.converter import ConversionResult


REPORT_FIELDS = [
    "pdf_path",
    "markdown_path",
    "success",
    "skipped",
    "error",
    "elapsed_seconds",
]


def setup_logging(log_dir: Path) -> Path:
    """Configure console and file logging for a conversion run."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"convert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    return log_path


def write_csv_report(results: list[ConversionResult], report_path: Path) -> None:
    """Write a structured CSV report for all conversion results."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "pdf_path": str(result.pdf_path),
                    "markdown_path": str(result.markdown_path),
                    "success": result.success,
                    "skipped": result.skipped,
                    "error": result.error,
                    "elapsed_seconds": f"{result.elapsed_seconds:.3f}",
                }
            )

