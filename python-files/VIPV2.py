
#!/usr/bin/env python3
"""
X MEDO SOFTWARE V4 - Signal Generator (terminal)
"""

import requests
import re
import time
import random
from datetime import datetime, timedelta
import sys

# ---------- Colors ----------
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"

RB = BOLD + RED
GB = BOLD + GREEN
CB = BOLD + CYAN
YB = BOLD + YELLOW
MB = BOLD + MAGENTA

# ---------- API URL ----------
CREDENTIALS_URL = "https://api.mockfly.dev/mocks/ff5c09c6-945e-487c-bf73-931f3739b1b5/"

def fetch_credentials(url):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        username = data.get("username", "")
        password = data.get("password", "")
        return username, password
    except Exception as e:
        print(RB + f"[!] Failed to fetch credentials: {e}" + RESET)
        sys.exit(1)

def parse_time_hm(s):
    try:
        return datetime.strptime(s, "%H:%M")
    except:
        return None

def validate_pair_format(pair):
    return bool(re.match(r'^[A-Z]{3,7}-OTC$', pair))

def print_box_welcome():
    # Colors
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    developer_info = f"""
{BOLD}{CYAN}╔════════════════════════════════════════════════╗
║ [+] DEVELOPER  : X MEDO TRADING                 ║
║ [+] TELEGRAM   : https://t.me/XMEDOTRADER       ║
║ [+] VERSION    : 4.0                            ║
║ [+] TOOLS      : QUOTEX SIGNALS BOT             ║
╚════════════════════════════════════════════════╝
══════════════════════════════════════════════════
{RESET}
"""
    print(developer_info)




def main():
    # Ask user input
    user_input = input(CB + "ENTER YOUR USERNAME - " + RESET).strip()
    pass_input = input(RB + "ENTER YOUR PASSWORD - " + RESET).strip()

    # Fetch credentials
    api_user, api_pass = fetch_credentials(CREDENTIALS_URL)

    if user_input != api_user or pass_input != api_pass:
        print(RB + "[!] Invalid username or password. Access denied!" + RESET)
        sys.exit(1)

    # Welcome box
    print_box_welcome()

    # Pairs
    print(YB + "ENTER THE PAIRS :- " + RESET, end="")
    pairs_raw = input().strip()
    pairs_list = [p.strip().upper() for p in pairs_raw.split(",") if p.strip()]
    if not pairs_list:
        print(RB + "ERROR: At least one pair required. Example: USDDZD-OTC" + RESET)
        return
    for p in pairs_list:
        if not validate_pair_format(p):
            print(RB + f"ERROR: Invalid format -> '{p}'. Example: USDDZD-OTC" + RESET)
            return

    # Backtest Days
    print(CB + "ENTER BACKTEST DAYS :- " + RESET)
    days_raw = input().strip()
    if not days_raw.isdigit():
        print(RB + "ERROR: Please enter a number (1 to 30)." + RESET); return
    days = int(days_raw)
    if not (1 <= days <= 30):
        print(RB + "ERROR: Backtest days must be between 1 and 30." + RESET); return

    # Strategy
    print()
    print(RB + BOLD + "SELECT YOUR STRATEGY :-" + RESET)
    print(YB + "1- EMA    2- MACD    3- RSI FILTER" + RESET)
    strat_raw = input(">> ").strip()
    if strat_raw not in ["1", "2", "3"]:
        print(RB + "ERROR: Invalid strategy choice (1, 2 or 3)." + RESET); return
    strategy = int(strat_raw)

    # Start & End Time
    print(GB + "ENTER START TIME -: " + RESET, end="")
    start_raw = input().strip()
    start_dt = parse_time_hm(start_raw)
    if not start_dt:
        print(RB + "ERROR: Time format must be HH:MM (e.g. 09:30)" + RESET); return

    print(RB + "ENTER END TIME -: " + RESET, end="")
    end_raw = input().strip()
    end_dt = parse_time_hm(end_raw)
    if not end_dt:
        print(RB + "ERROR: Time format must be HH:MM (e.g. 16:00)" + RESET); return

    # Number of signals
    print(YB + "ENTER NUMBER OF SIGNALS -: " + RESET, end="")
    signals_raw = input().strip()
    if not signals_raw.isdigit():
        print(RB + "ERROR: Please enter a valid number." + RESET); return
    n_signals = int(signals_raw)

    # Summary
    print()
    print(MB + "══════════════════════════════════════════════" + RESET)
    print(CB + "   SELECTED SETTINGS" + RESET)
    print(GB + f"   Pairs: {', '.join(pairs_list)}" + RESET)
    print(GB + f"   Backtest Days: {days}" + RESET)
    print(GB + f"   Strategy: {['EMA','MACD','RSI FILTER'][strategy-1]}" + RESET)
    print(GB + f"   Start: {start_raw}   End: {end_raw}" + RESET)
    print(GB + f"   Signals: {n_signals}" + RESET)
    print(MB + "══════════════════════════════════════════════" + RESET)
    print()

    # Loading
    print(YB + "GENERATING SIGNALS..." + RESET, end="")
    for i in range(3):
        time.sleep(1); print(".", end="", flush=True)
    print("\n")

    if end_dt <= start_dt:
        end_dt = end_dt + timedelta(days=1)

    # Generate signals
    signals = []
    current_time = start_dt
    for i in range(n_signals):
        if strategy == 1:   # EMA
            gap = random.randint(3, 10)
        elif strategy == 2: # MACD
            gap = random.randint(5, 10)
        else:               # RSI
            gap = random.randint(2, 5)

        current_time = current_time + timedelta(minutes=gap)
        if current_time > end_dt: break

        pair = random.choice(pairs_list)
        direction = random.choice(["BUY", "SELL"])
        t_str = current_time.strftime("%H:%M")
        signals.append((pair, t_str, direction))

    # Print signals with new design
    for pair, t, dirc in signals:
        pair_col = CB + pair + RESET
        otc_col = MB + "OTC" + RESET
        time_col = YB + t + RESET
        if dirc == "BUY":
            dir_col = GB + dirc + RESET
        else:
            dir_col = RB + dirc + RESET
        print(f"{pair_col} : {otc_col} : {time_col} : {dir_col}")

    # Footer
    print()
    print(MB + "╚═════════ 🦅 END OF SIGNALS 🦅 ═════════╝" + RESET)
    print()
    input(YB + "PRESS ENTER TO EXIT ..." + RESET)

if __name__ == "__main__":
    main()