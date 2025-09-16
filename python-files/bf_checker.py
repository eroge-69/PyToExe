#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Breastfeeding Compatibility Checker (Prototype)

Quickly aggregates compatibility information for a drug from:
 - e-lactancia (APILAM)
 - LactMed (NIH / NCBI Bookshelf)

Usage:
  python bf_checker.py ibuprofen
  python bf_checker.py "sertraline"
  python bf_checker.py -o results.csv paracetamol ibuprofen sertraline

Notes:
 - Uses only Python standard library (urllib, re, html.parser)
 - Web scraping is best-effort; sites can change HTML structure.
 - Output: clean Markdown to console; optional CSV via -o
"""

import sys
import re
import csv
import json
import time
import argparse
from urllib.parse import quote_plus, urljoin
from urllib.request import Request, urlopen
from html import unescape

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

BASE_ELACTANCIA = "https://e-lactancia.org/"
BASE_NCBI_BOOKS = "https://www.ncbi.nlm.nih.gov/books/"


def http_get(url, timeout=20):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as r:
        content = r.read()
        # try to decode as utf-8; fallback latin-1
        try:
            return content.decode("utf-8", errors="replace")
        except Exception:
            return content.decode("latin-1", errors="replace")


def clean_text(text):
    text = unescape(text)
    text = re.sub(r"<\/?(script|style)[^>]*>.*?<\/(script|style)>", " ", text, flags=re.S|re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_elactancia(drug):
    """Return dict with keys: source, url, title, risk, last_updated, snippet"""
    search_url = BASE_ELACTANCIA + "?s=" + quote_plus(drug)
    html = http_get(search_url)

    # Find first result link to a product/tradename page under /breastfeeding/
    # Prefer exact product page
    candidates = re.findall(r'href=\"(https?://e-lactancia\\.org/(?:breastfeeding/[^\"\\s]+))\"', html)
    # Deduplicate while preserving order
    seen = set()
    links = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            links.append(c)
    url = links[0] if links else search_url

    page = http_get(url)
    text = clean_text(page)

    # Extract risk label by looking for common Spanish labels near top
    risk_labels = [
        ("Muy inseguro", "Very Unsafe / Contraindicated"),
        ("Poco seguro", "Limited compatibility / Use with caution"),
        ("Bastante seguro", "Probably compatible"),
        ("Compatible", "Compatible / Preferred"),
        ("Seguro, mejor opción", "Very low risk / Preferred"),
    ]

    risk = None
    for es, en in risk_labels:
        if re.search(re.escape(es), text, flags=re.I):
            risk = en
            break

    # Extract last updated date if present
    m_date = re.search(r"Última actualización\s*:\s*([0-9]{1,2}\s+de\s+[A-Za-zñáéíóú]+\s+de\s+[0-9]{4})", text)
    last_updated = m_date.group(1) if m_date else None

    # Make a short snippet: first 320 chars of intro
    snippet = None
    m_intro = re.search(r"(Ibuprofeno|[A-Za-zÁÉÍÓÚÑñ\- ]{3,40})\s+Compatible.*?\.", text)
    if not m_intro:
        # fallback: first 300 chars
        snippet = text[:300]
    else:
        snippet = m_intro.group(0)

    return {
        "source": "e-lactancia",
        "url": url,
        "title": f"{drug} — e-lactancia",
        "risk": risk,
        "last_updated": last_updated,
        "snippet": snippet,
    }


def fetch_lactmed(drug):
    """Search NCBI Bookshelf for LactMed record and extract summary paragraph.
       Return dict with keys: source, url, title, summary.
    """
    # Search Books for lactmed + drug
    q = quote_plus(f"lactmed {drug}")
    search_url = BASE_NCBI_BOOKS + f"?term={q}"
    html = http_get(search_url)

    # Find a result that looks like a LactMed book chapter (NBK id)
    # e.g., href="/books/NBK501922/" (homepage) or specific NBK pages
    links = re.findall(r'href=\"(/books/NBK[0-9]+[^\"#>]*)\"', html)

    # Prefer links that include "lactmed" keyword nearby or in surrounding context
    chosen = None
    for m in re.finditer(r'<a[^>]+href=\"(/books/NBK[0-9]+[^\"#>]*)\"[^>]*>(.*?)</a>', html, flags=re.I|re.S):
        href, label = m.group(1), clean_text(m.group(2)).lower()
        # If label or context mentions Drugs and Lactation Database (LactMed)
        context = html[max(0, m.start()-300): m.end()+300].lower()
        if "lactmed" in label or "lactmed" in context:
            chosen = href
            break
    if not chosen:
        chosen = links[0] if links else None

    if not chosen:
        return {
            "source": "LactMed",
            "url": search_url,
            "title": f"{drug} — LactMed (search)",
            "summary": "No LactMed record found via search.",
        }

    url = urljoin(BASE_NCBI_BOOKS, chosen)
    page = http_get(url)
    text = page

    # Extract "Summary of Use during Lactation" section
    # Match heading text and capture following paragraphs until next <h2/3>
    m = re.search(r'(Summary of Use during Lactation.*?)(?:<h[23]|\Z)', text, flags=re.I|re.S)
    if m:
        summary_html = m.group(1)
        summary = clean_text(summary_html)
        # Truncate overly long summaries
        summary = re.sub(r"^Summary of Use during Lactation\s*", "", summary, flags=re.I)
        summary = summary.strip()
        if len(summary) > 1200:
            summary = summary[:1200].rsplit(" ", 1)[0] + " …"
    else:
        # Fallback: first paragraph
        summary = clean_text(text)[:600]

    title_m = re.search(r"<title>(.*?)</title>", page, flags=re.I|re.S)
    title = clean_text(title_m.group(1)) if title_m else f"{drug} — LactMed"

    return {
        "source": "LactMed",
        "url": url,
        "title": title,
        "summary": summary,
    }


def combine(elact, lactmed):
    """Create a concise, merged Markdown summary."""
    lines = []
    lines.append(f"# {elact['title'].split(' — ')[0].title()} — Breastfeeding Compatibility\n")
    # Quick take
    quick = ""
    if elact.get("risk"):
        quick = f"**Quick take:** e‑lactancia: {elact['risk']}."
    else:
        quick = "**Quick take:** e‑lactancia: no explicit risk label found."

    lines.append(quick + "\n")

    # e-lactancia block
    lines.append("## e‑lactancia\n")
    if elact.get("risk"):
        lines.append(f"• **Risk:** {elact['risk']}")
    if elact.get("last_updated"):
        lines.append(f"• **Last updated:** {elact['last_updated']}")
    lines.append(f"• **Record:** {elact['url']}")
    if elact.get("snippet"):
        lines.append(f"• **Notes:** {elact['snippet']}")

    # LactMed block
    lines.append("\n## LactMed (NIH/NCBI)\n")
    lines.append(f"• **Record:** {lactmed['url']}")
    if lactmed.get("summary"):
        lines.append(f"• **Summary:** {lactmed['summary']}")

    # Footer
    lines.append("\n*This summary does not replace clinical judgment. Consider infant gestational age, comorbidities, dosage, route, and duration.*")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Breastfeeding compatibility checker (e-lactancia + LactMed)")
    ap.add_argument("drugs", nargs="+", help="Drug names to check (e.g., ibuprofen sertraline)")
    ap.add_argument("-o", "--output", help="Optional CSV output file")
    args = ap.parse_args()

    rows = []
    for drug in args.drugs:
        try:
            el = fetch_elactancia(drug)
        except Exception as e:
            el = {"source": "e-lactancia", "url": "", "title": f"{drug} — e-lactancia", "risk": None, "last_updated": None, "snippet": f"Error: {e}"}
        time.sleep(0.6)  # be polite
        try:
            lm = fetch_lactmed(drug)
        except Exception as e:
            lm = {"source": "LactMed", "url": "", "title": f"{drug} — LactMed", "summary": f"Error: {e}"}
        print(combine(el, lm))
        print("\n" + "="*80 + "\n")

        rows.append({
            "drug": drug,
            "elactancia_risk": el.get("risk") or "",
            "elactancia_url": el.get("url") or "",
            "elactancia_last_updated": el.get("last_updated") or "",
            "lactmed_url": lm.get("url") or "",
            "lactmed_summary": lm.get("summary") or "",
        })

    if args.output:
        fieldnames = list(rows[0].keys()) if rows else ["drug"]
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"Saved CSV to {args.output}")

if __name__ == "__main__":
    main()
