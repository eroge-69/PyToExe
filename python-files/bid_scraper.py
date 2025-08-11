#!/usr/bin/env python
# bid_scraper.py
import re
import sys
import time
import json
import math
import argparse
from pathlib import Path
from datetime import datetime
from dateutil import parser as dateparser

import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---------- Config you can tweak ----------
NETWORK_IDLE_WAIT = 30000     # ms
PAGE_LOAD_TIMEOUT = 45000     # ms
STEP_DELAY_MIN = 0.4          # seconds
STEP_DELAY_MAX = 1.1
SCROLL_STEPS = 8
SCROLL_PAUSE = 0.6
MAX_PAGINATION_CLICKS = 20
# ------------------------------------------

def human_delay():
    import random
    time.sleep(random.uniform(STEP_DELAY_MIN, STEP_DELAY_MAX))

def norm_text(s):
    return re.sub(r"\s+", " ", s).strip()

def parse_date_maybe(text):
    """Try to parse a date from messy text."""
    if not text:
        return None
    # common patterns first
    m = re.search(r'(\b\d{1,2}/\d{1,2}/\d{2,4}\b)(?:\s+at\s+(\d{1,2}:\d{2}\s*[AP]M)?)?', text, re.I)
    if m:
        try:
            return dateparser.parse(" ".join([x for x in m.groups() if x]))
        except Exception:
            pass
    # fallback
    try:
        return dateparser.parse(text, fuzzy=True)
    except Exception:
        return None

def text_content_or_empty(el):
    try:
        return norm_text(el.inner_text())
    except Exception:
        return ""

def wait_full_render(page):
    try:
        page.wait_for_load_state("domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
    except PWTimeout:
        pass
    try:
        page.wait_for_load_state("networkidle", timeout=NETWORK_IDLE_WAIT)
    except PWTimeout:
        pass

def slow_scroll(page, steps=SCROLL_STEPS):
    for _ in range(steps):
        page.mouse.wheel(0, 1200)
        time.sleep(SCROLL_PAUSE)

def detect_human_verification(page):
    html = page.content().lower()
    hints = [
        "press & hold", "are you human", "human verification",
        "cloudflare", "cf-challenge", "verify you are", "captcha"
    ]
    return any(h in html for h in hints)

def pause_for_verification():
    print("\n⚠️  Human verification detected. Complete it in the **open browser**.")
    input("When finished, press ENTER here to continue... ")

# ---------- Extractors ----------

def extract_questcdn(page, base_url):
    """
    Works for URLs like:
    https://qcpi.questcdn.com/cdn/posting/?projType=all&provider=...&group=...
    """
    rows = []
    try:
        # table rows
        page.wait_for_selector("table tbody tr", timeout=15000)
        trs = page.locator("table tbody tr")
        count = trs.count()
        for i in range(count):
            tr = trs.nth(i)
            cols = tr.locator("td")
            if cols.count() < 6:
                continue

            # fields
            title = text_content_or_empty(cols.nth(3))
            due = text_content_or_empty(cols.nth(4))
            owner = text_content_or_empty(cols.nth(6)) if cols.count() > 6 else ""
            city  = text_content_or_empty(cols.nth(5)) if cols.count() > 5 else ""
            link = ""
            try:
                a = cols.nth(3).locator("a")
                if a.count() > 0:
                    link = a.first.get_attribute("href") or ""
                    if link and link.startswith("/"):
                        link = "https://qcpi.questcdn.com" + link
            except Exception:
                pass

            # If we can, click through to get more
            scope = ""
            bidnum = ""
            if link:
                with page.expect_navigation(wait_until="domcontentloaded", timeout=20000):
                    a.first.click()
                wait_full_render(page)
                # Read details on the detail page if present
                try:
                    h1 = page.locator("h1").first.inner_text()
                    if h1:
                        title = norm_text(h1)
                except Exception:
                    pass
                try:
                    # common labels on Quest
                    t = norm_text(page.locator("body").inner_text())
                    m = re.search(r"Quest Number[:\s]+(\d+)", t, re.I)
                    if m: bidnum = m.group(1)
                    # Due date sometimes displayed as "Closing Date: Tue, 08/26/2025 01:00 PM CDT"
                    m2 = re.search(r"(Closing|Bid)\s*Date[:\s]+([^\n]+)", t, re.I)
                    if m2:
                        due = norm_text(m2.group(2))
                    # Description block
                    # (Keep short to avoid scraping entire page)
                    desc_m = re.search(r"(Project Description|Description)[:\s]+(.{0,600})", t, re.I|re.S)
                    if desc_m:
                        scope = norm_text(desc_m.group(2))
                except Exception:
                    pass
                page.go_back()
                wait_full_render(page)

            rows.append(dict(
                Source_URL=base_url,
                Bid_Name=title,
                Bid_Number=bidnum,
                Bid_Date=due,
                Estimated_Cost="",
                Owner=owner,
                Location=city,
                Scope=scope,
                Direct_URL=link or base_url,
                Comments=""
            ))
            human_delay()
    except Exception as e:
        return [], f"Extractor error: {e}"
    return rows, ""

def extract_ionwave(page, base_url):
    """
    IonWave list pages often show events in a grid with titles linking to details.
    """
    rows = []
    try:
        slow_scroll(page, 6)
        cards = page.locator("a[href*='Event'] , a[href*='SourcingEvent'], a[href*='bid']")
        # Fallback to clickable rows:
        if cards.count() == 0:
            cards = page.locator("table tbody tr a")
        seen = set()
        max_cards = min(50, cards.count())
        for i in range(max_cards):
            a = cards.nth(i)
            href = a.get_attribute("href") or ""
            if href in seen:
                continue
            seen.add(href)
            title = norm_text(a.inner_text())
            # Open in same tab
            a.click()
            wait_full_render(page)
            t = norm_text(page.locator("body").inner_text())
            # Attempt to parse fields
            bidnum = ""
            due = ""
            owner = ""
            city = ""
            scope = ""

            m = re.search(r"(Bid|Due|Close)\s*Date[:\s]+([^\n]+)", t, re.I)
            if m: due = m.group(2)

            m = re.search(r"(Solicitation|Bid|Event)\s*(No\.|Number)[:\s]+([A-Za-z0-9\-_/]+)", t, re.I)
            if m: bidnum = m.group(3)

            m = re.search(r"(Owner|Agency|Department)[:\s]+([^\n]+)", t, re.I)
            if m: owner = m.group(2)

            m = re.search(r"(Location|City)[:\s]+([^\n]+)", t, re.I)
            if m: city = m.group(2)

            # Quick scope grab (short)
            m = re.search(r"(Description|Scope)[:\s]+(.{0,600})", t, re.I|re.S)
            if m: scope = norm_text(m.group(2))

            rows.append(dict(
                Source_URL=base_url,
                Bid_Name=title or "Untitled",
                Bid_Number=bidnum,
                Bid_Date=due,
                Estimated_Cost="",
                Owner=owner,
                Location=city,
                Scope=scope,
                Direct_URL=page.url,
                Comments=""
            ))
            page.go_back()
            wait_full_render(page)
            human_delay()
    except Exception as e:
        return [], f"Extractor error: {e}"
    return rows, ""

def extract_generic(page, base_url):
    """Last-resort: try to collect a few likely-looking items on a page."""
    rows = []
    try:
        slow_scroll(page, 6)
        # try all links that look like bid postings
        links = page.locator("a")
        maxl = min(200, links.count())
        for i in range(maxl):
            a = links.nth(i)
            text = norm_text(a.inner_text())
            if not text:
                continue
            # Heuristics: keep links with bid-ish words
            if re.search(r"(bid|rfp|rfq|solicitation|tender|project|opportunit)", text, re.I):
                href = a.get_attribute("href") or ""
                rows.append(dict(
                    Source_URL=base_url,
                    Bid_Name=text[:200],
                    Bid_Number="",
                    Bid_Date="",
                    Estimated_Cost="",
                    Owner="",
                    Location="",
                    Scope="",
                    Direct_URL=href if href else base_url,
                    Comments="Generic capture; details may require manual drilldown"
                ))
        # De-dup by Direct_URL + Bid_Name
        dedup = {}
        for r in rows:
            k = (r["Direct_URL"], r["Bid_Name"])
            if k not in dedup:
                dedup[k] = r
        rows = list(dedup.values())
    except Exception as e:
        return [], f"Extractor error: {e}"
    return rows, ""

# ---------- Router ----------

def route_extract(page, url):
    host = re.sub(r"^https?://", "", url).split("/")[0].lower()
    if "questcdn.com" in host:
        return extract_questcdn(page, url)
    if "ionwave" in host:
        return extract_ionwave(page, url)
    return extract_generic(page, url)

# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True, help="Path to 'Bookmarks – Bid Tracking.xlsx'")
    ap.add_argument("--output", required=False, help="Output Excel filename (default auto)")
    ap.add_argument("--user-data-dir", required=True, help="Folder to persist Chromium profile/cookies")
    ap.add_argument("--date", required=False, help="Current date for filtering (YYYY-MM-DD). Defaults to today.")
    ap.add_argument("--head", action="store_true", help="Run headed to allow solving human verification")
    args = ap.parse_args()

    run_date = datetime.today()
    if args.date:
        run_date = datetime.strptime(args.date, "%Y-%m-%d")

    outname = args.output or f"Bid_Opportunities_{run_date.strftime('%Y-%m-%d')}.xlsx"

    # Read Excel: first column is URL (exact string), second column optional label
    df = pd.read_excel(args.excel, header=None)
    urls = [str(u).strip() for u in df.iloc[:,0].tolist() if isinstance(u, str) and u.strip()]
    expected_count = len(urls)

    # Data stores
    bid_rows = []
    login_required = []
    no_current = []
    requires_js = []
    human_needed = []
    run_errors = []
    processed_log = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=args.user_data_dir,
            headless=not args.head,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1366, "height": 800}
        )
        page = context.new_page()

        for idx, url in enumerate(urls, start=1):
            print(f"[{idx}/{expected_count}] {url}")
            rec = dict(URL=url, Status="Processed", Note="")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
                wait_full_render(page)
                # detect verification
                if detect_human_verification(page):
                    human_needed.append(dict(URL=url, Reason="Human verification/CAPTCHA"))
                    pause_for_verification()
                    wait_full_render(page)

                # Is this a JS site? We already loaded with JS, but detect empty pages
                body_text = norm_text(page.locator("body").inner_text()) if page.locator("body").count() else ""
                if not body_text:
                    requires_js.append(dict(URL=url, Reason="Empty body after load"))
                    rec["Status"] = "Requires JavaScript"
                    processed_log.append(rec)
                    continue

                # Route
                rows, err = route_extract(page, url)
                if err:
                    print("   extractor note:", err)

                # Filter by date; keep “No bid date listed” if we have a row with missing date
                kept = []
                for r in rows:
                    raw = r.get("Bid_Date", "")
                    dt = parse_date_maybe(raw)
                    if dt:
                        if dt.date() >= run_date.date():
                            kept.append(r)
                    else:
                        r["Comments"] = (r.get("Comments") + "; No bid date listed").strip("; ")
                        kept.append(r)

                if kept:
                    bid_rows.extend(kept)
                else:
                    no_current.append(dict(URL=url, Note="No active opportunities after date filter"))

            except PWTimeout:
                rec["Status"] = "Error"
                rec["Note"] = "Timeout"
                run_errors.append(dict(URL=url, Error="Timeout"))
            except Exception as e:
                text = str(e)
                if "login" in text.lower():
                    login_required.append(dict(URL=url, Reason="Login required"))
                    rec["Status"] = "Login Required"
                else:
                    rec["Status"] = "Error"
                    rec["Note"] = text[:200]
                    run_errors.append(dict(URL=url, Error=text))
            finally:
                processed_log.append(rec)
                human_delay()

        # Write Excel
        def to_df(rows, cols):
            if not rows:
                return pd.DataFrame(columns=cols)
            return pd.DataFrame(rows)[cols]

        bid_cols = ["Source_URL","Bid_Name","Bid_Number","Bid_Date","Estimated_Cost","Owner","Location","Scope","Direct_URL","Comments"]
        sheets = {
            "Bid Opportunities": to_df(bid_rows, bid_cols),
            "Login Required": pd.DataFrame(login_required),
            "No Current Opportunities": pd.DataFrame(no_current),
            "Requires JavaScript": pd.DataFrame(requires_js),
            "Human Verification Needed": pd.DataFrame(human_needed),
            "Run Summary": pd.DataFrame([{
                "Run Date": run_date.strftime("%Y-%m-%d"),
                "Total URLs": expected_count,
                "Processed URLs": len(processed_log),
                "Bids Collected": len(bid_rows),
                "Login Required": len(login_required),
                "No Current": len(no_current),
                "Requires JS": len(requires_js),
                "Human Verification": len(human_needed),
                "Errors": len(run_errors)
            }]),
            "Processed URLs Log": pd.DataFrame(processed_log)
        }

        with pd.ExcelWriter(outname, engine="openpyxl") as xw:
            for name, df_out in sheets.items():
                df_out.to_excel(xw, index=False, sheet_name=name)

        print(f"\n✅ Done. Wrote: {outname}")
        context.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
