
#!/usr/bin/env python3
"""
robux_code_checker.py

A CLI tool to validate and de-duplicate Robux-style codes.

Features
--------
1) Validates format XXXXX-XXXXX-XXXXX (alphanumeric, uppercase).
2) Detects duplicates within the provided batch.
3) Detects duplicates against a persistent history file (JSON).
4) Optionally saves unique, valid codes to the history.
5) Generates a CSV report of the check results (optional).

Usage
-----
# Check codes from a text file (one or many per line, spaces/newlines allowed), do NOT save:
python robux_code_checker.py --input codes.txt --history code_history.json

# Check from stdin (paste, then Ctrl+D / Ctrl+Z+Enter on Windows), and save unique valid codes:
python robux_code_checker.py --save --history code_history.json

# Also write a CSV report:
python robux_code_checker.py --input codes.txt --history code_history.json --report report.csv

# Reset/initialize history (use with caution):
python robux_code_checker.py --init --history code_history.json

Notes
-----
- Input is uppercased automatically.
- History is stored as JSON with a list of codes under "codes".
- CSV report includes columns: code, status (invalid/duplicate_in_batch/duplicate_in_history/unique).
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import List, Set, Tuple

FORMAT_RE = re.compile(r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$')

def load_history(path: str) -> Set[str]:
    if not path or not os.path.exists(path):
        return set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        codes = data.get('codes', [])
        return set(map(str, codes))
    except Exception:
        return set()

def save_history(path: str, history: Set[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'codes': sorted(history)
        }, f, ensure_ascii=False, indent=2)

def parse_codes_from_text(text: str) -> List[str]:
    # Split by whitespace and commas, uppercase everything
    raw = re.split(r'[\s,]+', text.strip())
    return [c.upper() for c in raw if c.strip()]

def validate_and_check(codes: List[str], history: Set[str]):
    invalid_format = []
    dup_in_batch = set()
    seen = set()

    for c in codes:
        if not FORMAT_RE.match(c):
            invalid_format.append(c)
        if c in seen:
            dup_in_batch.add(c)
        seen.add(c)

    valid_codes = [c for c in codes if c not in invalid_format]
    dup_vs_history = [c for c in valid_codes if c in history]
    unique_new = [c for c in valid_codes if c not in history and c not in dup_in_batch]

    return {
        'invalid_format': invalid_format,
        'duplicates_in_batch': sorted(dup_in_batch),
        'duplicates_vs_history': sorted(set(dup_vs_history)),
        'unique_new': sorted(set(unique_new))
    }

def write_report_csv(path: str, result: dict) -> None:
    import csv
    rows = []
    for c in result.get('invalid_format', []):
        rows.append((c, 'invalid'))
    for c in result.get('duplicates_in_batch', []):
        rows.append((c, 'duplicate_in_batch'))
    for c in result.get('duplicates_vs_history', []):
        rows.append((c, 'duplicate_in_history'))
    for c in result.get('unique_new', []):
        rows.append((c, 'unique'))

    # Deduplicate rows preserving last status precedence (unique shouldn't be overwritten)
    dedup = {}
    for code, status in rows:
        dedup[code] = status
    rows = sorted(dedup.items(), key=lambda x: (x[1], x[0]))

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['code', 'status'])
        writer.writerows(rows)

def main():
    ap = argparse.ArgumentParser(description="Validate and deduplicate Robux-style codes.")
    ap.add_argument('--input', '-i', help='Path to a text file containing codes (whitespace/comma separated). If omitted, reads from stdin.')
    ap.add_argument('--history', '-H', default='code_history.json', help='Path to JSON file storing history (default: code_history.json).')
    ap.add_argument('--save', action='store_true', help='Save unique, valid codes into the history after checking.')
    ap.add_argument('--report', '-r', help='Optional path to write a CSV report.')
    ap.add_argument('--init', action='store_true', help='Initialize/reset the history file to empty.')
    args = ap.parse_args()

    if args.init:
        save_history(args.history, set())
        print(f'Initialized empty history at: {args.history}')
        return

    # Load history
    history = load_history(args.history)

    # Read input
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        if sys.stdin.isatty():
            print("Paste codes, then press Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows):", file=sys.stderr)
        text = sys.stdin.read()

    codes = parse_codes_from_text(text)
    result = validate_and_check(codes, history)

    # Print human-readable summary
    print("=== Check Results ===")
    print(f"Total provided: {len(codes)}")
    print(f"Invalid format: {len(result['invalid_format'])}")
    print(f"Duplicates in batch: {len(result['duplicates_in_batch'])}")
    print(f"Duplicates vs history: {len(result['duplicates_vs_history'])}")
    print(f"Unique new (valid & not in history): {len(result['unique_new'])}")
    print()
    if result['invalid_format']:
        print("Invalid format:")
        for c in result['invalid_format']:
            print(f"  - {c}")
        print()
    if result['duplicates_in_batch']:
        print("Duplicates within input:")
        for c in result['duplicates_in_batch']:
            print(f"  - {c}")
        print()
    if result['duplicates_vs_history']:
        print("Duplicates versus history:")
        for c in result['duplicates_vs_history']:
            print(f"  - {c}")
        print()
    if result['unique_new']:
        print("Unique new codes:")
        for c in result['unique_new']:
            print(f"  - {c}")
        print()

    # Write CSV if requested
    if args.report:
        write_report_csv(args.report, result)
        print(f"CSV report written to: {os.path.abspath(args.report)}")

    # Save to history if requested
    if args.save:
        updated = set(history)
        updated.update(result['unique_new'])
        save_history(args.history, updated)
        print(f"History updated at: {args.history} (now has {len(updated)} codes)")


if __name__ == '__main__':
    main()
