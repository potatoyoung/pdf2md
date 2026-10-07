from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path

from literature_preprocessor.converter import ConversionResult, convert_pdf_to_markdown
from literature_preprocessor.logger import setup_logging, write_csv_report
from literature_preprocessor.scanner import find_pdf_files
from literature_preprocessor.utils import ensure_directory, output_path_for_pdf, resolve_directory


logger = logging.getLogger(__name__)


def confirm(prompt: str) -> bool:
    """Return True only when the user explicitly answers yes."""
    try:
        answer = input(f"{prompt} [y/N]: ")
    except EOFError:
        logger.warning("No input available; treating prompt as no: %s", prompt)
        return False
    return answer.strip().lower() in {"y", "yes"}


def confirm_delete_pdfs(pdf_paths: list[Path]) -> bool:
    """Ask whether all successfully converted source PDFs should be deleted."""
    return confirm(
        f"Delete {len(pdf_paths)} successfully converted source PDF(s)?"
    )


def clear_markdown_files(output_dir: Path) -> int:
    """Delete Markdown files under an output directory and return the count."""
    deleted_count = 0
    for markdown_path in sorted(output_dir.rglob("*.md")):
        if not markdown_path.is_file():
            continue
        try:
            markdown_path.unlink()
            deleted_count += 1
            logger.info("Deleted Markdown file: %s", markdown_path)
        except OSError as exc:
            logger.error("Failed to delete Markdown file: %s (%s)", markdown_path, exc)
    return deleted_count


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(
        description="Batch convert research paper PDFs to Markdown with PyMuPDF4LLM.",
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        default=Path("data/pdf"),
        help="Directory containing PDF files. Default: data/pdf",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("data/markdown"),
        help="Directory for generated Markdown files. Default: data/markdown",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing non-empty Markdown files.",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only scan PDFs directly under input-dir.",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("logs"),
        help="Directory for logs and reports. Default: logs",
    )
    return parser


def run_batch(
    input_dir: Path,
    output_dir: Path,
    log_dir: Path,
    overwrite: bool = False,
    recursive: bool = True,
) -> list[ConversionResult]:
    """Run a full PDF to Markdown batch conversion."""
    input_dir = resolve_directory(input_dir)
    output_dir = ensure_directory(output_dir)
    log_dir = ensure_directory(log_dir)

    log_path = setup_logging(log_dir)
    report_path = log_dir / f"conversion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    logger.info("Input directory: %s", input_dir)
    logger.info("Output directory: %s", output_dir)
    logger.info("Recursive scan: %s", recursive)
    logger.info("Overwrite existing Markdown: %s", overwrite)
    logger.info("Log file: %s", log_path)

    if confirm(f"Clear existing Markdown files in {output_dir}?"):
        deleted_count = clear_markdown_files(output_dir)
        logger.info("Cleared %d Markdown file(s) from output directory", deleted_count)
    else:
        logger.info("Kept existing Markdown files in output directory")

    pdf_files = find_pdf_files(input_dir=input_dir, recursive=recursive)
    logger.info("Found %d PDF file(s)", len(pdf_files))

    results: list[ConversionResult] = []
    converted_pdf_paths: list[Path] = []
    for index, pdf_path in enumerate(pdf_files, start=1):
        markdown_path = output_path_for_pdf(pdf_path, input_dir, output_dir)
        logger.info("[%d/%d] Converting: %s", index, len(pdf_files), pdf_path)

        result = convert_pdf_to_markdown(
            pdf_path=pdf_path,
            markdown_path=markdown_path,
            overwrite=overwrite,
        )
        results.append(result)

        if result.skipped:
            logger.info("Skipped existing output: %s", markdown_path)
        elif result.success:
            logger.info("Converted to: %s (%.3fs)", markdown_path, result.elapsed_seconds)
            converted_pdf_paths.append(pdf_path)
        else:
            logger.error("Failed: %s (%s)", pdf_path, result.error)

    if converted_pdf_paths:
        if confirm_delete_pdfs(converted_pdf_paths):
            for pdf_path in converted_pdf_paths:
                try:
                    pdf_path.unlink()
                    logger.info("Deleted source PDF: %s", pdf_path)
                except OSError as exc:
                    logger.error("Failed to delete source PDF: %s (%s)", pdf_path, exc)
        else:
            for pdf_path in converted_pdf_paths:
                logger.info("Kept source PDF: %s", pdf_path)

    write_csv_report(results, report_path)

    success_count = sum(1 for result in results if result.success and not result.skipped)
    skipped_count = sum(1 for result in results if result.skipped)
    failed_count = sum(1 for result in results if not result.success)
    logger.info(
        "Done. converted=%d skipped=%d failed=%d report=%s",
        success_count,
        skipped_count,
        failed_count,
        report_path,
    )
    return results


def main() -> int:
    """CLI entry point."""
    args = build_parser().parse_args()

    try:
        results = run_batch(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            log_dir=args.log_dir,
            overwrite=args.overwrite,
            recursive=not args.no_recursive,
        )
    except Exception as exc:
        logging.basicConfig(level=logging.ERROR)
        logger.error("Batch conversion failed before processing files: %s", exc)
        return 2

    return 1 if any(not result.success for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
