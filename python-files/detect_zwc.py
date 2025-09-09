#!/usr/bin/env python3
# detect_zwc.py
# Detect zero-width / invisible Unicode characters in text.

import sys
import unicodedata
import argparse
import re
from typing import Iterable, Tuple

# Common zero-width / invisible code points and ranges
ZWC_POINTS = [
    0x00AD,  # SOFT HYPHEN (often invisible)
    0x034F,  # COMBINING GRAPHEME JOINER
    0x180E,  # MONGOLIAN VOWEL SEPARATOR (deprecated; often zero-width)
    0x200B, 0x200C, 0x200D,      # ZWSP, ZWNJ, ZWJ
    0x200E, 0x200F,              # LRM, RLM
    0x202A, 0x202B, 0x202C,      # LRE, RLE, PDF
    0x202D, 0x202E,              # LRO, RLO
    0x2060,                      # WORD JOINER
    0x2061, 0x2062, 0x2063, 0x2064,  # INVISIBLE FUNCTION/TIMES/SEPARATOR/PLUS
    0x2066, 0x2067, 0x2068, 0x2069,  # LRI, RLI, FSI, PDI
    0xFEFF,                      # ZERO WIDTH NO-BREAK SPACE / BOM
]

# Ranges (inclusive) for variation selectors (also zero width)
ZWC_RANGES = [
    (0xFE00, 0xFE0F),           # VARIATION SELECTOR-1..16
    (0xE0100, 0xE01EF),         # VARIATION SELECTOR-17..256 (supplementary)
]

def is_zwc(cp: int) -> bool:
    if cp in ZWC_POINTS:
        return True
    for lo, hi in ZWC_RANGES:
        if lo <= cp <= hi:
            return True
    return False

def find_zwc(text: str) -> Iterable[Tuple[int, int, str]]:
    """
    Yield (index, codepoint, name) for each zero-width/invisible char in text.
    """
    i = 0
    for ch in text:
        cp = ord(ch)
        if is_zwc(cp):
            try:
                name = unicodedata.name(ch)
            except ValueError:
                name = f"U+{cp:04X} (no name)"
            yield (i, cp, name)
        i += 1

def visualize_context(text: str, idx: int, radius: int = 12) -> str:
    start = max(0, idx - radius)
    end = min(len(text), idx + radius + 1)
    snippet = text[start:end]
    # Mark the exact position with ⟦ ⟧ so it shows up even if neighbors are invisible
    rel = idx - start
    return snippet[:rel] + "⟦⟧" + snippet[rel + 1:]

def scan_stream(name: str, text: str) -> int:
    found = 0
    for i, cp, nm in find_zwc(text):
        found += 1
        print(f"{name}:{i}: U+{cp:04X}  {nm}")
        print(f"  context: {visualize_context(text, i)}")
    return found

def main():
    ap = argparse.ArgumentParser(
        description="Detect zero-width / invisible Unicode characters in input text."
    )
    ap.add_argument(
        "paths", nargs="*", help="Files to scan. If omitted, reads from stdin or --text."
    )
    ap.add_argument(
        "--text", help="Scan this literal text (useful for quick checks)."
    )
    args = ap.parse_args()

    total_found = 0

    if args.text is not None:
        total_found += scan_stream("<arg:text>", args.text)

    if args.paths:
        for p in args.paths:
            try:
                data = open(p, "r", encoding="utf-8", errors="replace").read()
            except OSError as e:
                print(f"error: cannot read {p}: {e}", file=sys.stderr)
                continue
            total_found += scan_stream(p, data)
    elif args.text is None:
        # Read from stdin
        data = sys.stdin.read()
        total_found += scan_stream("<stdin>", data)

    if total_found == 0:
        print("No zero-width/invisible characters found.")
        sys.exit(0)
    else:
        print(f"\nTotal suspicious characters found: {total_found}")
        # Non-zero exit code so it can be used in CI/pre-commit hooks
        sys.exit(1)

if __name__ == "__main__":
    main()
