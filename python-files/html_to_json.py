#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def html_to_json():
    print("Bitte gib dein HTML ein (Strg+D oder Strg+Z + Enter zum Beenden):\n")
    # Mehrzeilige Eingabe
    html_lines = []
    try:
        while True:
            line = input()
            html_lines.append(line)
    except EOFError:
        pass

    html_content = "\n".join(html_lines)

    # JSON-Struktur
    data = [
        {
            "title": "Hier Titel eingeben",
            "category": "Hier Kategorie eingeben",
            "content": html_content
        }
    ]

    # JSON mit korrektem Escaping erstellen
    json_output = json.dumps(data, ensure_ascii=False, indent=2)
    
    print("\n--- JSON Ausgabe ---\n")
    print(json_output)
    
    # Optional: JSON-Datei speichern
    save = input("\nJSON auch in Datei speichern? (y/n): ").strip().lower()
    if save == "y":
        filename = input("Dateiname (z.B. newsletter.json): ").strip()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"JSON gespeichert in {filename}")

if __name__ == "__main__":
    html_to_json()
