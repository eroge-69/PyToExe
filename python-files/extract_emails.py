#!/usr/bin/env python3
"""
extract_emails.py
===================

This script scans the current working directory for Excel workbooks and
converts each sheet into a CSV file. All email addresses found in any
cell of every workbook are collected and written into a single CSV file.

Usage
-----

Run the script from the command line and optionally specify a target
directory. If no directory is supplied, it operates on the current
directory::

    python extract_emails.py              # scan current directory
    python extract_emails.py /path/to/dir # scan specific directory

The script creates a subdirectory called ``converted_csv`` within the
target directory to hold the per‑sheet CSV files. The consolidated
addresses are written to ``all_emails.csv`` in the target directory.

Requirements
------------

This script depends on the standard library, `pandas` and
`openpyxl`. Both libraries are installed in this environment and are
commonly available in many Python distributions.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Iterable, Set

import pandas as pd


EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def extract_emails_from_dataframe(df: pd.DataFrame) -> Set[str]:
    """Extract all email addresses from a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame from which to extract email addresses.

    Returns
    -------
    Set[str]
        A set of unique email addresses found in the DataFrame.
    """
    emails: Set[str] = set()
    # Convert all values to string and flatten the array
    try:
        values: Iterable[str] = df.astype(str).to_numpy().flatten()
    except Exception:
        # Fallback: iterate through DataFrame values directly if astype fails
        values = (str(v) for row in df.values for v in row)
    for val in values:
        for match in EMAIL_REGEX.findall(val):
            emails.add(match)
    return emails


def sanitize_name(name: str) -> str:
    """Sanitize sheet names and file names for filesystem usage.

    Removes characters that are not alphanumeric or underscore and
    replaces them with underscores. Leading and trailing underscores
    are stripped.
    """
    sanitized = re.sub(r"[^0-9A-Za-z]+", "_", name)
    return sanitized.strip("_") or "sheet"


def process_excel_file(filepath: str, csv_output_dir: str) -> Set[str]:
    """Convert all sheets of an Excel workbook to CSV and extract emails.

    Parameters
    ----------
    filepath : str
        Path to the Excel file.
    csv_output_dir : str
        Directory where the CSV files should be written.

    Returns
    -------
    Set[str]
        A set of unique email addresses found in this file.
    """
    print(f"Processing {os.path.basename(filepath)}...")
    emails: Set[str] = set()
    try:
        excel = pd.ExcelFile(filepath)
    except Exception as exc:
        # Skip unreadable files
        print(f"  Skipped (could not read): {filepath} — {exc}")
        return emails
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    for sheet_name in excel.sheet_names:
        try:
            df = excel.parse(sheet_name=sheet_name, dtype=str)
        except Exception as exc:
            print(f"  Could not parse sheet '{sheet_name}' in {filepath}: {exc}")
            continue
        sanitized_sheet = sanitize_name(sheet_name)
        csv_filename = os.path.join(
            csv_output_dir, f"{sanitize_name(base_name)}_{sanitized_sheet}.csv"
        )
        # Write CSV; ensure directory exists
        os.makedirs(csv_output_dir, exist_ok=True)
        try:
            df.to_csv(csv_filename, index=False)
            print(f"    wrote {os.path.relpath(csv_filename, start=os.path.dirname(csv_output_dir))}")
        except Exception as exc:
            print(f"    Failed to write CSV for sheet '{sheet_name}' in {filepath}: {exc}")
        # Extract emails from DataFrame
        emails.update(extract_emails_from_dataframe(df))
    return emails


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert Excel files in a directory to CSV and collect all "
            "email addresses into a single CSV file."
        )
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory containing Excel files (default: current directory)",
    )
    parser.add_argument(
        "--output",
        default="all_emails.csv",
        help="Name of the consolidated email CSV file (default: all_emails.csv)",
    )
    parser.add_argument(
        "--csv-dir",
        default="converted_csv",
        help="Subdirectory name for storing individual CSV files (default: converted_csv)",
    )
    args = parser.parse_args(argv)

    directory = os.path.abspath(args.directory)
    csv_output_dir = os.path.join(directory, args.csv_dir)
    all_emails: Set[str] = set()

    for entry in os.listdir(directory):
        if entry.lower().endswith((".xls", ".xlsx", ".xlsm", ".xlsb")):
            filepath = os.path.join(directory, entry)
            emails_from_file = process_excel_file(filepath, csv_output_dir)
            all_emails.update(emails_from_file)

    # Write consolidated email list to CSV
    if all_emails:
        output_path = os.path.join(directory, args.output)
        try:
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                for email in sorted(all_emails):
                    f.write(f"{email}\n")
            print(f"\nCollected {len(all_emails)} unique email(s).")
            print(f"Email list written to: {output_path}")
        except Exception as exc:
            print(f"Error writing consolidated CSV: {exc}")
            return 1
    else:
        print("No emails found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())