#!/usr/bin/env python3
"""
license_cli.py

Kleines CLI-Tool zum legalen Erzeugen und Validieren von Freischaltcodes (Beispiel-/Testzwecke).
Hinweis: Dieses Tool dient nur zur Muster-Generierung und -Validierung eigener oder autorisierter
Schlüssel und hilft **nicht**, Kopierschutz zu umgehen oder fremde Lizenzen zu knacken.

Features:
- Generieren verschiedener Formate (z. B. 9 uppercase, 12 uppercase, gruppiert 3-3-3 oder 4-4-4)
- Option: Letztes Zeichen als Prüfbuchstabe (Checksumme: sum von A=0..Z=25 mod26)
- Option: Alphabet ohne leicht verwechselbare Buchstaben (keine I, O)
- Validierung gegen Regex und optional gegen Prüfsummenregel
- Ausgabe in Konsole oder in Datei

Benutzung:
  Generieren:  python license_cli.py gen --format 12 --count 5
  Generieren mit Prüfziffer: python license_cli.py gen --format checksum-last-12 --count 5
  Generieren gruppiert: python license_cli.py gen --format 3-3-3 --sep - --count 3
  Prüfen: python license_cli.py validate --codes NWCCCYYRFUTB ABCDEFGHIJKL
  Prüfen aus Datei: python license_cli.py validate --infile codes.txt
"""

from __future__ import annotations
import argparse
import random
import re
import string
from typing import List, Tuple, Optional

# ------------------------ Generator-Funktionen ------------------------
DEFAULT_ALPHABET = string.ascii_uppercase
ALPHABET_NO_CONFUSE = ''.join(c for c in string.ascii_uppercase if c not in ("I","O"))

def gen_random_upper(length: int = 9, alphabet: str = DEFAULT_ALPHABET) -> str:
    return ''.join(random.choice(alphabet) for _ in range(length))

def gen_grouped(total_length: int, group_size: int = 3, sep: str = '-') -> str:
    if total_length % group_size != 0:
        raise ValueError("total_length must be divisible by group_size")
    parts = [''.join(random.choice(DEFAULT_ALPHABET) for _ in range(group_size))
             for _ in range(total_length // group_size)]
    return sep.join(parts)

def checksum_last_char(body: str) -> str:
    """Berechnet Prüfbuchstaben als (Summe(A=0..Z=25) mod 26) -> Buchstabe"""
    vals = [(ord(c) - 65) for c in body]
    ch_val = sum(vals) % 26
    return chr(ch_val + 65)

def gen_with_checksum(total_length: int = 9, alphabet: str = DEFAULT_ALPHABET) -> str:
    if total_length < 2:
        raise ValueError("total_length must be >= 2 for checksum scheme")
    body_len = total_length - 1
    body = ''.join(random.choice(alphabet) for _ in range(body_len))
    chk = checksum_last_char(body)
    return body + chk

def gen_no_confuse(length: int = 9) -> str:
    return gen_random_upper(length, alphabet=ALPHABET_NO_CONFUSE)

# ------------------------ Validator-Funktionen ------------------------

def is_upper_n(code: str, n: int) -> bool:
    return bool(re.fullmatch(rf"[A-Z]{{{n}}}", code))

def is_grouped(code: str, group_size: int, groups: int, sep: str) -> bool:
    pattern = rf"^(?:[A-Z]{{{group_size}}})(?:{re.escape(sep)}[A-Z]{{{group_size}}}){{{groups-1}}}$"
    return bool(re.fullmatch(pattern, code))

def validate_checksum(code: str) -> bool:
    """Validiert die Prüfsumme, wenn letzte Stelle Prüfbuchstabe ist.
    Erwartet: code ohne Trennzeichen, mindestens 2 Zeichen lang.
    """
    code_plain = re.sub(r"[^A-Z]", "", code)
    if len(code_plain) < 2:
        return False
    body, chk = code_plain[:-1], code_plain[-1]
    return checksum_last_char(body) == chk

# ------------------------ CLI & Hilfsroutinen ------------------------

def generate_codes(format_spec: str, count: int = 1, sep: str = '-', checksum: bool = False,
                   no_confuse: bool = False) -> List[str]:
    out = []
    alphabet = ALPHABET_NO_CONFUSE if no_confuse else DEFAULT_ALPHABET

    # format_spec kann sein: '9', '12', '3-3-3', 'checksum-last-12' etc.
    if re.fullmatch(r"\d+", format_spec):
        n = int(format_spec)
        for _ in range(count):
            if checksum:
                out.append(gen_with_checksum(n, alphabet=alphabet))
            else:
                out.append(gen_random_upper(n, alphabet=alphabet))
        return out

    m = re.fullmatch(r"(\d+)-(\d+)-(\d+)", format_spec)
    if m:
        groups = [int(m.group(i)) for i in range(1,4)]
        total = sum(groups)
        # if sep is '' then no separators
        for _ in range(count):
            parts = [''.join(random.choice(alphabet) for _ in range(g)) for g in groups]
            out.append(sep.join(parts))
        return out

    # support e.g. 'checksum-last-12'
    m2 = re.fullmatch(r"checksum-last-(\d+)", format_spec)
    if m2:
        n = int(m2.group(1))
        for _ in range(count):
            out.append(gen_with_checksum(n, alphabet=alphabet))
        return out

    raise ValueError(f"Unbekanntes format_spec: {format_spec}")

def validate_codes(codes: List[str], expected_format: Optional[str] = None, expect_checksum: bool = False,
                   sep: str = '-') -> List[Tuple[str, bool, Optional[str]]]:
    """Gibt Liste von Tuples zurück: (code, is_valid_format, reason)
    reason ist ein kurzer Hinweis (z. B. 'format mismatch', 'checksum invalid', 'ok').
    """
    results = []
    for code in codes:
        ok = True
        reason = 'ok'
        plain = re.sub(r"[^A-Z]", "", code)
        if expected_format:
            if re.fullmatch(r"\d+", expected_format):
                n = int(expected_format)
                if not is_upper_n(plain, n):
                    ok = False
                    reason = f'expected {n} uppercase letters (found {len(plain)})'
            else:
                m = re.fullmatch(r"(\d+)-(\d+)-(\d+)", expected_format)
                if m:
                    groups = [int(m.group(i)) for i in range(1,4)]
                    total = sum(groups)
                    if not is_upper_n(plain, total):
                        ok = False
                        reason = f'expected total {total} uppercase letters (found {len(plain)})'
                elif expected_format.startswith('checksum-last-'):
                    # handled below
                    pass
                else:
                    # unknown spec: skip strict format check
                    pass

        if ok and expect_checksum:
            if not validate_checksum(code):
                ok = False
                reason = 'checksum invalid'

        results.append((code, ok, reason))
    return results

# ------------------------ Main / Argparse ------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Generiert und validiert Beispiel-Freischaltcodes (legal).')
    sub = p.add_subparsers(dest='cmd', required=True)

    g = sub.add_parser('gen', help='Generiere Codes')
    g.add_argument('--format', '-f', default='9',
                   help="Format: z.B. '9', '12', '3-3-3', 'checksum-last-12' (default: 9)")
    g.add_argument('--count', '-c', type=int, default=5, help='Anzahl der zu erzeugenden Codes')
    g.add_argument('--sep', default='-', help='Trennzeichen bei Gruppen (default: -)')
    g.add_argument('--checksum', action='store_true', help='Letztes Zeichen als Prüfbuchstabe einsetzen (nur für numeric formats)')
    g.add_argument('--no-confuse', action='store_true', help='Keine I,O in Alphabet verwenden')
    g.add_argument('--outfile', '-o', help='Datei, in die die erzeugten Codes geschrieben werden')

    v = sub.add_parser('validate', help='Validiere Codes')
    v.add_argument('--codes', nargs='*', help='Liste von Codes, z.B. ABCDEF...')
    v.add_argument('--infile', help='Textdatei mit Codes (eine pro Zeile)')
    v.add_argument('--format', '-f', help="Erwartetes Format für Prüfung: '9', '12', '3-3-3', 'checksum-last-12'")
    v.add_argument('--expect-checksum', action='store_true', help='Erwarte, dass letztes Zeichen Prüfbuchstabe ist')

    return p.parse_args()

def main() -> None:
    args = parse_args()

    if args.cmd == 'gen':
        try:
            codes = generate_codes(args.format, count=args.count, sep=args.sep, checksum=args.checksum, no_confuse=args.no_confuse)
        except ValueError as e:
            print('Fehler beim Generieren:', e)
            return
        if args.outfile:
            with open(args.outfile, 'w', encoding='utf-8') as f:
                for c in codes:
                    f.write(c + '\\n')
            print(f'{len(codes)} Codes in {args.outfile} geschrieben.')
        else:
            for c in codes:
                print(c)

    elif args.cmd == 'validate':
        codes: List[str] = []
        if args.infile:
            with open(args.infile, 'r', encoding='utf-8') as f:
                for line in f:
                    s = line.strip()
                    if s:
                        codes.append(s)
        if args.codes:
            codes.extend(args.codes)
        if not codes:
            print('Keine Codes angegeben. Nutze --codes oder --infile.')
            return
        results = validate_codes(codes, expected_format=args.format, expect_checksum=args.expect_checksum)
        ok_count = 0
        for code, ok, reason in results:
            status = 'OK' if ok else 'INVALID'
            print(f'{code}\\t{status}\\t{reason}')
            if ok:
                ok_count += 1
        print(f'Valid: {ok_count}/{len(results)}')

if __name__ == '__main__':
    main()
