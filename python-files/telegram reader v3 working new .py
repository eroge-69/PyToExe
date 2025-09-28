import tkinter as tk
from tkinter import scrolledtext
import tkinter.font as tkFont
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberInvalidError
import os
import asyncio
import threading
import queue
import sys
import sys, os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
    return os.path.join(base_path, relative_path)

sound_file = resource_path("alert.wav")

# =========================
# THEME
# =========================
BG = "#0f1220"         # page background
PANEL = "#151a2e"      # panels / cards
TEXT = "#e6e9ff"       # primary text
MUTED = "#8c94b8"      # secondary text
ACCENT = "#6aa3ff"     # blue accent
ACCENT2 = "#7ef0c0"    # mint accent
MATRIX = "#00ff41"     # highlight green
HEADER_BG = "#10152a"  # header row
GRID_BORDER = "#2a2f4a"

ROW_ALT = "#13182b"        # alternating row (even rows)
ROW_HILITE = "#ffb347"     # bright warm highlight for unread rows
UNREAD_TEXT = "#0c1220"    # dark text on bright highlight
UNREAD_BORDER = "#ff9f1a"  # thin border color for unread cells

# =========================
# CUSTOM SOUND (your WAV)
# =========================
SOUND_PATH = sound_file 

# =========================
# TELEGRAM CREDS
# =========================
api_id = '27368434'
api_hash = '2dc42354066cb5ed14fc90f7b4668a10'

# =========================
# SESSION
# =========================
session_name = 'user_session'
if not os.path.exists(f'{session_name}.session'):
    print("Session file not found. Creating a new session...")
else:
    print("Using existing session file.")

client = TelegramClient(session_name, api_id, api_hash)

# =========================
# CHANNELS TO MONITOR
# =========================
channels_to_monitor = [-1001622365719, -1001617718235, 7868286574]

# =========================
# GUI DATA / HEADERS
# =========================
headers = ["Coin", "Profit", "Direction", "Leverage", "Entry", "Stop Loss", "Targets", "Time", "Instruction"]

# Thread-safe queues (Telethon thread -> Tk main thread)
log_queue = queue.Queue()
signal_queue = queue.Queue()

# Row index tracker for the table
signal_table_row_index = 1

# Keep widgets grouped by row so we can toggle highlight on click
row_widgets = {}      # row_index -> list[Label]
row_unread = set()    # rows that are unread (highlighted)

# =========================
# GUI (root + layout) — created before auth so prompts can use it
# =========================
root = tk.Tk()
root.title("Telegram Signal Monitor — Dark Panel")
root.configure(bg=BG)
root.geometry("1200x700")

# Fonts
base_font = tkFont.Font(family="Segoe UI", size=10)
small_font = tkFont.Font(family="Segoe UI", size=9)
bold_font = tkFont.Font(family="Segoe UI", size=10, weight="bold")
unread_font = tkFont.Font(family="Segoe UI", size=10, weight="bold")  # bold for unread rows

# Header
header_frame = tk.Frame(root, bg=BG)
header_frame.pack(fill="x", pady=(12, 4), padx=12)

logo = tk.Canvas(header_frame, width=40, height=40, bg=BG, highlightthickness=0)
def rounded_rect(c, x1, y1, x2, y2, r, **kw):
    points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2,
              x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
    return c.create_polygon(points, smooth=True, **kw)
rounded_rect(logo, 2, 2, 38, 38, 10, fill=ACCENT)
logo.create_text(20, 21, text="TG", fill="#0c1220", font=("Segoe UI", 11, "bold"))
logo.pack(side="left")

title_block = tk.Frame(header_frame, bg=BG)
title_block.pack(side="left", padx=10)

title_lbl = tk.Label(title_block, text="Telegram Signal Monitor", bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold"))
title_lbl.pack(anchor="w")
sub_lbl = tk.Label(title_block, text="Live messages → parsed into a styled table", bg=BG, fg=MUTED, font=small_font)
sub_lbl.pack(anchor="w")

# Message log panel
log_panel = tk.Frame(root, bg=BG)
log_panel.pack(fill="x", padx=12, pady=(0, 10))

log_label = tk.Label(log_panel, text="Message Log", bg=BG, fg=MUTED, font=bold_font)
log_label.pack(anchor="w", pady=(0, 6))

log_card = tk.Frame(log_panel, bg=PANEL, highlightthickness=1, highlightbackground=GRID_BORDER, bd=0)
log_card.pack(fill="x", padx=0, pady=0)

message_log = scrolledtext.ScrolledText(log_card, wrap=tk.WORD, width=80, height=8, bg=PANEL, fg=TEXT,
                                        insertbackground=TEXT, font=base_font, borderwidth=0, relief="flat")
message_log.pack(padx=10, pady=10, fill="both", expand=True)

# Signal table container (scrollable)
table_panel = tk.Frame(root, bg=BG)
table_panel.pack(fill="both", expand=True, padx=12, pady=(0, 12))

table_label = tk.Label(table_panel, text="Parsed Signals", bg=BG, fg=MUTED, font=bold_font)
table_label.pack(anchor="w", pady=(0, 6))

# Outer "card"
signal_card = tk.Frame(table_panel, bg=PANEL, highlightthickness=1, highlightbackground=GRID_BORDER, bd=0)
signal_card.pack(fill="both", expand=True)

# Scrollable canvas for table
canvas = tk.Canvas(signal_card, bg=PANEL, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar_y = tk.Scrollbar(signal_card, orient="vertical", command=canvas.yview, bg=PANEL)
scrollbar_y.pack(side="right", fill="y")
scrollbar_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview, bg=PANEL)
scrollbar_x.pack(fill="x")

canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

signal_table_frame = tk.Frame(canvas, bg=PANEL)
canvas.create_window((0, 0), window=signal_table_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
signal_table_frame.bind("<Configure>", on_frame_configure)

def _on_mousewheel(event):
    delta = -1 * int(event.delta/120) if sys.platform.startswith("win") else (-1 if getattr(event, "num", 0) == 5 else 1)
    canvas.yview_scroll(delta, "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)
canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux

# Table headers
for col, header in enumerate(headers):
    lbl = tk.Label(
        signal_table_frame, text=header, bg=HEADER_BG, fg=TEXT,
        font=("Segoe UI", 10, "bold"), padx=10, pady=8, borderwidth=0
    )
    lbl.grid(row=0, column=col, sticky="nsew", padx=(0, 1), pady=(0, 1))
    signal_table_frame.grid_columnconfigure(col, weight=1, minsize=110)

# =========================
# SOUND
# =========================
def play_signal_sound():
    """
    Use your custom WAV on Windows; fall back gracefully elsewhere.
    """
    try:
        if sys.platform.startswith("win"):
            import winsound
            if SOUND_PATH and os.path.isfile(SOUND_PATH):
                winsound.PlaySound(SOUND_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            if SOUND_PATH and os.path.isfile(SOUND_PATH):
                try:
                    import simpleaudio
                    simpleaudio.WaveObject.from_wave_file(SOUND_PATH).play()
                except Exception:
                    try:
                        root.bell()
                    except Exception:
                        pass
            else:
                root.bell()
    except Exception:
        try:
            root.bell()
        except Exception:
            pass

# =========================
# STYLE HELPERS
# =========================
def compute_fg(header: str, value: str, unread: bool):
    """Return the foreground color for a cell based on header/value and unread state."""
    if unread:
        return UNREAD_TEXT  # dark text on bright gold
    # read rows: contextual colors
    if header == "Coin":
        return TEXT
    if header == "Direction" and isinstance(value, str):
        v = value.lower()
        if "long" in v or "buy" in v:
            return MATRIX
        if "short" in v or "sell" in v:
            return ACCENT
    if header == "Instruction" and value:
        return MATRIX if "⚠️" in value else ACCENT2
    return MUTED

def set_row_bg(row_idx: int, color: str):
    for w in row_widgets.get(row_idx, []):
        w.configure(bg=color)

def restyle_row_read(row_idx: int):
    """When marking read: restore alternating bg, restore fg per content, normal font, remove border."""
    base = PANEL if (row_idx % 2 == 1) else ROW_ALT
    for i, w in enumerate(row_widgets.get(row_idx, [])):
        header = headers[i]
        value = w.cget("text")
        w.configure(
            bg=base,
            fg=compute_fg(header, value, unread=False),
            font=base_font,
            borderwidth=0,
            relief="flat",
            highlightthickness=0
        )

# =========================
# ROW HIGHLIGHT TOGGLE
# =========================
def mark_row_unread(row_idx: int):
    row_unread.add(row_idx)
    for i, w in enumerate(row_widgets.get(row_idx, [])):
        header = headers[i]
        value = w.cget("text")
        w.configure(
            bg=ROW_HILITE,
            fg=compute_fg(header, value, unread=True),
            font=unread_font,
            borderwidth=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=UNREAD_BORDER,
            highlightcolor=UNREAD_BORDER
        )

def mark_row_read(row_idx: int):
    if row_idx in row_unread:
        row_unread.discard(row_idx)
        restyle_row_read(row_idx)

def on_row_click(event, row_idx: int):
    mark_row_read(row_idx)

# =========================
# TABLE RENDERING
# =========================
def add_signal_to_table(data: dict):
    global signal_table_row_index

    current_row = signal_table_row_index
    row_widgets[current_row] = []

    # Build cells as UNREAD initially (gold bg, dark text, bold, thin border)
    for col, header in enumerate(headers):
        value = data.get(header, "")
        cell = tk.Label(
            signal_table_frame,
            text=value,
            bg=ROW_HILITE,
            fg=compute_fg(header, value, unread=True),
            font=unread_font,
            padx=8, pady=6,
            borderwidth=1, relief="solid",
            highlightthickness=1,
            highlightbackground=UNREAD_BORDER,
            highlightcolor=UNREAD_BORDER,
            anchor="w", justify="left", cursor="hand2"
        )
        cell.grid(row=current_row, column=col, sticky="nsew", padx=(0, 1), pady=(0, 1))
        cell.bind("<Button-1>", lambda e, r=current_row: on_row_click(e, r))
        row_widgets[current_row].append(cell)

    # Mark as unread so it stays highlighted until clicked
    row_unread.add(current_row)
    signal_table_row_index += 1

# =========================
# QUEUE CONSUMERS (Tk thread)
# =========================
def pump_log_queue():
    try:
        while True:
            msg = log_queue.get_nowait()
            message_log.insert(tk.END, msg + "\n")
            message_log.see(tk.END)
    except queue.Empty:
        pass
    root.after(100, pump_log_queue)

def pump_signal_queue():
    try:
        added = False
        while True:
            data = signal_queue.get_nowait()
            add_signal_to_table(data)
            added = True
    except queue.Empty:
        pass
    if 'added' in locals() and added:
        play_signal_sound()
    root.after(120, pump_signal_queue)

pump_log_queue()
pump_signal_queue()

# =========================
# GUI PROMPTS for Telegram auth (phone, code, 2FA) — styled popups
# =========================
def gui_prompt_async(title: str, message: str, secret: bool = False) -> asyncio.Future:
    """
    Create a small styled modal asking the user for input.
    Returns an asyncio.Future that resolves with the entered text (or None if canceled).
    """
    fut = asyncio.get_event_loop().create_future()

    def _open_dialog():
        win = tk.Toplevel(root)
        win.title(title)
        win.configure(bg=BG)
        win.transient(root)
        win.grab_set()
        win.resizable(False, False)

        # center on parent
        win.update_idletasks()
        w, h = 380, 160
        x = root.winfo_x() + (root.winfo_width() // 2) - (w // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

        # Content
        lab = tk.Label(win, text=message, bg=BG, fg=TEXT, font=bold_font, wraplength=340, justify="left")
        lab.pack(padx=16, pady=(16, 8), anchor="w")

        ent_var = tk.StringVar()
        ent = tk.Entry(win, textvariable=ent_var, bg=PANEL, fg=TEXT, insertbackground=TEXT,
                       relief="flat", highlightthickness=1, highlightbackground=GRID_BORDER,
                       font=base_font, show="*" if secret else "")
        ent.pack(padx=16, pady=(0, 12), fill="x")
        ent.focus_set()

        btns = tk.Frame(win, bg=BG)
        btns.pack(fill="x", padx=16, pady=(0, 12))

        def _ok():
            if not fut.done():
                fut.set_result(ent_var.get().strip() or "")
            win.destroy()

        def _cancel():
            if not fut.done():
                fut.set_result(None)
            win.destroy()

        okb = tk.Button(btns, text="OK", command=_ok, bg="#10152a", fg=TEXT, relief="flat")
        okb.pack(side="right", padx=(6, 0))
        cb = tk.Button(btns, text="Cancel", command=_cancel, bg="#10152a", fg=MUTED, relief="flat")
        cb.pack(side="right")

        # Enter/Esc bindings
        win.bind("<Return>", lambda e: _ok())
        win.bind("<Escape>", lambda e: _cancel())

    # open the dialog safely on Tk thread
    root.after(0, _open_dialog)
    return fut

async def ask_phone_number():
    return await gui_prompt_async("Telegram Login", "Enter your phone number (with country code):")

async def ask_login_code():
    return await gui_prompt_async("Telegram Code", "Enter the login code Telegram just sent you:")

async def ask_two_step_password():
    return await gui_prompt_async("Two-Step Verification", "Enter your Telegram password:", secret=True)

# =========================
# TELETHON: monitor loop (with GUI-based auth)
# =========================
async def monitor_channels():
    try:
        # Connect (non-interactive)
        await client.connect()

        if not await client.is_user_authorized():
            # 1) Ask for phone
            phone = await ask_phone_number()
            if not phone:
                log_queue.put("[Auth] Login cancelled (no phone).")
                return

            # 2) Send code and ask user to input it
            try:
                await client.send_code_request(phone)
            except PhoneNumberInvalidError:
                log_queue.put("[Auth] Invalid phone number.")
                return

            code = await ask_login_code()
            if not code:
                log_queue.put("[Auth] Login cancelled (no code).")
                return

            # 3) Try sign in with code; maybe ask for 2FA password
            try:
                await client.sign_in(phone=phone, code=code)
            except PhoneCodeInvalidError:
                log_queue.put("[Auth] Invalid login code.")
                return
            except SessionPasswordNeededError:
                pwd = await ask_two_step_password()
                if not pwd:
                    log_queue.put("[Auth] Login cancelled (no 2FA password).")
                    return
                try:
                    await client.sign_in(password=pwd)
                except Exception as e:
                    log_queue.put(f"[Auth] Two-step password error: {e}")
                    return

        # At this point we’re authenticated
        log_queue.put("Authenticated as user.")

        # Resolve and attach channels
        channels = []
        for channel in channels_to_monitor:
            try:
                entity = await client.get_entity(channel)
                channels.append(entity)
                title = getattr(entity, 'title', None) or getattr(entity, 'username', None) or str(channel)
                log_queue.put(f"Monitoring: {title}")
            except Exception as e:
                log_queue.put(f"Failed to add {channel}: {e}")

        if not channels:
            log_queue.put("No valid channels to monitor. Exiting...")
            return

        @client.on(events.NewMessage(chats=channels))
        async def handler(event):
            try:
                txt = event.message.message or ""
                sender = await event.get_chat()
                sender_name = getattr(sender, 'title', None) or getattr(sender, 'username', None) or "Unknown Sender"
                msg_line = f"New message from {sender_name}: {txt}"
                log_queue.put(msg_line)

                if "📩" in txt or "⚠️" in txt:
                    signal_data = parse_signal(txt)
                    if signal_data:
                        signal_queue.put(signal_data)
            except Exception as e:
                log_queue.put(f"[Handler Error] {e}")

        # Switch to standard Telethon loop
        await client.run_until_disconnected()

    except Exception as e:
        log_queue.put(f"[Monitor Error] {e}")

def start_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_channels())

# =========================
# PARSER (same as before)
# =========================
def parse_signal(message: str):
    data = {}
    if "📩" in message or "⚠️" in message:
        lines = message.split("\n")
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if "Pair:" in line:
                data["Coin"] = line.split(":", 1)[1].strip()
            elif "#" in line and "Fully close" not in line:
                data["Coin"] = line.strip()
            elif "Profit:" in line:
                data["Profit"] = line.split(":", 1)[1].strip()
            elif "Direction:" in line:
                data["Direction"] = line.split(":", 1)[1].strip()
            elif "Leverage:" in line:
                data["Leverage"] = line.split(":", 1)[1].strip()
            elif "Entry:" in line:
                data["Entry"] = line.split(":", 1)[1].strip()
            elif "Stop Loss:" in line:
                data["Stop Loss"] = line.split(":", 1)[1].strip()
            elif "Target" in line:
                if "Targets" not in data:
                    data["Targets"] = line.strip()
                else:
                    data["Targets"] += " | " + line.strip()
            elif "Time:" in line:
                data["Time"] = line.split(":", 1)[1].strip()
            elif "Fully close" in line or "⚠️" in line:
                data["Instruction"] = line.strip()
    return data

# =========================
# START TELEGRAM THREAD
# =========================
tg_thread = threading.Thread(target=start_asyncio_loop, daemon=True)
tg_thread.start()

# =========================
# CLEAN SHUTDOWN
# =========================
def on_close():
    try:
        if client and client.is_connected():
            def _disc():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(client.disconnect())
                    loop.close()
                except Exception:
                    pass
            threading.Thread(target=_disc, daemon=True).start()
    finally:
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# =========================
# MAINLOOP
# =========================
root.mainloop()
