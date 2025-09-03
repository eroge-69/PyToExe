#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
David (Open APIs) — executable spider for open, no-key APIs
Runs against: Crossref, OpenAlex, PubMed, OpenLibrary, MusicBrainz

Usage:
  ./david_open_apis.py                 # runs with default query ("AI") and 5 rows per source
  ./david_open_apis.py "AI in Music"   # custom query
  ./david_open_apis.py -q "copyright" -n 10

Outputs JSON Lines to stdout (one record per line), only for:
  - status: "unregistered" (no ISWC + no ISRC)
  - status: "partial"      (missing/conflicting ISWC/ISRC)
"""

import asyncio
import json
import re
import sys
import argparse
from typing import Any, Dict, List, Optional, Tuple

import httpx

USER_AGENT = "metadata_integrity/1.0 (contact: you@example.com)"

# ---------------------------
# Utilities
# ---------------------------

def classify_record(item: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Return (status, reason) or (None, None) if fully registered."""
    iswc, isrc = item.get("iswc"), item.get("isrc")

    # Normalize list-y fields if needed
    def _norm(v):
        if isinstance(v, list):
            return [x for x in v if x]
        return v

    iswc = _norm(iswc)
    isrc = _norm(isrc)

    if not iswc and not isrc:
        return "unregistered", "no ISWC or ISRC"

    # Conflicts
    if isinstance(iswc, list) and len(set(iswc)) > 1:
        return "partial", f"conflicting ISWCs: {iswc}"
    if isinstance(isrc, list) and len(set(isrc)) > 1:
        return "partial", f"conflicting ISRCs: {isrc}"

    # Missing one
    if not iswc:
        return "partial", "missing ISWC"
    if not isrc:
        return "partial", "missing ISRC"

    # Both present (single values) -> considered registered
    return None, None

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def make_fingerprint(item: Dict[str, Any]) -> str:
    """Prefer identifiers; else use source + title slug."""
    if item.get("iswc"):
        v = item["iswc"]
        v = v[0] if isinstance(v, list) else v
        return f"iswc:{v}"
    if item.get("isrc"):
        v = item["isrc"]
        v = v[0] if isinstance(v, list) else v
        return f"isrc:{v}"
    doi = item.get("raw", {}).get("doi") or item.get("doi")
    if doi:
        return f"doi:{doi}"
    src = item.get("source", "unknown")
    title = slugify(item.get("title", ""))
    return f"src:{src}|title:{title}"

# ---------------------------
# Fetchers (Open, No-Key)
# ---------------------------

async def fetch_crossref(query: str, rows: int = 5) -> List[Dict[str, Any]]:
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": rows, "mailto": "you@example.com"}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
        out = []
        for it in items:
            title = (it.get("title") or [""])[0]
            doi = it.get("DOI")
            out.append({
                "source": "crossref",
                "industry": "publishing",
                "title": title,
                "raw": {"doi": doi, "issued": it.get("issued")},
                "doi": doi,
                "iswc": None,
                "isrc": None,
            })
        return out

async def fetch_openalex(query: str, rows: int = 5) -> List[Dict[str, Any]]:
    url = "https://api.openalex.org/works"
    params = {"search": query, "per-page": rows}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        items = r.json().get("results", [])
        out = []
        for it in items:
            title = it.get("display_name") or it.get("title") or ""
            doi = it.get("doi")
            out.append({
                "source": "openalex",
                "industry": "research",
                "title": title,
                "raw": {"doi": doi, "publication_year": it.get("publication_year")},
                "doi": doi,
                "iswc": None,
                "isrc": None,
            })
        return out

async def fetch_pubmed(query: str, rows: int = 5) -> List[Dict[str, Any]]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": rows}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        r = await client.get(base, params=params)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        out = []
        if not ids:
            return out
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        sr = await client.get(summary_url, params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
        sr.raise_for_status()
        res = sr.json().get("result", {})
        for pmid in ids:
            info = res.get(pmid, {})
            title = info.get("title", "")
            out.append({
                "source": "pubmed",
                "industry": "research",
                "title": title,
                "raw": {"pmid": pmid, "pubdate": info.get("pubdate")},
                "iswc": None,
                "isrc": None,
            })
        return out

async def fetch_openlibrary(query: str, rows: int = 5) -> List[Dict[str, Any]]:
    url = "https://openlibrary.org/search.json"
    params = {"q": query, "limit": rows}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        items = r.json().get("docs", [])
        out = []
        for it in items:
            title = it.get("title") or ""
            out.append({
                "source": "openlibrary",
                "industry": "publishing",
                "title": title,
                "raw": {"key": it.get("key"), "first_publish_year": it.get("first_publish_year")},
                "iswc": None,
                "isrc": None,
            })
        return out

async def fetch_musicbrainz(query: str, rows: int = 5) -> List[Dict[str, Any]]:
    url = "https://musicbrainz.org/ws/2/recording"
    params = {"query": query, "fmt": "json", "limit": rows}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        r = await client.get(url, params=params, headers=headers)
        r.raise_for_status()
        items = r.json().get("recordings", [])
        out = []
        for it in items:
            title = it.get("title") or ""
            iswc = it.get("iswc")  # string or None
            isrcs = it.get("isrcs")  # list or None
            isrc = isrcs if isrcs else None
            out.append({
                "source": "musicbrainz",
                "industry": "music",
                "title": title,
                "raw": it,
                "iswc": iswc,
                "isrc": isrc,
            })
        return out

OPEN_FETCHERS = [
    fetch_crossref,
    fetch_openalex,
    fetch_pubmed,
    fetch_openlibrary,
    fetch_musicbrainz,
]

# ---------------------------
# Runner
# ---------------------------

async def gather_all(query: str, rows: int = 5) -> List[Dict[str, Any]]:
    tasks = [f(query, rows) for f in OPEN_FETCHERS]
    results_nested = await asyncio.gather(*tasks, return_exceptions=True)

    # Flatten and handle exceptions
    results: List[Dict[str, Any]] = []
    for res in results_nested:
        if isinstance(res, Exception):
            # Emit an error record for visibility
            results.append({
                "source": "error",
                "industry": "general",
                "title": "<fetch failed>",
                "raw": {"error": str(res)},
                "iswc": None,
                "isrc": None,
                "status": "error",
                "reason": str(res),
            })
            continue
        results.extend(res or [])
    return results

def filter_and_dedupe(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for rec in records:
        status, reason = classify_record(rec)
        if not status:
            # fully registered → skip
            continue
        fp = make_fingerprint(rec)
        if fp in seen:
            continue
        seen.add(fp)
        rec["status"], rec["reason"], rec["fingerprint"] = status, reason, fp
        out.append(rec)
    return out

async def main():
    parser = argparse.ArgumentParser(description="David (Open APIs) – metadata gap spider")
    parser.add_argument("query", nargs="?", default="AI", help="Search query (default: AI)")
    parser.add_argument("-n", "--rows", type=int, default=5, help="Rows per source (default: 5)")
    args = parser.parse_args()

    records = await gather_all(args.query, rows=args.rows)
    filtered = filter_and_dedupe(records)

    for rec in filtered:
        # Print as JSON lines
        print(json.dumps(rec, ensure_ascii=False))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
