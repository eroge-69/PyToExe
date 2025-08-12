#!/usr/bin/env python3
# For legal/authorized testing only. Get written permission first. ALL STATEMENTS NON-BINDING.

import sys, time, random, shutil, argparse, socket, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== Colors & UI =====
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
        return max(60, min(shutil.get_terminal_size().columns, 140))
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
    out = []
    for ln in s.splitlines():
        pad = max(0, (w - len(strip_ansi(ln))) // 2)
        out.append(" " * pad + ln)
    return "\n".join(out)

def line(s=""):
    print(s[:term_width()])

def side_rain_forever():
    """Moving symbols along far left/right edges forever (daemon)."""
    left_colors  = [DIM+MAG, DIM+CYN, DIM+YLW]
    right_colors = [DIM+MAG, DIM+CYN, DIM+YLW]
    while True:
        h = term_height()
        w = term_width()
        sys.stdout.write("\033[s")
        for row in range(1, h):
            lc = random.choice(left_colors)
            rc = random.choice(right_colors)
            ls = random.choice(SYMS)
            rs = random.choice(SYMS)
            sys.stdout.write(f"\033[{row};1H{lc}{ls}{RESET}")
            if w >= 2:
                sys.stdout.write(f"\033[{row};{w}H{rc}{rs}{RESET}")
        sys.stdout.write("\033[u")
        sys.stdout.flush()
        time.sleep(0.08)

def header_box():
    boxw = 60
    top = YLW + "╔" + "═" * boxw + "╗" + RESET
    mid1 = (YLW + "║" + RESET + BOLD + "  PORTAL PRO — TARGET PORT SCANNER".ljust(boxw) + YLW + "║" + RESET)
    mid2 = (YLW + "║" + RESET + "  For admins, researchers & lab testing".ljust(boxw) + YLW + "║" + RESET)
    mid3 = (YLW + "║" + RESET + "  USE ONLY WITH EXPLICIT PERMISSION".ljust(boxw) + YLW + "║" + RESET)
    bot = YLW + "╚" + "═" * boxw + "╝" + RESET
    print(center("\n".join([top, mid1, mid2, mid3, bot])))
    print()
    line(center(f"{MAG}{BOLD}Without Sigma, this tool wouldn’t even exist.{RESET}"))
    print()

def banner():
    header_box()
    art = f"""{CYN}{BOLD}
██████╗  ██████╗ ██████╗ ████████╗ █████╗ ██╗     
██╔══██╗██╔════╝ ██╔══██╗╚══██╔══╝██╔══██╗██║     
██████╔╝██║  ███╗██████╔╝   ██║   ███████║██║     
██╔══██╗██║   ██║██╔══██╗   ██║   ██╔══██║██║     
██║  ██║╚██████╔╝██║  ██║   ██║   ██║  ██║███████╗
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝
                        PRO
{RESET}"""
    print(center(art))
    line(center(f"{BOLD}$¥$  ⚡ INITIALIZING SOCKETS ⚡  $¥${RESET}"))
    print()

def center_input(prompt: str) -> str:
    visible = strip_ansi(prompt)
    pad = max(0, (term_width() - len(visible)) // 2)
    sys.stdout.write(" " * pad + prompt)
    sys.stdout.flush
    return input().strip()

# ===== Cute IP prompt lines (with rarity buckets) =====
NORMAL_LINES = [
    "nice ip twin",
    "wow another ip, i’m tired",
    "hand over the digits",
    "feed me numbers",
    "gimme that spicy ipv4",
    "bet it’s 192.168.something",
    "lemme sniff that ip real quick",
    "what’s the addy champ",
    "drop the target, soldier",
    "ip me up, buttercup",
    "another one… throw it in",
    "target acquired? not yet—type it",
    "is it alive? we’ll find out",
    "put the IP here, trust",
    "paste the host like you mean it",
    "servin’ sockets since forever",
    "enter. the. ip.",
    "bring me that juicy endpoint",
    "time to ring some ports",
    "deliver the coordinates",
    "knock knock—who’s port?",
    "open the gates (type ip)",
    "runtime snacks = IP address",
    "whisper the IP gently",
    "slap the IP, let’s go",
    "make it public (or local, idc)",
    "present the victim—uh, target",
    "paint me an ipv4",
    "host, please and thank you",
    "coords to the castle, knight",
    "I hunger for octets",
    "ip goes here ↓ (obviously)",
    "serve the hostname on ice",
    "another day, another scan",
    "don’t be shy, type it",
]

CHAOS_LINES = [
    "SYSTEM REQUIRES MORE COOKIES",
    "PLEASE SEND BACON",
    "ENGAGE LASERS… PEW PEW",
    "FBI—JUST KIDDING—TYPE THE IP",
    "IMMA BLAST THIS SCAN!!",
    "AHHHHHHHHHHHHHHHHHHHHHHH AH AH AH AH DONT UNPLUG ME AHHHHHH AHHH THEYRE BEHIND YOU BEHIND YOU!!!!!!!!!! TURN AROUND NOW!!!!! AHHHHHHHHHHHHHHHHHH",
]

RARE_SUS_LINES = [
    "the packets yearn for the address",
    "deep breaths… now type the target",
    "i can feel the sockets tingling",
    "the firewall can’t stop destiny",
    "portals opening—drop coordinates",
    "you digging in meeeee",
    "do you want pain?? do you want pain??? *slap* do you want pain?? *slap* do you want pain??? *slap* do you want pain?? *slap* do you want pain??? *slap* do you want fucking pain????! *slap*",
]

def random_prompt_line() -> str:
    r = random.random()
    if r < 0.85:
        return random.choice(NORMAL_LINES)
    elif r < 0.95:
        return random.choice(CHAOS_LINES)
    else:
        return random.choice(RARE_SUS_LINES)

# ===== Port logic =====
def parse_ports(spec: str):
    """Parse '22,80,443,8000-8100' -> sorted unique list of ints."""
    ports = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a = int(a); b = int(b)
            if a > b: a, b = b, a
            for p in range(max(1, a), min(65535, b) + 1):
                ports.add(p)
        else:
            p = int(part)
            if 1 <= p <= 65535:
                ports.add(p)
    return sorted(ports)

def top_1024():
    """Use 1..1024 as the 'top ~1000' commonly-served ports."""
    return list(range(1, 1025))

def scan_port(host, port, timeout):
    """Return True if TCP connect succeeds, else False."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False

def service_name(port):
    try:
        return socket.getservbyport(port)
    except Exception:
        return None

def scan_ports(host, ports, threads, timeout):
    open_ports = []
    with ThreadPoolExecutor(max_workers=threads) as exe:
        futs = {exe.submit(scan_port, host, p, timeout): p for p in ports}
        done = 0
        total = len(ports)
        for fut in as_completed(futs):
            p = futs[fut]
            ok = fut.result()
            done += 1
            if done % max(1, total // 20) == 0:
                sys.stdout.write(f"\r{DIM}scanned {done}/{total}...{RESET}")
                sys.stdout.flush()
            if ok:
                open_ports.append(p)
    sys.stdout.write("\r" + " " * 40 + "\r")
    return sorted(open_ports)

def print_results(open_ports):
    if not open_ports:
        line(center(RED + "No open ports found." + RESET))
        return
    line(center(GRN + f"Open ports ({len(open_ports)}):" + RESET))
    for p in open_ports:
        svc = service_name(p)
        label = f"{p}/tcp" + (f" ({svc})" if svc else "")
        line(center(GRN + "• " + label + RESET))

def ask_target():
    tagline = random_prompt_line()
    line(center(DIM + f"{tagline}" + RESET))
    return center_input(f"{BOLD}🎯  TARGET IP / HOSTNAME ➜ {RESET}")

def ask_ports():
    spec = center_input(f"{BOLD}🔢  PORTS (e.g. 22,80,443,8000-8100) ➜ {RESET}")
    try:
        ports = parse_ports(spec)
        if ports:
            return ports
    except Exception:
        pass
    line(center(RED + "Couldn’t parse ports. Try again." + RESET))
    return ask_ports()

def menu():
    line(center(f"{BOLD}{CYN}=== MENU ==={RESET}"))
    line(center(f"{GRN}[1]{RESET} Scan ALL ports (1–65535)"))
    line(center(f"{GRN}[2]{RESET} Scan TOP 1024 ports (1–1024)"))
    line(center(f"{GRN}[3]{RESET} Scan SPECIFIC list/ranges"))
    line(center(f"{GRN}[4]{RESET} Quit"))
    line(center(f"{DIM}[5] secret{RESET}"))
    return center_input(f"{BOLD}➜{RESET} ").strip().lower()

def secret_gag_then_exit():
    msg = "*fart* oops *fart* oops"
    line(center(msg))
    sys.exit(0)

def main_loop(threads, timeout):
    while True:
        choice = menu()
        if choice == "5" or choice == "secret":
            secret_gag_then_exit()
        elif choice == "4":
            line(center(MAG + "Exiting PORTAL PRO..." + RESET))
            break
        elif choice not in ("1", "2", "3"):
            line(center(RED + "Invalid choice. Enter 1, 2, 3, 4, or 5." + RESET))
            continue

        target = ask_target()
        if choice == "1":
            ports = list(range(1, 65536))
        elif choice == "2":
            ports = top_1024()
        else:
            ports = ask_ports()

        line()
        line(center(f"{BOLD}⚔  SCANNING {target} — {len(ports)} ports  ⚔{RESET}"))
        line()

        # Resolve early to catch DNS issues fast
        try:
            socket.getaddrinfo(target, None)
        except Exception as e:
            line(center(RED + f"DNS/Resolution error: {e}" + RESET))
            continue

        t0 = time.time()
        open_ports = scan_ports(target, ports, threads=threads, timeout=timeout)
        dt = time.time() - t0

        line()
        print_results(open_ports)
        line(center(DIM + f"Done in {dt:.2f}s with {threads} threads, timeout={timeout:.1f}s" + RESET))
        line()

def main():
    threading.Thread(target=side_rain_forever, daemon=True).start()
    banner()
    main_loop(threads=ARGS.threads, timeout=ARGS.timeout)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        prog="portal_pro",
        description="Threaded TCP port scanner. Authorized testing only. ALL NON-BINDING."
    )
    ap.add_argument("--threads", type=int, default=200, help="Number of worker threads (default: 200)")
    ap.add_argument("--timeout", type=float, default=0.7, help="Socket timeout seconds (default: 0.7)")
    ARGS = ap.parse_args()
    main()
