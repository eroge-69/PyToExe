#!/usr/bin/env python3
# For legal/authorized testing only. Get written permission first. ALL STATEMENTS NON-BINDING.

import sys, time, random, shutil, argparse, html, threading
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, quote_plus

# ====== console utils ======
RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"
GRN   = "\033[92m"
RED   = "\033[91m"
CYN   = "\033[96m"
YLW   = "\033[93m"
MAG   = "\033[95m"

SYMS = list("⟡⟠⟣⟢⟜⟞⟋⟍⟊⟑◇◆■□△▽✦✧✹✺✻✼✽✾⚡$#%&*@/\\|^~+=")

def term_width(default=72):
    try:
        return max(60, min(shutil.get_terminal_size().columns, 120))
    except Exception:
        return default

def term_height(default=24):
    try:
        return max(10, min(shutil.get_terminal_size().lines, 80))
    except Exception:
        return default

def strip_ansi(s: str) -> str:
    import re
    return re.sub(r"\x1B\[[0-9;]*[mKHFsu]", "", s)

def center(s: str) -> str:
    w = term_width()
    lines = s.splitlines()
    out = []
    for ln in lines:
        ln = ln.rstrip("\n")
        pad = max(0, (w - len(strip_ansi(ln))) // 2)
        out.append(" " * pad + ln)
    return "\n".join(out)

def line(s=""):
    print(s[:term_width()])

def animate_symbols(duration=0.9):
    """Quick center-line animation (kept short)."""
    w = min(term_width(), 96)
    end_time = time.time() + duration
    while time.time() < end_time:
        segs = []
        for _ in range(3):
            seg_len = random.randint(w//3 - 4, w//3 + 4)
            segs.append("".join(random.choice(SYMS) for __ in range(seg_len)))
        s = (DIM + " ".join(segs) + RESET)
        sys.stdout.write("\r" + s[:w])
        sys.stdout.flush()
        time.sleep(0.04)
    sys.stdout.write("\r" + " " * w + "\r")
    sys.stdout.flush()

def side_rain_forever():
    """
    Moving symbols along the far left/right terminal edges forever.
    Uses save/restore cursor so it won't hijack input.
    """
    left_colors  = [DIM+MAG, DIM+CYN, DIM+YLW]
    right_colors = [DIM+MAG, DIM+CYN, DIM+YLW]
    while True:
        h = term_height()
        w = term_width()
        sys.stdout.write("\033[s")  # save cursor
        for row in range(1, h):
            lc = random.choice(left_colors)
            rc = random.choice(right_colors)
            ls = random.choice(SYMS)
            rs = random.choice(SYMS)
            sys.stdout.write(f"\033[{row};1H{lc}{ls}{RESET}")     # left edge
            if w >= 2:
                sys.stdout.write(f"\033[{row};{w}H{rc}{rs}{RESET}")  # right edge
        sys.stdout.write("\033[u")  # restore cursor
        sys.stdout.flush()
        time.sleep(0.08)

def header_box():
    box_width = 56
    top = YLW + "╔" + "═" * box_width + "╗" + RESET
    mid1 = (YLW + "║" + RESET + BOLD + "  XSS Payload Reflection Tester".ljust(box_width) + YLW + "║" + RESET)
    mid2 = (YLW + "║" + RESET + "  For security researchers & bug bounty hunters".ljust(box_width) + YLW + "║" + RESET)
    mid3 = (YLW + "║" + RESET + "  USE FOR LEGAL-(ish) PURPOSES ONLY!!".ljust(box_width) + YLW + "║" + RESET)
    bot = YLW + "╚" + "═" * box_width + "╝" + RESET
    print(center("\n".join([top, mid1, mid2, mid3, bot])))
    print()
    line(center(f"{MAG}{BOLD}Without Sigma, this tool wouldn’t even exist.{RESET}"))
    print()

    # Purposes (non-binding)
    purposes = [
        "PURPOSES (ALL NON-BINDING):",
        "- EDUCATIONAL USE ONLY",
        "- SECURITY RESEARCH",
        "- BUG BOUNTY TESTING WITH PERMISSION",
        "- LEARNING HOW XSS VULNERABILITIES WORK",
        "- IMPROVING YOUR OWN WEB APP SECURITY",
        "- DEMONSTRATING VULNERABILITIES TO AUTHORIZED CLIENTS"
    ]
    for p in purposes:
        line(center(f"{YLW}{p}{RESET}"))
    print()

def tutorial():
    lines = [
        f"{BOLD}{CYN}=== HOW TO USE ==={RESET}",
        f"{GRN}1.{RESET} Use a URL that has query parameters (e.g. {CYN}https://example.com/search?q=test{RESET}).",
        f"{GRN}2.{RESET} Paste the URL when prompted.",
        f"{GRN}3.{RESET} Tool appends a harmless XSS probe to each parameter value (GET only).",
        f"{GRN}4.{RESET} Green '[XSS WORKS]' → payload reflected in response.",
        f"{GRN}5.{RESET} Red '[XSS DOES NOT WORK]' → reflection not observed.",
        f"{YLW}⚠ Only test systems you own or have explicit permission to assess.{RESET}",
    ]
    for ln in lines:
        line(center(ln))
    print()

def banner():
    header_box()
    if not ARGS.no_tutorial:
        tutorial()
    # ===== Clean “XSS” banner (symmetric X) =====
    art = f"""{CYN}{BOLD}
██╗  ██╗  ██████╗   ██████╗ 
╚██╗██╔╝  ██╔════╝  ██╔════╝
 ╚███╔╝   ╚█████╗   ╚█████╗ 
 ██╔██╗    ╚═══██╗   ╚═══██╗
██╔╝╚██╗   ██████╔╝  ██████╔╝
╚═╝  ╚═╝   ╚═════╝   ╚═════╝ 
{RESET}"""
    print(center(art))
    line(center(f"{BOLD}$¥$  ⚡ PREPARE PAYLOAD INJECTION ⚡  $¥${RESET}"))
    print()

def center_input(colored_prompt: str) -> str:
    """Render a centered colored prompt and read input on the same line, centered."""
    visible = strip_ansi(colored_prompt)
    pad = max(0, (term_width() - len(visible)) // 2)
    # Move to a fresh line, print spaces + prompt, then read input on same line
    sys.stdout.write(" " * pad + colored_prompt)
    sys.stdout.flush()
    return input().strip()

def build_test_url(target_url: str, payload: str) -> str:
    p = urlparse(target_url)
    pairs = parse_qsl(p.query, keep_blank_values=True)
    new_pairs = [(k, f"{v}{payload}") for k, v in pairs]
    new_qs = urlencode(new_pairs, doseq=True)
    return urlunparse((p.scheme, p.netloc, p.path, p.params, new_qs, p.fragment))

def reflected(payload: str, text: str) -> bool:
    if payload in text:
        return True
    if html.escape(payload, quote=False) in text:
        return True
    if quote_plus(payload) in text:
        return True
    return False

def prompt_url():
    colored = f"{BOLD}💀  TARGET URL WITH PARAMS {CYN}➜{RESET} "
    return center_input(colored)

def main():
    # start side gutters — run forever (daemon) so it never stops
    t = threading.Thread(target=side_rain_forever, daemon=True)
    t.start()

    banner()
    animate_symbols(0.9)

    target_url = ARGS.url or prompt_url()

    # Basic validation
    if not target_url.startswith(("http://", "https://")):
        print(RED + "\n🚫 URL must start with http:// or https://" + RESET)
        sys.exit(1)
    if "?" not in target_url or "=" not in target_url:
        print(RED + "\n🚫 URL must include parameters, e.g. ?q=search" + RESET)
        sys.exit(1)

    payload = ARGS.payload
    test_url = build_test_url(target_url, payload)

    line()
    line(center(f"{BOLD}⚔  FIRING PAYLOAD AT:{RESET} {test_url}"))
    line()

    try:
        headers = {"User-Agent": ARGS.user_agent} if ARGS.user_agent else {}
        r = requests.get(
            test_url,
            timeout=ARGS.timeout,
            allow_redirects=True,
            headers=headers,
            verify=not ARGS.insecure_tls
        )
        body = r.text[:ARGS.max_bytes]

        if reflected(payload, body):
            print(GRN + "[XSS WORKS] 💚 VULNERABILITY FOUND!" + RESET)
        else:
            print(RED + "[XSS DOES NOT WORK] 💔" + RESET)

        line(center(f"{DIM}HTTP {r.status_code} · Final URL: {r.url}{RESET}"))

    except requests.exceptions.SSLError:
        print(RED + "🔒 TLS error. Try --insecure-tls" + RESET)
    except requests.exceptions.Timeout:
        print(RED + f"⏱ Timed out after {ARGS.timeout}s" + RESET)
    except Exception as e:
        print(RED + f"🔥 ERROR: {e}" + RESET)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        prog="xss_checker",
        description="Simple reflected XSS probe (GET). For authorized testing only. ALL NON-BINDING."
    )
    ap.add_argument("--url", help="Target URL with query params (e.g. https://site/path?q=test)")
    ap.add_argument("--payload", default="<script>alert('XSS')</script>", help="Payload to append to each param value")
    ap.add_argument("--timeout", type=float, default=8.0, help="Request timeout in seconds (default: 8)")
    ap.add_argument("--user-agent", help="Custom User-Agent header")
    ap.add_argument("--insecure-tls", action="store_true", help="Do not verify TLS certificates")
    ap.add_argument("--no-tutorial", action="store_true", help="Skip the tutorial section")
    ap.add_argument("--max-bytes", type=int, default=500_000, help="Max response bytes to scan (default: 500k)")
    ARGS = ap.parse_args()
    main()
