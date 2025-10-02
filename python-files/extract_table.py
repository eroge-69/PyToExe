#!/usr/bin/env python3
"""
extract_table_coords.py
Extrahiert konkrete Zellen unter einer Kopfzeile aus technischen Zeichnungen (PDF)
und speichert das Ergebnis als Excel (auswertung.xlsx).

Usage:
    python extract_table_coords.py input.pdf
    python extract_table_coords.py input.pdf --out result.xlsx --debug
"""

import pdfplumber
import re
import sys
import os
from openpyxl import Workbook
from datetime import datetime

WANTED_FIELDS = [
    "Zeichnungs-Nr",
    "Titel",
    "Material",
    "Blechstärke",
    "Gewicht",
    "Dimension",
    "Abwicklung X",
    "Abwicklung Y"
]

# ---- Hilfsfunktionen ----
def normalize(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    # Umlaute -> ae oe ue etc
    s = s.replace("ä", "ae").replace("Ä", "Ae").replace("ö", "oe").replace("Ö", "Oe").replace("ü", "ue").replace("Ü", "Ue").replace("ß", "ss")
    s = s.lower()
    # nur alphanumerisch behalten
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def log_debug(msg, dbg_list=None):
    print(msg)
    if dbg_list is not None:
        dbg_list.append(msg)

def group_words_to_lines(words, y_tol=3):
    """
    words: list of dicts with keys 'text','x0','x1','top','bottom'
    returns list of lines: each line is dict {'top': avg_top, 'items': [word,...]}
    sorted from top->down (small top -> large top)
    """
    if not words:
        return []
    # sort by top asc (top smaller = physically higher on page), then x0 asc
    sorted_words = sorted(words, key=lambda w: (round(w['top'],3), w['x0']))
    lines = []
    for w in sorted_words:
        if not lines:
            lines.append({'top': w['top'], 'items': [w]})
            continue
        last = lines[-1]
        if abs(last['top'] - w['top']) <= y_tol:
            last['items'].append(w)
            # keep top as average to be robust
            last['top'] = (last['top'] * (len(last['items'])-1) + w['top']) / len(last['items'])
        else:
            lines.append({'top': w['top'], 'items': [w]})
    # sort items in each line by x0
    for l in lines:
        l['items'].sort(key=lambda it: it['x0'])
    return lines

def match_header_in_line(line_items, wanted=WANTED_FIELDS, max_tokens_per_field=6):
    """
    Versucht die header-Felder in dieser Zeile (items) in der gewünschten Reihenfolge zu matchen.
    Gibt None zurück, falls nicht matchbar.
    Ansonsten: list von dicts mit start_idx,end_idx,left_x,right_x,center_x
    """
    tokens = [it['text'] for it in line_items]
    norms = [normalize(t) for t in tokens]
    n = len(tokens)
    pos = 0
    result = []
    for field in wanted:
        want = normalize(field)
        found = None
        for i in range(pos, n):
            comb = ""
            for j in range(i, min(n, i + max_tokens_per_field)):
                comb += norms[j]
                # akzeptieren wenn comb enthält want oder umgekehrt (Split/Bindefugen)
                if want in comb or comb in want:
                    left_x = line_items[i]['x0']
                    right_x = line_items[j]['x1']
                    center_x = (left_x + right_x) / 2.0
                    found = {'start_idx': i, 'end_idx': j, 'left_x': left_x, 'right_x': right_x, 'center_x': center_x}
                    break
            if found:
                break
        if not found:
            return None
        result.append(found)
        pos = found['end_idx'] + 1
    return result

def find_value_line_for_header(lines, header_line_index, header_cols):
    """
    Wir versuchen zuerst die unmittelbar folgende Zeile (index+1) zu nehmen.
    Falls diese sehr weit vertikal entfernt ist, suchen wir die nächste Zeile mit top > header_bottom (minimal).
    """
    header_line = lines[header_line_index]
    # determine header bottom as max bottom of header items
    header_bottom = max(it.get('bottom', it.get('top', 0)) for it in header_line['items'])
    # candidate: next line
    if header_line_index + 1 < len(lines):
        cand = lines[header_line_index + 1]
        # if top is reasonably close, accept
        if (cand['top'] - header_bottom) >= 0 and (cand['top'] - header_bottom) < 200:
            return header_line_index + 1
    # else search the line with minimal top greater than header_bottom
    best_idx = None
    best_diff = None
    for idx in range(header_line_index + 1, len(lines)):
        diff = lines[idx]['top'] - header_bottom
        if diff >= 0:
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_idx = idx
    return best_idx

def assign_values_to_columns(value_items, header_cols):
    """
    value_items: list of words in the value line (sorted by x0)
    header_cols: list with centers
    returns list of strings per column
    """
    centers = [ (c['left_x'] + c['right_x']) / 2.0 for c in header_cols ]
    n = len(centers)
    # build boundaries (midpoints)
    left_bounds = []
    right_bounds = []
    for i in range(n):
        left = centers[i] - 99999 if i == 0 else (centers[i-1] + centers[i]) / 2.0
        right = centers[i] + 99999 if i == n-1 else (centers[i] + centers[i+1]) / 2.0
        left_bounds.append(left)
        right_bounds.append(right)
    cols = [[] for _ in range(n)]
    for w in value_items:
        xcen = (w['x0'] + w['x1']) / 2.0
        assigned = False
        for i in range(n):
            if xcen >= left_bounds[i] and xcen <= right_bounds[i]:
                cols[i].append((w['x0'], w['text']))
                assigned = True
                break
        if not assigned:
            # fallback nearest center
            dmin = None
            idx = 0
            for i,c in enumerate(centers):
                d = abs(xcen - c)
                if dmin is None or d < dmin:
                    dmin = d; idx = i
            cols[idx].append((w['x0'], w['text']))
    # join each column by ascending x
    out = []
    for arr in cols:
        arr_sorted = sorted(arr, key=lambda t: t[0])
        text = " ".join([t[1] for t in arr_sorted]).strip()
        out.append(re.sub(r'\s+', ' ', text))
    return out

# ---- Hauptfunktion ----
def extract_table_from_pdf(pdf_path, out_excel="auswertung.xlsx", debug=False):
    dbg_lines = []
    if debug:
        log_debug(f"Start Extraction: {pdf_path}  ({datetime.now()})", dbg_lines)
    extracted = {}
    found_any = False

    with pdfplumber.open(pdf_path) as pdf:
        for pnum, page in enumerate(pdf.pages, start=1):
            if debug:
                log_debug(f"--- Seite {pnum} ---", dbg_lines)
            # words mit Positionen
            words = page.extract_words(use_text_flow=True, keep_blank_chars=False)
            # normalize keys (pdfplumber liefert 'x0','x1','top','bottom','text')
            words_clean = []
            for w in words:
                words_clean.append({
                    'text': w.get('text', ''),
                    'x0': float(w.get('x0', 0)),
                    'x1': float(w.get('x1', 0)),
                    'top': float(w.get('top', 0)),
                    'bottom': float(w.get('bottom', w.get('top',0)))
                })
            if not words_clean:
                if debug:
                    log_debug("Seite hat keine Text-Wörter.", dbg_lines)
                continue

            # Gruppiere in Zeilen
            lines = group_words_to_lines(words_clean, y_tol=3)

            if debug:
                log_debug(f"Gefundene Zeilen (oben->unten): {len(lines)}", dbg_lines)
                for i,l in enumerate(lines[:40]):
                    sample = " | ".join([f'"{it["text"]}"@{int(it["x0"])}' for it in l['items']])
                    log_debug(f"  Zeile {i+1} top={int(l['top'])}: {sample}", dbg_lines)

            # Suche Header-Zeile
            for idx, line in enumerate(lines):
                header_cols = match_header_in_line(line['items'], WANTED_FIELDS)
                if header_cols:
                    # Debug Info
                    if debug:
                        hdr_sample = " | ".join([f'{WANTED_FIELDS[i]}[{line["items"][col["start_idx"]]["text"]}..{line["items"][col["end_idx"]]["text"]}]' for i,col in enumerate(header_cols)])
                        log_debug(f"Header-Linie gefunden auf Seite {pnum}, Zeile {idx+1}: {hdr_sample}", dbg_lines)
                        log_debug("Header-Spalten (center x): " + ", ".join([str(int((c['left_x']+c['right_x'])/2)) for c in header_cols]), dbg_lines)

                    # finde die passende Wert-Zeile direkt darunter
                    val_idx = find_value_line_for_header(lines, idx, header_cols)
                    if val_idx is None:
                        if debug:
                            log_debug("Keine passende Wert-Zeile direkt darunter gefunden (val_idx is None). Versuche weiter.", dbg_lines)
                        continue

                    # In manchen PDFs kann die "Wertzeile" auf mehrere folgende Zeilen verteilt sein.
                    # Zuerst nehmen wir die gefundene val_idx; falls leer, sammeln wir evtl. mehrere Zeilen.
                    value_line = lines[val_idx]
                    # Falls value_line leer (keine items), versuchen wir mehrere nachfolgende Zeilen zu kombinieren (bis 3 Zeilen)
                    combined_items = list(value_line['items'])
                    # join maybe row+1, row+2 if combined is very short
                    for k in range(1,3):
                        if len(combined_items) == 0 and val_idx + k < len(lines):
                            combined_items.extend(lines[val_idx + k]['items'])

                    # Wenn immer noch nichts, skip
                    if len(combined_items) == 0:
                        if debug:
                            log_debug("Wertzeile hat keine Items. Suche nächste Zeile.", dbg_lines)
                        continue

                    # Jetzt extrahiere Werte per Spalte
                    values = assign_values_to_columns(combined_items, header_cols)
                    # Mappe
                    for i, field in enumerate(WANTED_FIELDS):
                        extracted[field] = values[i] if i < len(values) else ""
                    found_any = True

                    # Debug: zeige extrahierte values
                    if debug:
                        log_debug("Extrahierte Werte:", dbg_lines)
                        for f in WANTED_FIELDS:
                            log_debug(f'  {f}: "{extracted.get(f,"")}"', dbg_lines)
                    break  # stop lines loop if we found header on this page

            if found_any:
                break  # stop pages loop

    # Ergebnis schreiben
    wb = Workbook()
    ws = wb.active
    ws.title = "Zeichnung"
    # Kopfzeile
    ws.append(WANTED_FIELDS)
    # Werte (falls nicht gefunden => leere Strings)
    ws.append([extracted.get(f, "") for f in WANTED_FIELDS])
    wb.save(out_excel)

    if debug:
        # zusätzlich debug log in Datei schreiben
        try:
            logf = os.path.splitext(out_excel)[0] + "_debug_log.txt"
            with open(logf, "w", encoding="utf-8") as fh:
                fh.write("\n".join(dbg_lines))
            log_debug(f"\n✅ Excel geschrieben: {out_excel}", dbg_lines)
            log_debug(f"✅ Debug-Log geschrieben: {logf}", dbg_lines)
        except Exception as e:
            log_debug(f"Warnung: Debug-Log konnte nicht geschrieben werden: {e}", dbg_lines)
    else:
        print(f"✅ Excel geschrieben: {out_excel}")

    return extracted

# ---- CLI ----
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extrahiere Werte direkt unter Header-Zeile aus PDF und schreibe Excel.")
    parser.add_argument("pdf", help="Input PDF Datei")
    parser.add_argument("--out", "-o", help="Output Excel Datei", default="auswertung.xlsx")
    parser.add_argument("--debug", "-d", help="Debug-Ausgabe (Konsolen- + debug logfile)", action="store_true")
    args = parser.parse_args()
    if not os.path.exists(args.pdf):
        print("Fehler: PDF nicht gefunden:", args.pdf)
        sys.exit(1)
    extract_table_from_pdf(args.pdf, args.out, debug=args.debug)

if __name__ == "__main__":
    main()
