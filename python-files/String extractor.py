# -*- coding: utf-8 -*-
import sys
import os

# Die zu suchenden Strings
search_strings = ["PcaSVc", "Dps", "Sha1", "Mdma"]

def extract_strings_from_file(filepath, search_strings):
    found = {s: [] for s in search_strings}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                for s in search_strings:
                    if s in line:
                        found[s].append((lineno, line.strip()))
    except Exception as e:
        print(f"Fehler beim Lesen von {filepath}: {e}")
    return found

def main(files):
    for file in files:
        print(f"\nDatei: {file}")
        results = extract_strings_from_file(file, search_strings)
        for s in search_strings:
            if results[s]:
                for lineno, line in results[s]:
                    print(f"  {s} gefunden in Zeile {lineno}: {line}")
            else:
                print(f"  {s} nicht gefunden.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bitte gib mindestens eine Datei als Argument an.")
        print("Beispiel: python extract_strings.py datei1.txt datei2.log")
        sys.exit(1)
    main(sys.argv[1:])