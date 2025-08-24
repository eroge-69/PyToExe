import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import string
import itertools
import requests
import queue
import os
import random

# -----------------------------
# Config
# -----------------------------
ALLOWED_CHARS = string.ascii_lowercase + string.digits + "_"  # Mojang-safe
MOJANG_URL = "https://api.mojang.com/users/profiles/minecraft/{name}"
DEFAULT_DELAY_MS = 150
LOG_FILE = "logs.txt"
AVAILABLE_FILE = "available.txt"

OBJECT_WORDS = [
    "guitar","piano","stone","water","cloud","table","chair","lamp","rope","sand","tree","rock","gold",
    "iron","bell","drum","glass","brick","wheel","crate","spear","torch","tower","river","mountain","bottle",
    "spoon","fork","plate","cable","mouse","keyboard","screen","phone","radio","laser","engine","gear"
]

THREE_LETTER_REAL = [
    "sun","box","car","bus","van","pen","cup","cap","map","key","bed","bag","log","ore","ice","gem","oak",
    "ash","tin","ore","hut","web","rod","axe","bow","ore","mud","hay","cow","pig","hen","egg","ink","jar"
]

LEET_MAP = {
    "a": ["x","4"],
    "e": ["3"],
    "i": ["1"],
    "o": ["0"],
    "s": ["5","z"],
    "t": ["7"],
}

SEED_CATEGORIES = {
    "instruments": ["guitar", "piano", "drum", "violin", "flute", "sax", "trumpet"],
    "furniture": ["chair", "table", "lamp", "bed", "sofa", "stool"],
    "tools": ["hammer", "axe", "screw", "wheel", "rope", "gear", "cable"],
    "animals": ["dog", "cat", "cow", "pig", "hen", "bat", "fox"],
}

# -----------------------------
# Globals
# -----------------------------
stop_event = threading.Event()
ui_queue = queue.Queue()
available_set = set()

# -----------------------------
# Utilities
# -----------------------------
def safe_log(msg: str):
    ui_queue.put(("log", msg))
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass

def load_available_set():
    if os.path.exists(AVAILABLE_FILE):
        with open(AVAILABLE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                available_set.add(line.strip())

def save_available(name: str):
    if name in available_set:
        return
    available_set.add(name)
    with open(AVAILABLE_FILE, "a", encoding="utf-8") as f:
        f.write(name + "\n")

def mojang_status(session: requests.Session, name: str):
    try:
        r = session.get(MOJANG_URL.format(name=name), timeout=8)
    except requests.RequestException as e:
        return ("error", f"req-failed: {e}")
    if r.status_code == 200:
        try:
            data = r.json()
            if isinstance(data, dict) and "id" in data:
                return "taken"
            return "taken"
        except Exception:
            return "taken"
    elif r.status_code == 204:
        return "available"
    elif r.status_code == 404:
        text = r.text.lower()
        if "couldn't find" in text or "not found" in text:
            return "available"
        return ("error", 404)
    elif r.status_code == 429:
        return "rate_limited"
    else:
        return ("error", r.status_code)

def backoff_sleep(attempt: int):
    delay = min(60, 2 ** max(0, attempt - 1))
    time.sleep(delay)

def generate_leet_variations(word: str, max_variants: int = 10):
    word = word.lower()
    variants = set()
    for i, ch in enumerate(word):
        if ch in LEET_MAP:
            for repl in LEET_MAP[ch]:
                candidate = word[:i] + repl + word[i+1:]
                if all(c in ALLOWED_CHARS for c in candidate):
                    variants.add(candidate)
    if len(word) >= 3:
        variants.add(word[0] + "_" + word[1:])
    if len(word) <= 12:
        variants.add(word + "1")
        variants.add(word + "0")
    out = []
    for v in variants:
        out.append(v)
        if len(out) >= max_variants:
            break
    return out

def generate_ai_object_names(max_count=1000):
    seen = set()
    while True:
        category = random.choice(list(SEED_CATEGORIES.keys()))
        base = random.choice(SEED_CATEGORIES[category])
        name = base
        if random.random() < 0.4:
            name += str(random.randint(1,9))
        if random.random() < 0.3:
            idx = random.randint(0, len(name)-1)
            if name[idx] in LEET_MAP:
                name = name[:idx] + random.choice(LEET_MAP[name[idx]]) + name[idx+1:]
        if name not in seen:
            seen.add(name)
            yield name
        if len(seen) >= max_count:
            seen.clear()

# -----------------------------
# Worker loops
# -----------------------------
def check_names_iter(names_iterable, delay_ms: int):
    stop_event.clear()
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (NameChecker/1.0)"})
    rate_attempt = 0
    count = 0
    for name in names_iterable:
        if stop_event.is_set():
            safe_log("⏹️ Stopped.")
            ui_queue.put(("status", "Stopped"))
            return
        name = name.strip()
        if not name or any(c not in ALLOWED_CHARS for c in name):
            continue
        status = mojang_status(session, name)
        count += 1
        if status == "available":
            safe_log(f"✅ AVAILABLE: {name}")
            save_available(name)
        elif status == "taken":
            safe_log(f"❌ TAKEN: {name}")
        elif status == "rate_limited":
            safe_log("⚠️ 429 rate limited. Backing off...")
            rate_attempt += 1
            backoff_sleep(rate_attempt)
            continue
        else:
            code = status[1] if isinstance(status, tuple) else "unknown"
            safe_log(f"⚠️ ERROR ({code}) for {name}")
        ui_queue.put(("progress", 1))
        ui_queue.put(("count", 1))
        time.sleep(max(0, delay_ms) / 1000.0)
    ui_queue.put(("status", "Done"))
    safe_log("✅ Done.")

# -----------------------------
# Start functions
# -----------------------------
def start_bruteforce(delay_ms: int):
    ui_queue.put(("reset_progress", 37 ** 3))
    ui_queue.put(("status", "Brute forcing 3-letter names"))
    def gen():
        for tup in itertools.product(ALLOWED_CHARS, repeat=3):
            yield "".join(tup)
    threading.Thread(target=check_names_iter, args=(gen(), delay_ms), daemon=True).start()

def start_objects(delay_ms: int):
    names = [w.lower() for w in OBJECT_WORDS if all(c in ALLOWED_CHARS for c in w.lower())]
    ui_queue.put(("reset_progress", len(names)))
    ui_queue.put(("status", "Checking object names"))
    threading.Thread(target=check_names_iter, args=(names, delay_ms), daemon=True).start()

def start_three_letter_real(delay_ms: int):
    names = [w.lower() for w in THREE_LETTER_REAL if len(w) == 3 and all(c in ALLOWED_CHARS for c in w.lower())]
    ui_queue.put(("reset_progress", len(names)))
    ui_queue.put(("status", "Checking 3-letter real words"))
    threading.Thread(target=check_names_iter, args=(names, delay_ms), daemon=True).start()

def start_leet_from_input(base_word: str, delay_ms: int):
    base_word = base_word.strip().lower()
    if not base_word:
        safe_log("⚠️ Enter a base word first.")
        return
    variants = generate_leet_variations(base_word)
    if not variants:
        safe_log("⚠️ No variants produced.")
        return
    ui_queue.put(("reset_progress", len(variants)))
    ui_queue.put(("status", f"Checking leet variations of '{base_word}'"))
    threading.Thread(target=check_names_iter, args=(variants, delay_ms), daemon=True).start()

def start_check_single(name: str, delay_ms: int):
    name = name.strip().lower()
    if not name:
        safe_log("⚠️ Enter a name to check.")
        return
    ui_queue.put(("reset_progress", 1))
    ui_queue.put(("status", f"Checking '{name}'"))
    threading.Thread(target=check_names_iter, args=([name], delay_ms), daemon=True).start()

def start_ai_generator(delay_ms: int):
    ui_queue.put(("reset_progress", 1000))
    ui_queue.put(("status", "AI Object Generator"))
    threading.Thread(target=check_names_iter, args=(generate_ai_object_names(1000), delay_ms), daemon=True).start()

def stop_all():
    stop_event.set()

# -----------------------------
# GUI
# -----------------------------
def build_gui():
    load_available_set()
    root = tk.Tk()
    root.title("Luxis (Mojang API)")
    root.geometry("860x600")
    root.configure(bg="#1e1e1e")

    header = tk.Label(root, text="Luxis - Minecraft Name Checker", bg="#1e1e1e", fg="white",
                      font=("Segoe UI", 16, "bold"))
    header.pack(pady=(10, 6))

    ctrl = tk.Frame(root, bg="#1e1e1e")
    ctrl.pack(fill="x", padx=12)

    tk.Label(ctrl, text="Delay (ms):", bg="#1e1e1e", fg="white").grid(row=0, column=0, sticky="w", padx=(0,6))
    delay_var = tk.IntVar(value=DEFAULT_DELAY_MS)
    delay_scale = ttk.Scale(ctrl, from_=0, to=1000, orient="horizontal",
                            command=lambda v: delay_var.set(int(float(v))))
    delay_scale.set(DEFAULT_DELAY_MS)
    delay_scale.grid(row=0, column=1, sticky="we", padx=(0,12))
    ctrl.grid_columnconfigure(1, weight=1)

    # Buttons
    btn1 = ttk.Button(ctrl, text="🔎 Brute-force 3-letter",
                      command=lambda: start_bruteforce(delay_var.get()))
    btn1.grid(row=0, column=2, padx=6)
    btn2 = ttk.Button(ctrl, text="📦 Objects/Things",
                      command=lambda: start_objects(delay_var.get()))
    btn2.grid(row=0, column=3, padx=6)
    btn3 = ttk.Button(ctrl, text="🔤 3-letter Real Words",
                      command=lambda: start_three_letter_real(delay_var.get()))
    btn3.grid(row=0, column=4, padx=6)
    ai_btn = ttk.Button(ctrl, text="🤖 AI Object Generator",
                        command=lambda: start_ai_generator(delay_var.get()))
    ai_btn.grid(row=0, column=5, padx=6)
    stop_btn = ttk.Button(ctrl, text="⛔ Stop", command=stop_all)
    stop_btn.grid(row=0, column=6, padx=6)

    manual_frame = tk.Frame(root, bg="#1e1e1e")
    manual_frame.pack(fill="x", padx=12, pady=(8, 0))
    tk.Label(manual_frame, text="Manual name:", bg="#1e1e1e", fg="white").grid(row=0, column=0, sticky="w")
    manual_entry = ttk.Entry(manual_frame, width=24)
    manual_entry.grid(row=0, column=1, padx=6)
    check_btn = ttk.Button(manual_frame, text="Check",
                           command=lambda: start_check_single(manual_entry.get(), delay_var.get()))
    check_btn.grid(row=0, column=2, padx=6)
    tk.Label(manual_frame, text="Leet base word:", bg="#1e1e1e", fg="white").grid(row=0, column=3, sticky="w", padx=(16,0))
    leet_entry = ttk.Entry(manual_frame, width=24)
    leet_entry.grid(row=0, column=4, padx=6)
    leet_btn = ttk.Button(manual_frame, text="Generate Variations",
                          command=lambda: start_leet_from_input(leet_entry.get(), delay_var.get()))
    leet_btn.grid(row=0, column=5, padx=6)

    stats_frame = tk.Frame(root, bg="#1e1e1e")
    stats_frame.pack(fill="x", padx=12, pady=(8, 4))
    status_var = tk.StringVar(value="Idle")
    status_lbl = tk.Label(stats_frame, textvariable=status_var, bg="#1e1e1e", fg="#d0d0d0")
    status_lbl.pack(anchor="w")
    progress = ttk.Progressbar(stats_frame, mode="determinate")
    progress.pack(fill="x", pady=(6, 4))
    counts_var = tk.StringVar(value="Checked: 0 • Available saved: {}".format(len(available_set)))
    counts_lbl = tk.Label(stats_frame, textvariable=counts_var, bg="#1e1e1e", fg="#9ad27d")
    counts_lbl.pack(anchor="w")

    log = scrolledtext.ScrolledText(root, height=18, bg="#111", fg="#00ff66",
                                    insertbackground="white", font=("Consolas", 11))
    log.pack(fill="both", expand=True, padx=12, pady=(4, 10))

    def process_ui_queue():
        while True:
            try:
                item = ui_queue.get_nowait()
            except queue.Empty:
                break
            kind = item[0]
            if kind == "log":
                log.insert(tk.END, item[1] + "\n")
                log.see(tk.END)
            elif kind == "status":
                status_var.set(item[1])
            elif kind == "reset_progress":
                progress["maximum"] = max(1, int(item[1]))
                progress["value"] = 0
                counts_var.set("Checked: 0 • Available saved: {}".format(len(available_set)))
            elif kind == "progress":
                progress["value"] = min(progress["maximum"], progress["value"] + int(item[1]))
            elif kind == "count":
                text = counts_var.get()
                try:
                    cur = int(text.split("Checked: ")[1].split(" • ")[0])
                except Exception:
                    cur = 0
                cur += int(item[1])
                counts_var.set(f"Checked: {cur} • Available saved: {len(available_set)}")

    def tick():
        process_ui_queue()
        root.after(100, tick)

    tick()
    return root

# -----------------------------
# Entry
# -----------------------------
if __name__ == "__main__":
    try:
        app = build_gui()
        app.mainloop()
    except KeyboardInterrupt:
        pass
