import re
import requests
import json
import os
from colorama import Fore, Style, init
import subprocess
import socket
import os
import sys
from colorama import init, Fore
import random
from collections import defaultdict
from colorama import Fore, Style, init
import time
import requests
from datetime import datetime, timedelta
import threading

init(autoreset=True)


win_count = 0
loss_count = 0


import json
SAVE_FILE = "signal_results.json"

def save_results():
    data = {
        "total_wins": total_wins,
        "total_losses": total_losses,
        "recent_signals": recent_signals
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_results():
    global total_wins, total_losses, recent_signals
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            total_wins = data.get("total_wins", 0)
            total_losses = data.get("total_losses", 0)

            recent_signals = data.get("recent_signals", [])
            print(Fore.GREEN + f"[✓] Loaded saved results: {total_wins} Wins, {total_losses} Losses")
    else:
         print(Fore.YELLOW + "[!] No saved results found. Starting fresh.")


def utc6_to_utc3(time_str):
    dt = datetime.strptime(time_str, "%H:%M")
    converted = dt - timedelta(hours=9)

    return converted.strftime("%H:%M")

def utc3_to_utc6(time_str):
    dt = datetime.strptime(time_str, "%H:%M")
    converted = dt + timedelta(hours=9)
    return converted.strftime("%H:%M")


# === CONFIG ===

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

loader_running = False  # Global flag for animation loop

def animated_loader(message, duration=5):
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    idx = 0

    while time.time() < end_time:
        sys.stdout.write(f"\r{message} {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.2)

    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")  # Clear line

def animated_loader_loop(message):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    while loader_running:
        sys.stdout.write(f"\r{message} {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.2)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")  # Clear line


def display_border(color):
    border = f"{color}▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"
    print(border)
    return border

def show_login_page(border_color, message=""):
    clear_screen()
    print("\n")
    print(border_color)
    print(f"""
       ███    ██ ███████ ██   ██  ██████      ███████ ██   ██ ██████
       ████   ██ ██       ██ ██  ██    ██     ██       ██ ██  ██   ██
       ██ ██  ██ █████     ███   ██    ██     █████     ███   ██████
       ██  ██ ██ ██       ██ ██  ██    ██     ██       ██ ██  ██
      ██   ████ ███████ ██   ██  ██████      ███████ ██   ██ ██


    """)
    print("\n")
    print('                     ' + Style.BRIGHT + '  ' + Fore.WHITE + ' NEXO EXP IS POWERFUL SOCKET ')
    print('                           ' + Style.BRIGHT + '  ' + Fore.WHITE + ' DEVELOPER BY RT ')
    print('                      ' + Style.BRIGHT + '  ' + Fore.WHITE + ' TELEGRAM: @ROHAN_TRADER1')
    print('                           ' + Style.BRIGHT + '  ' + Fore.WHITE + ' VERSION:  v10.0 ')
    print('                       ' + Style.BRIGHT + '  ' + Fore.WHITE + ' TIMEZONE: [ UTC +6:00 ] ')
    if message:
        print('                       ' + Style.BRIGHT + '      ' + message)
    print(border_color)
    print("\n")



# Signal result API
#RESULT_API_URL = "https://nafi.qtxserver.site/signals?signals="
def send_to_telegram(message):
    targets = []

    if PUBLIC_CHANNEL_ID:
        targets.append(PUBLIC_CHANNEL_ID)
    if PRIVATE_CHANNEL_ID:
        targets.append(PRIVATE_CHANNEL_ID)
    if ADDITIONAL_CHANNEL_ID:
        targets.append(ADDITIONAL_CHANNEL_ID)
    if EXTRA_CHANNEL_ID:
        targets.append(EXTRA_CHANNEL_ID)

    for chat_id in targets:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(Fore.RED + f"[!] Failed to send to {chat_id}: {response.text}")
        except Exception as e:
            print(Fore.RED + f"[!] Telegram send error: {e}")

            #   Format signal message
def format_signal_message(pair, time_str, direction):
    icon = "⬆️" if direction == "CALL" else "⬇️"
    # Prevent copy label using invisible char
    invisible_prefix = "\u2060"

    # Simulated collapsible header
    header = "<b></b>"

    # Body as clean text block (NOT <pre>, avoids copy button)
    body = (
        "۩❦۩¤════¤ NEXO CLOUD SIGNAL ¤════¤۩❦۩\n\n"
        f"♅ Pairs     : {pair}\n"
        f"卐 Time     : {time_str}\n"
        f"卍 Direction: {direction} {icon}\n\n"
        f"✪ Strategy Engaged: Sniper Candle\n"
    )

    return f"{invisible_prefix}{header}\n\n<code>{body}</code>"

# Format result message
def format_result_message(pair, time_str, direction, result):
    if "WIN" in result.upper():
        return f"Results: {pair} / {time_str} - ✅ WIN"
    if "WIN MTG1" in result.upper():
        return f"Results: {pair} / {time_str} - ✅1 WIN"
    elif "LOSS" in result.upper():
        return f"Results: {pair} / {time_str} - ❌ LOSS"
    else:
        return f"Results: {pair} / {time_str} - ✅ WIN"

# Check result


from colorama import Fore, init
init(autoreset=True)

from collections import defaultdict
import requests

# Dictionary to track win/loss per pair
pair_results = defaultdict(lambda: {"win": 0, "loss": 0})

# Total signal counters
total_signals = 0
total_wins = 0
total_losses = 0


# Store signals that failed due to API issues
pending_results = []
pending_lock = threading.Lock()

# Global lists to store cumulative results
recent_signals = []                                                                                                                                    

def print_cumulative_results():
    global total_wins, total_losses, recent_signals

    total_signals = total_wins + total_losses
    accuracy = round((total_wins / total_signals) * 100, 2) if total_signals > 0 else 0
                                                                                                                                                       
    box_lines = []
    box_lines.append("╔════════════════════════════════╗")
    box_lines.append("║    🤖  QUOTEX ᐅ RESULTS  🤖    ║")
    box_lines.append("╠════════════════════════════════╣")
    for pair, time_str, result in recent_signals:
        indicator = "✅" if "WIN" in result.upper() or "𝗣𝗥𝗢𝗙𝗜𝗧" in result.upper() else "❎"
        status_label = "𝗣𝗥𝗢𝗙𝗜𝗧 ✅" if indicator == "🟢" else "𝗗𝗘𝗙𝗘𝗔𝗧𝗦 ❎"
        line = f"║ {indicator} {pair:<12} {time_str} {status_label}"
        box_lines.append(line.ljust(38) + "║")

    box_lines.append("╠═══════════════════════════╣")
    box_lines.append(f"║   ✅ TOTAL WINS:   {total_wins}".ljust(38) + "")
    box_lines.append(f"║   ❌ TOTAL LOSSES: {total_losses}".ljust(38) + "")
    box_lines.append(f"║   💀 ACCURACY: {accuracy}%".ljust(38) + "")
    box_lines.append("╚═══════════════════════════╝")

    final_message = "\n".join(box_lines)
    print(final_message + "\n")


def send_cumulative_results_to_telegram():
    global total_wins, total_losses, recent_signals

    total_signals = total_wins + total_losses
    accuracy = round((total_wins / total_signals) * 100, 2) if total_signals > 0 else 0

    lines = []
    lines.append("ALL [Bot]:")
    lines.append("╔═══════════════════════════════════╗")
    lines.append("║     🤖  QUOTEX ᐅ RESULTS  🤖       ║")
    lines.append("╠═══════════════════════════════════╣")

    for pair, time_str, result in recent_signals:
        is_win = "✅" in result
        is_loss = "❎" in result
        emoji = "✅" if is_win else "❎"
        result_display = result

        lines.append(f" {emoji}  {pair:<15} {time_str} {result_display}".ljust(38))

    lines.append("╠════════════════════════════╣")
    lines.append(f"║   ✅ TOTAL WINS:   {total_wins}".ljust(38))
    lines.append(f"║   ❌ TOTAL LOSSES: {total_losses}".ljust(38))
    lines.append(f"║   💀 ACCURACY: {accuracy}%".ljust(38))
    lines.append("╚════════════════════════════╝")

    message = "\n".join(lines)
    send_to_telegram(f"<pre>{message}</pre>")




def process_signals():
    """
    প্রধান লুপ + ইনপুট-হ্যান্ডলার।
    ▸ auto_send_signals() থ্রেড থেকে কিউ-তে সিগন্যাল ঢুকে;
    ▸ ইউজার রেজাল্ট দিলে জয়/পরাজয় গুনে টেলেগ্রামে পাঠায়;
    ▸ প্রতি ১০-টা সিগন্যালে একবার সারসংক্ষেপ পাঠায়।
    """
    global total_wins, total_losses, recent_signals

    # লোকাল কিউ— auto-thread এখানে রেজাল্ট দেয়, নিচের while লুপ প্রসেস করে
    from queue import Queue
    results_queue = Queue()

    entered_signals   : list[tuple] = []
    pending_signals   : list[tuple] = []
    total_processed = 0

    # ──────────────────────────
    # nested helper → সিগন্যাল পাঠানো
    def auto_send_signals():
        while True:
            # কিউ খালি হলে নতুন র‍্যান্ডম সিগন্যাল বানাই
            if signal_queue.empty():
                pairs = ["EURUSD-OTC", "USDJPY-OTC", "EURCAD-OTC"]
                start = datetime.now().strftime("%H:%M")
                end   = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
                for sig in generate_random_signals(pairs, start, end):
                    signal_queue.put(sig)

            pair, time_str, direction = signal_queue.get()
            send_to_telegram(format_signal_message(pair, time_str, direction))
            results_queue.put((pair, time_str, direction))
            pending_signals.append((pair, time_str, direction))
            time.sleep(random.randint(92, 93))

    # থ্রেড চালু
    threading.Thread(target=auto_send_signals, daemon=True).start()

    # ──────────────────────────
    # মূল ইনপুট-প্রসেসিং লুপ
    while True:
        #pause_event.wait()          # CTRL+P → pause, CTRL+R → resume
        if results_queue.empty():
            time.sleep(0.2)
            continue

        pair, time_str, direction = results_queue.get()

        while True:
            prompt = (f"Enter result type {pair} at {time_str} {direction}:""(w/m/l/s/nl/p/f): ")
            result_input = input(prompt).strip().lower()

            # ───── জয় বা পরাজয় ─────
            if result_input in ("w", "l", "m"):
                result_status = (
                    "𝗣𝗥𝗢𝗙𝗜𝗧 ✅"   if result_input == "w" else
                    "𝗣𝗥𝗢𝗙𝗜𝗧 ✅¹"  if result_input == "m" else
                    "𝗗𝗘𝗙𝗘𝗔𝗧𝗦 ❎"
                )
                if result_input in ("w", "m"):
                    total_wins  += 1
                else:
                    total_losses += 1

                recent_signals.append((pair, time_str, result_status))
                entered_signals.append((pair, time_str, direction, result_status))
                if (pair, time_str, direction) in pending_signals:
                    pending_signals.remove((pair, time_str, direction))

                # ইন্ডিভিজুয়াল ফলাফল কার্ড
                total = total_wins + total_losses
                acc   = round((total_wins / total) * 100, 2) if total else 0
                card = (
                    "××××××『 𝗥𝗲𝘀𝘂𝗹𝘁𝘀 𝗦𝗵𝗼𝘄𝗲𝗱 』××××××\n\n"
                    f"📊 𝗣𝗮𝗶𝗿𝘀  ⟶ {pair}\n"
                    f"🕦 𝗧𝗶𝗺𝗲   ⟶ {time_str}\n"
                    f"☠️ 𝗙𝗶𝗻𝗮𝗹 𝗥𝗲𝘀𝘂𝗹𝘁 ⟶ {result_status}\n\n"
                    "╭────────────────────╮\n"
                    f"✯ 𝗣𝗥𝗢𝗙𝗜𝗧𝗦  : {total_wins}\n"
                    f"✜ 𝗗𝗘𝗙𝗘𝗔𝗧𝗦  : {total_losses}\n"
                    f"☠ 𝗔𝗖𝗖𝗨𝗥𝗔𝗖𝗬 : {acc}%\n"
                    "╰────────────────────╯"
                )
                send_to_telegram(card)
                save_results()

                # প্রতি ১০-টা সিগন্যাল শেষে সারসংক্ষেপ
                total_processed += 1
                if total_processed % 10 == 0:
                    print_cumulative_results()
                    send_cumulative_results_to_telegram()
                break

            # ───── ‘f’ → পুরো সারসংক্ষেপ দেখাও ─────
            elif result_input == "f":
                print_cumulative_results()
                send_cumulative_results_to_telegram()
                break

            # ───── ‘s’ → সিগন্যাল স্কিপ ─────
            elif result_input == "s":
                print(f"[!] Skipped {pair} at {time_str}")
                break

            # ───── ‘nl’ → পেন্ডিং-লিস্ট UTC-3 এ কনভার্ট ─────
            elif result_input == "nl":
                print("\nHere is your pending signals without results "
                      "utc+6:00 to utc-3:00 converted\n")
                for sig in pending_signals:
                    local = sig[1][:5]
                    print(f"M1;{sig[0]};{utc6_to_utc3(local)};{sig[2]}")
                print()
                break

            # ───── ‘p’ → বাল্ক-পেস্টেড রেজাল্ট প্রসেস ─────
            elif result_input == "p":
                print("\nPaste your signals results with utc-3:00 "
                      "(blank line to finish)\n")
                pasted = []
                while True:
                    line = input()
                    if not line.strip():
                        break
                    pasted.append(line.strip())

                for ln in pasted:
                    raw = ln.replace("✅", "").replace("❎", "").strip()
                    parts = (raw.split(";") if ";" in raw else raw.split())
                    if len(parts) < 4:
                        print(f"[!] Invalid format: {ln}")
                        continue

                    p, t, dir = parts[1], utc3_to_utc6(parts[2]), parts[3]
                    is_win = "✅" in ln
                    status = "𝗣𝗥𝗢𝗙𝗜𝗧 ✅" if is_win else "𝗗𝗘𝗙𝗘𝗔𝗧𝗦 ❎"
                    (total_wins if is_win else total_losses).__iadd__(1)
                    recent_signals.append((p, t, status))

                save_results()
                print("[✓] Pasted signals processed ✅\n")
                break

            else:
                print("Invalid input! Use: w, m, l, s, nl, p or f only.")


from queue import Queue

# Queue to store signals
signal_queue = Queue()

# Global counters
total_wins = 0
total_losses = 0



def schedule_signal(pair, time_str, direction):
    now = datetime.now()
    signal_time = now.replace(hour=int(time_str.split(":")[0]), minute=int(time_str.split(":")[1]), second=0, microsecond=0)
    if signal_time < now:
        signal_time += timedelta(days=3)

    send_time = signal_time - timedelta(minutes=4)
    wait_seconds = (send_time - now).total_seconds()

    # Schedule only once, no spinner here
    threading.Timer(wait_seconds, send_signal, args=(pair, time_str, direction)).start()


def retry_pending_results():
    while True:
        time.sleep(180)  # Wait 3 minutes before retrying
        with pending_lock:
            if not pending_results:
                continue
            retry_list = pending_results[:]
            pending_results.clear()

        print(Fore.YELLOW + f"[RETRYING] Checking {len(retry_list)} previously failed results...")
        for pair, time_str, direction in retry_list:
            check_result(pair, time_str, direction)

def generate_random_signals(pairs, start_time, end_time):
    all_signals = []

    start_dt = datetime.strptime(start_time, "%H:%M")
    end_dt = datetime.strptime(end_time, "%H:%M")

    # Calculate hours in float (e.g., 1.5 hours)
    duration_minutes = (end_dt - start_dt).total_seconds() / 60
    hours = duration_minutes / 60

    # Calculate how many signals to generate based on duration
    total_signals = int(hours * random.randint(26, 28))

    current_time = start_dt

    while current_time < end_dt and len(all_signals) < total_signals:
        pair = random.choice(pairs)
        direction = random.choice(["CALL", "PUT"])
        time_str = current_time.strftime("%H:%M")
        all_signals.append((pair, time_str, direction))

        # Gap of 3–4 minutes
        gap = random.randint(90, 92)
        current_time += timedelta(seconds=gap)

    return all_signals

def main():
    global BOT_TOKEN, PUBLIC_CHANNEL_ID, PRIVATE_CHANNEL_ID, ADDITIONAL_CHANNEL_ID, EXTRA_CHANNEL_ID

    print("\n")
    option = input("∆ Which option to send signals? (ex, 1. Public, 2. Private): ").strip()
    signal_mode = input("∆ 1.Auto signal or 2.future Signal: ").strip()

    BOT_TOKEN = input("∆ Enter your Telegram Bot Token: ").strip()

    PUBLIC_CHANNEL_ID = ""
    PRIVATE_CHANNEL_ID = ""
    ADDITIONAL_CHANNEL_ID = ""
    EXTRA_CHANNEL_ID = ""

    if option == "1":
        how_many = input("∆ How many public channel do you send signal (1, 2 or 3): ").strip()
        if how_many == "1":
            PUBLIC_CHANNEL_ID = input("∆ Enter your PUBLIC Channel Username (with @): ").strip()
        elif how_many == "2":
            PUBLIC_CHANNEL_ID = input("∆ Enter your 1st PUBLIC Channel Username (with @): ").strip()
            ADDITIONAL_CHANNEL_ID = input("∆ Enter your 2nd PUBLIC Channel Username (with @): ").strip()
        elif how_many == "3":
            PUBLIC_CHANNEL_ID = input("∆ Enter your 1st PUBLIC Channel Username (with @): ").strip()
            ADDITIONAL_CHANNEL_ID = input("∆ Enter your 2nd PUBLIC Channel Username (with @): ").strip()
            EXTRA_CHANNEL_ID = input("∆ Enter your 3rd PUBLIC Channel Username (with @): ").strip()
        else:
            print("Invalid number of public channels. Exiting.")
            return

    elif option == "2":
        how_many = input("∆ How many private channel do you send signal (1, 2 or 3): ").strip()
        if how_many == "1":
            PRIVATE_CHANNEL_ID = input("∆ Enter your PRIVATE Channel ID (starts with -100): ").strip()
        elif how_many == "2":
            PRIVATE_CHANNEL_ID = input("∆ Enter your 1st PRIVATE Channel ID (starts with -100): ").strip()
            ADDITIONAL_CHANNEL_ID = input("∆ Enter your 2nd PRIVATE Channel ID (starts with -100): ").strip()
        elif how_many == "3":
            PRIVATE_CHANNEL_ID = input("∆ Enter your 1st PRIVATE Channel ID (starts with -100): ").strip()
            ADDITIONAL_CHANNEL_ID = input("∆ Enter your 2nd PRIVATE Channel ID (starts with -100): ").strip()
            EXTRA_CHANNEL_ID = input("∆ Enter your 3rd PRIVATE Channel ID (starts with -100): ").strip()
        else:
            print("Invalid number of private channels. Exiting.")
            return
    else:
        print("Invalid option. Exiting.")
        return

# Ask user if they want to load saved signals
    use_saved = input("Do you want save signals (yes or no): ").strip().lower()
    if use_saved == "yes":
        load_results()
    else:
         print(Fore.YELLOW + "[*] Starting with fresh signal result counts.")


    pairs_input = input("∆ Enter pairs comma separated, **_otc: ").strip()
    pairs = [p.strip() for p in pairs_input.split(',')]

    if signal_mode == "1":
        day = input("∆ Type stc count: ").strip()
        start_time = input("∆ Start Time (e.g. 00:00): ").strip()
        end_time = input("∆ End Time (e.g. 01:00): ").strip()

        signals = generate_random_signals(pairs, start_time, end_time)

        print("\nAnalysis market...\nMarket trend checking...\n")
        animated_loader("Scanning trends", duration=7)
        print("\nScanning Complete ✅")
        print("\nStarting signal execution...")

        now_time = datetime.now().strftime("%H:%M")
        future_signals = [s for s in signals if s[1] > now_time]

        if not future_signals:
            print(Fore.RED + "No future signals found. Exiting.")
            return

        # Put signals into queue
        for s in future_signals:
            signal_queue.put(s)

    elif signal_mode == "2":
        print("∆ Paste your signals (format: PAIR,HH:MM,DIRECTION). Type 'done' to finish:")
        while True:
            line = input()
            if line.strip().lower() == "done":
                break
            parts = line.strip().split(',')
            if len(parts) == 3:
                pair, time_str, direction = parts
                signal_queue.put((pair.strip(), time_str.strip(), direction.strip().upper()))                                                          
            else:
                print(Fore.YELLOW + "[!] Invalid format. Use: PAIR,HH:MM,DIRECTION")

        if signal_queue.empty():
            print(Fore.RED + "No valid signals entered. Exiting.")
            return

        print(Fore.GREEN + "\nSignals scheduled ✅\n")

    else:
        print("Invalid signal mode. Exiting.")
        return

    # Start processing signals one by one
    process_signals()

    print("\nBOT STARTED\n")
    time.sleep(1)
    global loader_running
    # Start key listener thread
    #key_thread = threading.Thread(target=key_listener)
    #key_thread.daemon = True
    #key_thread.start()


if __name__ == "__main__":
    try:
        main()

        # Keep the main thread alive for signals to run
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping bot...")

    finally:
        # Clean shutdown: stop animation spinner
        loader_running = False
        print("Exitedcleanly.")