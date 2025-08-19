"""
PDF Parts List Extractor
========================

This module implements a simple command‑line tool for extracting parts list
information from PDF documents.  It supports batch processing of multiple
PDFs and outputs a consolidated Excel spreadsheet with the parsed data.

The extractor is designed around the following core principles:

* **Text‑based pages first.**  It uses the `pdftotext` utility (from the
  Poppler suite) to extract text from PDFs.  Pages that contain no
  extractable text are assumed to be scanned images.  If OCR support is
  available on the system (via the `tesseract` command), the extractor
  will attempt to run OCR on those pages; otherwise, it logs the
  omission and continues.

* **Flexible table detection.**  Many parts lists are formatted as simple
  tables with columns separated by multiple spaces.  The extractor uses
  heuristics to locate a header row containing column names such as
  "Description", "Equipment", "Part", etc.  Once a header row has been
  identified, all subsequent rows with a similar column count are
  interpreted as part entries.  While this approach is not foolproof,
  it provides a reasonable baseline without external dependencies.

* **Structured output.**  Each part entry is stored with a consistent
  set of fields (description, equipment name, make, model, part number,
  drawing number, document number, page number, equipment category and
  parts classification).  Additional metadata about the source PDF and
  extraction time are added to each row.  The final results are
  exported to an Excel file (via pandas) and a CSV log of warnings is
  produced for troubleshooting.

To run the extractor:

    python pdf_parts_extractor.py --input-dir path/to/pdfs --output xlsx_path

The script will process all `.pdf` files in the given directory.  For
usage details, see the `argparse` description at the bottom of this
file.

Notes
-----
This implementation is a reference prototype.  Real‑world documents
often require more sophisticated layout analysis and OCR models.  The
design outlined in the accompanying report describes how to extend
this baseline with advanced OCR (e.g., Tesseract or PaddleOCR),
layout parsing and machine‑learning models for robust field
classification.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd


logger = logging.getLogger(__name__)


@dataclass
class PartEntry:
    """Data class representing a single extracted part entry."""

    description: str = ""
    equipment_name: str = ""
    make: str = ""
    model: str = ""
    part_number: str = ""
    drawing_number: str = ""
    document_number: str = ""
    page_number: int = 0
    equipment_category: str = ""
    parts_classification: str = ""
    pdf_file: str = ""
    extraction_time: str = ""


def run_command(command: Sequence[str]) -> Tuple[int, str, str]:
    """Run an external command and return return code, stdout and stderr.

    Parameters
    ----------
    command : sequence of str
        The command and its arguments to execute.

    Returns
    -------
    tuple
        A tuple `(returncode, stdout, stderr)`.
    """
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        return completed.returncode, completed.stdout, completed.stderr
    except FileNotFoundError:
        return 1, "", f"Command not found: {command[0]}"


def extract_text_with_pdftotext(pdf_path: str) -> Dict[int, str]:
    """Extract text from each page of a PDF using pdftotext.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF file.

    Returns
    -------
    dict
        A mapping from page number (1-based) to the extracted text.
    """
    # Query the number of pages using pdfinfo.
    rc, out, err = run_command(["pdfinfo", pdf_path])
    if rc != 0:
        logger.error("Failed to run pdfinfo on %s: %s", pdf_path, err)
        return {}

    pages_match = re.search(r"Pages:\s+(\d+)", out)
    if not pages_match:
        logger.error("Could not determine page count for %s", pdf_path)
        return {}
    try:
        page_count = int(pages_match.group(1))
    except ValueError:
        logger.error("Invalid page count in pdfinfo output: %s", out)
        return {}

    text_by_page: Dict[int, str] = {}

    for page in range(1, page_count + 1):
        # Use pdftotext with layout preservation for each page.
        command = [
            "pdftotext",
            "-layout",
            "-f",
            str(page),
            "-l",
            str(page),
            pdf_path,
            "-",
        ]
        rc, page_text, err = run_command(command)
        if rc != 0:
            logger.warning(
                "pdftotext failed for %s page %d: %s", pdf_path, page, err.strip()
            )
        text_by_page[page] = page_text.strip()
    return text_by_page


def perform_ocr_on_page(pdf_path: str, page: int) -> str:
    """Attempt to perform OCR on a page using tesseract.

    If tesseract is not installed, returns an empty string and logs a warning.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF file.
    page : int
        1-based page number.

    Returns
    -------
    str
        Recognized text for the page, or an empty string if OCR cannot be
        performed.
    """
    # Check tesseract availability
    rc, _, _ = run_command(["which", "tesseract"])
    if rc != 0:
        logger.warning(
            "tesseract not installed; skipping OCR for %s page %d", pdf_path, page
        )
        return ""

    # Convert page to PPM image using pdftoppm.
    # We create a temporary directory under /tmp for image output.
    tmp_dir = Path("/tmp/pdf_parts_ocr")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    ppm_base = tmp_dir / f"page_{os.getpid()}_{page}"
    command = [
        "pdftoppm",
        "-f",
        str(page),
        "-l",
        str(page),
        "-r",
        "300",  # resolution
        pdf_path,
        str(ppm_base),
    ]
    rc, out, err = run_command(command)
    if rc != 0:
        logger.warning(
            "pdftoppm failed for OCR on %s page %d: %s", pdf_path, page, err.strip()
        )
        return ""
    # The output file will be named `${ppm_base}-1.ppm`.
    ppm_file = f"{ppm_base}-1.ppm"
    txt_file = f"{ppm_base}-1"
    # Run tesseract on the image.  We capture stdout via file output.
    command = ["tesseract", ppm_file, txt_file, "--psm", "3", "-l", "eng"]
    rc, out, err = run_command(command)
    if rc != 0:
        logger.warning(
            "tesseract OCR failed for %s page %d: %s", pdf_path, page, err.strip()
        )
        return ""
    # Read back the generated .txt file.
    try:
        with open(f"{txt_file}.txt", "r", encoding="utf-8") as f:
            ocr_text = f.read().strip()
    except Exception as exc:
        logger.warning(
            "Failed to read OCR output for %s page %d: %s", pdf_path, page, exc
        )
        ocr_text = ""
    # Cleanup
    try:
        os.remove(ppm_file)
        os.remove(f"{txt_file}.txt")
    except OSError:
        pass
    return ocr_text


def parse_parts_from_text(
    text: str, page_number: int, pdf_name: str, extraction_time: str
) -> List[PartEntry]:
    """Parse potential parts list entries from a block of text.

    This function attempts to locate a header row by searching for common
    column names.  After a header has been found, subsequent lines with
    a similar number of columns are interpreted as data rows.  The
    resulting entries are returned as a list of PartEntry objects.

    Parameters
    ----------
    text : str
        Text extracted from a PDF page (either via pdftotext or OCR).
    page_number : int
        1-based page index (for traceability).
    pdf_name : str
        Name of the PDF file (without path).
    extraction_time : str
        ISO8601 timestamp used for all entries.

    Returns
    -------
    list
        List of PartEntry objects extracted from the text.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []

    # Define expected field names (lowercase for matching).
    field_keywords = {
        "description": ["description", "desc", "part description"],
        "equipment_name": ["equipment", "equip", "equipment name", "system"],
        "make": ["make", "manufacturer"],
        "model": ["model"],
        "part_number": ["part", "part no", "part #", "part number", "p/n"],
        "drawing_number": ["drawing", "dwg", "drawing no", "drawing number"],
        "document_number": ["document", "doc", "document no", "doc number"],
        "equipment_category": ["category", "equipment category", "cat"],
        "parts_classification": ["classification", "class", "parts classification"],
    }

    header_line_index: Optional[int] = None
    column_map: Dict[int, str] = {}
    num_columns = 0

    # Simple heuristic: find a line containing at least half of the
    # field keywords.  We tokenise by splitting on two or more spaces.
    for idx, line in enumerate(lines):
        # Use two or more spaces as delimiter to preserve multi‑word
        # fields better than splitting on any whitespace.  Fallback to
        # splitting on single spaces if no multi‑space found.
        if re.search(r"\s{2,}", line):
            tokens = re.split(r"\s{2,}", line)
        else:
            tokens = line.split()
        # Lowercase tokens for matching
        tokens_lc = [t.lower() for t in tokens]
        matched_fields = 0
        local_map: Dict[int, str] = {}
        for i, token in enumerate(tokens_lc):
            for field, keywords in field_keywords.items():
                if any(k in token for k in keywords):
                    local_map[i] = field
                    matched_fields += 1
                    break
        if matched_fields >= max(3, len(field_keywords) // 2):
            header_line_index = idx
            column_map = local_map
            num_columns = len(tokens)
            logger.debug(
                "Header detected on page %d (%s): %s", page_number, pdf_name, line
            )
            break

    if header_line_index is None:
        return []

    entries: List[PartEntry] = []

    # Process subsequent lines as potential data rows.
    for line in lines[header_line_index + 1 :]:
        # Split the line using the same logic.
        if re.search(r"\s{2,}", line):
            tokens = re.split(r"\s{2,}", line)
        else:
            tokens = line.split()
        if not tokens:
            continue
        # Skip lines that don't have the expected number of columns (+/- one).
        if abs(len(tokens) - num_columns) > 1:
            continue
        # Build entry using available tokens mapped via column_map.
        entry_kwargs = {
            "description": "",
            "equipment_name": "",
            "make": "",
            "model": "",
            "part_number": "",
            "drawing_number": "",
            "document_number": "",
            "equipment_category": "",
            "parts_classification": "",
        }
        for i, token in enumerate(tokens):
            field = column_map.get(i)
            if field:
                entry_kwargs[field] = token.strip()
        entry = PartEntry(
            description=entry_kwargs["description"],
            equipment_name=entry_kwargs["equipment_name"],
            make=entry_kwargs["make"],
            model=entry_kwargs["model"],
            part_number=entry_kwargs["part_number"],
            drawing_number=entry_kwargs["drawing_number"],
            document_number=entry_kwargs["document_number"],
            equipment_category=entry_kwargs["equipment_category"],
            parts_classification=entry_kwargs["parts_classification"],
            page_number=page_number,
            pdf_file=pdf_name,
            extraction_time=extraction_time,
        )
        entries.append(entry)
    return entries


def process_pdf(pdf_path: str) -> Tuple[List[PartEntry], List[Tuple[str, str]]]:
    """Process a single PDF and return extracted parts and warnings.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF file to process.

    Returns
    -------
    tuple
        A tuple `(entries, warnings)` where `entries` is a list of
        PartEntry objects and `warnings` is a list of (page, message)
        tuples describing any issues encountered.
    """
    pdf_name = os.path.basename(pdf_path)
    extraction_time = _dt.datetime.now().astimezone().isoformat()
    entries: List[PartEntry] = []
    warnings: List[Tuple[str, str]] = []

    text_by_page = extract_text_with_pdftotext(pdf_path)
    if not text_by_page:
        warnings.append(("global", f"No pages extracted from {pdf_name}"))
        return entries, warnings
    for page, text in text_by_page.items():
        # If no text is found, attempt OCR.
        if not text.strip():
            ocr_text = perform_ocr_on_page(pdf_path, page)
            if ocr_text:
                text = ocr_text
            else:
                warnings.append(
                    (f"Page {page}", f"No text extracted from page {page} of {pdf_name}")
                )
                continue
        page_entries = parse_parts_from_text(text, page, pdf_name, extraction_time)
        if page_entries:
            entries.extend(page_entries)
    return entries, warnings


def export_to_excel(entries: Sequence[PartEntry], output_path: str) -> None:
    """Export a list of PartEntry objects to an Excel file.

    Parameters
    ----------
    entries : sequence of PartEntry
        Extracted parts entries.
    output_path : str
        Path to write the Excel (.xlsx) file.
    """
    # Convert dataclass instances to dicts for pandas.
    records = [entry.__dict__ for entry in entries]
    df = pd.DataFrame(records)
    # Ensure a consistent column order
    columns = [
        "pdf_file",
        "page_number",
        "extraction_time",
        "description",
        "equipment_name",
        "make",
        "model",
        "part_number",
        "drawing_number",
        "document_number",
        "equipment_category",
        "parts_classification",
    ]
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    df = df[columns]
    # Write to Excel
    df.to_excel(output_path, index=False, engine="openpyxl")


def write_warnings_log(warnings: Sequence[Tuple[str, str]], log_path: str) -> None:
    """Write warnings to a CSV log file.

    Parameters
    ----------
    warnings : sequence of (str, str)
        A list of (location, message) tuples.
    log_path : str
        Path to write the CSV log.
    """
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Location", "Message"])
        for loc, msg in warnings:
            writer.writerow([loc, msg])


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract parts list information from PDF documents.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory containing PDF files to process.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="parts_list.xlsx",
        help="Path to the output Excel file (.xlsx).",
    )
    parser.add_argument(
        "--log",
        type=str,
        default="extraction_warnings.csv",
        help="Path to the warnings log CSV.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    args = parser.parse_args(argv)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        logger.error("Input directory does not exist: %s", input_dir)
        return 1

    pdf_paths = sorted([str(p) for p in input_dir.glob("*.pdf")])
    if not pdf_paths:
        logger.error("No PDF files found in directory: %s", input_dir)
        return 1

    all_entries: List[PartEntry] = []
    all_warnings: List[Tuple[str, str]] = []

    for pdf_path in pdf_paths:
        logger.info("Processing %s", pdf_path)
        entries, warnings = process_pdf(pdf_path)
        if entries:
            all_entries.extend(entries)
            logger.info("Extracted %d entries from %s", len(entries), pdf_path)
        else:
            logger.info("No entries extracted from %s", pdf_path)
        all_warnings.extend([(f"{pdf_path} {loc}", msg) for loc, msg in warnings])

    # Export results
    if all_entries:
        export_to_excel(all_entries, args.output)
        logger.info("Wrote extracted data to %s", args.output)
    else:
        logger.info("No entries extracted from any PDF.  No Excel file created.")
    if all_warnings:
        write_warnings_log(all_warnings, args.log)
        logger.info("Wrote warnings log to %s", args.log)

    return 0


if __name__ == "__main__":
    sys.exit(main())