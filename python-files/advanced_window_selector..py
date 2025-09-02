# Advanced Window Selector with Login, Loading Animation, and Fancy UI
# -------------------------------------------------------------------
# Retains the core behavior: let the user choose a window and set it Always-On-Top.
# Adds: 1) Login screen (username: Jack, password: Ghnf445m)
#       2) "Decoding" loading animation
#       3) Polished selector and a faux "advanced" control panel after pinning
#
# Requirements (Windows-only):
#   pip install pywin32 psutil
#
# Usage:
#   python advanced_window_selector.py
#
# Notes:
# - No changes to the fundamental behavior (pin selected window top-most).
# - Everything else is purely UX polish and optics.

import sys
import threading
import time
import random
import string
from dataclasses import dataclass

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except Exception as e:
    print("This script requires tkinter (usually included with Python).", e)
    sys.exit(1)

try:
    import win32gui
    import win32con
    import win32process
except Exception:
    print("This script requires 'pywin32'. Install with: pip install pywin32")
    sys.exit(1)

try:
    import psutil
except Exception:
    print("Optional: install 'psutil' for process info (pip install psutil)")
    psutil = None

# --------------------------
# Helpers (Windows)
# --------------------------

def is_window_visible_with_title(hwnd: int) -> bool:
    if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
        return False
    title = win32gui.GetWindowText(hwnd).strip()
    if not title:
        return False
    # Skip tool windows or the shell's program manager
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if style & win32con.WS_EX_TOOLWINDOW:
        return False
    return True


def list_top_level_windows():
    windows = []
    def enum_handler(hwnd, _):
        if is_window_visible_with_title(hwnd):
            title = win32gui.GetWindowText(hwnd)
            windows.append((hwnd, title))
    win32gui.EnumWindows(enum_handler, None)
    # De-dup & sort by title
    uniq = {}
    for hwnd, title in windows:
        uniq[hwnd] = title
    items = sorted([(h, t) for h, t in uniq.items()], key=lambda x: x[1].lower())
    return items


def set_topmost(hwnd: int, topmost: bool = True):
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST if topmost else win32con.HWND_NOTOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
    )


def get_process_info(hwnd: int):
    try:
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        name = None
        if psutil:
            try:
                p = psutil.Process(pid)
                name = p.name()
            except Exception:
                name = None
        return pid, name
    except Exception:
        return None, None

# --------------------------
# Fancy Styling
# --------------------------

DARK_BG = "#0b0f14"
CARD_BG = "#111822"
ACCENT = "#7cc5ff"
ACCENT_DIM = "#2b6ca3"
TEXT = "#e6f2ff"
MUTED = "#89a3b8"
FAIL = "#ff7a7a"
OK = "#75ffa1"

class Themer:
    @staticmethod
    def apply(root: tk.Tk):
        style = ttk.Style(root)
        # Use "clam" to unlock theming
        style.theme_use("clam")
        style.configure("TFrame", background=DARK_BG)
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("TLabel", background=DARK_BG, foreground=TEXT)
        style.configure("Muted.TLabel", background=DARK_BG, foreground=MUTED)
        style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT)
        style.configure("Accent.TLabel", background=DARK_BG, foreground=ACCENT)
        style.configure("TEntry", fieldbackground="#0e141b", foreground=TEXT, insertcolor=TEXT)
        style.configure("TButton", background=ACCENT_DIM, foreground=TEXT, bordercolor=ACCENT, focusthickness=3, focuscolor=ACCENT)
        style.map("TButton",
                  background=[("active", ACCENT)],
                  foreground=[("disabled", "#667789")])
        style.configure("Search.TEntry", fieldbackground="#0e141b", foreground=TEXT)
        style.configure("Info.TLabel", background=CARD_BG, foreground=MUTED)
        style.configure("Success.TLabel", background=CARD_BG, foreground=OK)
        style.configure("Danger.TLabel", background=CARD_BG, foreground=FAIL)

# --------------------------
# Login Screen
# --------------------------

VALID_USER = "Jack"
VALID_PASS = "Ghnf445m"

class LoginFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, padding=24)
        self.on_success = on_success
        self.configure(style="TFrame")

        wrapper = ttk.Frame(self, style="Card.TFrame", padding=24)
        wrapper.pack(expand=True)

        title = ttk.Label(wrapper, text="Secure Access Portal", style="Card.TLabel", font=("Segoe UI", 20, "bold"))
        subtitle = ttk.Label(wrapper, text="Restricted Area — Authorized Users Only", style="Info.TLabel")
        title.pack(anchor="w")
        subtitle.pack(anchor="w", pady=(0, 16))

        form = ttk.Frame(wrapper, style="Card.TFrame")
        form.pack(fill="x")

        ttk.Label(form, text="Username", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.user_var = tk.StringVar()
        user_entry = ttk.Entry(form, textvariable=self.user_var)
        user_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(form, text="Password", style="Card.TLabel").grid(row=2, column=0, sticky="w")
        self.pass_var = tk.StringVar()
        pass_entry = ttk.Entry(form, textvariable=self.pass_var, show="•")
        pass_entry.grid(row=3, column=0, sticky="ew")

        form.columnconfigure(0, weight=1)

        self.status = ttk.Label(wrapper, text="", style="Danger.TLabel")
        self.status.pack(anchor="w", pady=(10, 8))

        btn = ttk.Button(wrapper, text="Log In", command=self.try_login)
        btn.pack(anchor="e")

        user_entry.focus_set()

    def try_login(self):
        u, p = self.user_var.get().strip(), self.pass_var.get().strip()
        if u == VALID_USER and p == VALID_PASS:
            self.status.configure(text="")
            self.on_success()
        else:
            self.status.configure(text="Invalid credentials. Access denied.")

# --------------------------
# Loading / Decoding Screen
# --------------------------

class LoadingFrame(ttk.Frame):
    def __init__(self, master, on_done, duration=2.8):
        super().__init__(master, padding=24)
        self.on_done = on_done
        self.duration = duration
        self.configure(style="TFrame")

        card = ttk.Frame(self, style="Card.TFrame", padding=24)
        card.pack(expand=True, fill="both")

        ttk.Label(card, text="System Bootstrap", style="Card.TLabel", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(card, text="Initializing modules...", style="Info.TLabel").pack(anchor="w", pady=(0, 12))

        self.console = tk.Text(card, height=12, bg="#05080c", fg=ACCENT, insertbackground=ACCENT, relief="flat")
        self.console.pack(fill="both", expand=True)
        self.console.configure(state="disabled")

        self.prog = ttk.Progressbar(card, mode="indeterminate")
        self.prog.pack(fill="x", pady=(12, 0))
        self.prog.start(10)

        self._running = True
        threading.Thread(target=self._writer, daemon=True).start()
        self.after(int(self.duration * 1000), self.finish)

    def _writer(self):
        start = time.time()
        lines = [
            "[OK] entropy: reseeded RNG", "[OK] bus: handshake AES-GCM", "[OK] core: hooks mounted",
            "[OK] ui: shader pipeline built", "[OK] wm: window map cached", "[OK] net: offline mode",
        ]
        while self._running and time.time() - start < self.duration:
            time.sleep(0.06)
            if random.random() < 0.25:
                self._append(random_hex_line())
            else:
                self._append(random.choice(lines))
        # Final lines
        self._append("[OK] selector: ready")

    def _append(self, text):
        self.console.configure(state="normal")
        gib = obfuscate(text)
        self.console.insert("end", gib + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def finish(self):
        self._running = False
        self.prog.stop()
        self.on_done()


def random_hex_line():
    chunks = ["".join(random.choices("0123456789abcdef", k=random.randint(2, 8))) for _ in range(random.randint(6, 18))]
    return ":".join(chunks)


def obfuscate(s: str):
    # Randomly swap a few characters for a decoding vibe
    s = list(s)
    for i in range(len(s)):
        if random.random() < 0.06 and s[i].isalnum():
            s[i] = random.choice("#$%^*|/")
    return "".join(s)

# --------------------------
# Window Selector
# --------------------------

@dataclass
class WinItem:
    hwnd: int
    title: str

class SelectorFrame(ttk.Frame):
    def __init__(self, master, on_selected):
        super().__init__(master, padding=16)
        self.on_selected = on_selected
        self.configure(style="TFrame")

        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Window Selector", style="Accent.TLabel", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Button(header, text="Refresh", command=self.refresh).pack(side="right")

        search_row = ttk.Frame(self, style="TFrame")
        search_row.pack(fill="x", pady=(10, 6))
        ttk.Label(search_row, text="Search", style="TLabel").pack(side="left")
        self.q = tk.StringVar()
        ent = ttk.Entry(search_row, textvariable=self.q, style="Search.TEntry")
        ent.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ent.bind("<KeyRelease>", lambda e: self._filter())

        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(body, columns=("title", "pid", "proc"), show="headings", selectmode="browse")
        self.tree.heading("title", text="Title")
        self.tree.heading("pid", text="PID")
        self.tree.heading("proc", text="Process")
        self.tree.column("title", width=400)
        self.tree.column("pid", width=80, anchor="center")
        self.tree.column("proc", width=180, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self._dbl)

        self._all: list[WinItem] = []
        self.refresh()

    def refresh(self):
        self._all = [WinItem(hwnd=h, title=t) for h, t in list_top_level_windows()]
        self._render(self._all)

    def _render(self, items):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for it in items:
            pid, name = get_process_info(it.hwnd)
            self.tree.insert("", "end", iid=str(it.hwnd), values=(it.title, pid or "-", name or "-"))

    def _filter(self):
        q = self.q.get().lower().strip()
        if not q:
            self._render(self._all)
            return
        filtered = [it for it in self._all if q in it.title.lower()]
        self._render(filtered)

    def _dbl(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        hwnd = int(sel[0])
        title = next((it.title for it in self._all if it.hwnd == hwnd), None)
        if hwnd and title:
            self.on_selected(hwnd, title)

# --------------------------
# Advanced Control Panel (Cosmetic + a few real controls)
# --------------------------

class ControlPanel(ttk.Frame):
    def __init__(self, master, hwnd: int, title: str):
        super().__init__(master, padding=16, style="TFrame")
        self.hwnd = hwnd
        self.title = title

        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Pinned: ", style="TLabel", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Label(header, text=title, style="Accent.TLabel", font=("Segoe UI", 12, "bold")).pack(side="left")

        # Cards row
        cards = ttk.Frame(self, style="TFrame")
        cards.pack(fill="x", pady=(10, 0))

        # Status Card
        status = ttk.Frame(cards, style="Card.TFrame", padding=14)
        status.pack(side="left", fill="x", expand=True, padx=(0, 8))
        pid, name = get_process_info(hwnd)
        ttk.Label(status, text="Window Status", style="Card.TLabel", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(status, text=f"HWND: {hwnd}", style="Info.TLabel").pack(anchor="w")
        ttk.Label(status, text=f"PID: {pid or '-'}", style="Info.TLabel").pack(anchor="w")
        ttk.Label(status, text=f"Process: {name or '-'}", style="Info.TLabel").pack(anchor="w")
        ok = ttk.Label(status, text="Topmost: ENABLED", style="Success.TLabel")
        ok.pack(anchor="w", pady=(6, 0))

        # Controls Card
        controls = ttk.Frame(cards, style="Card.TFrame", padding=14)
        controls.pack(side="left", fill="x", expand=True, padx=(8, 8))
        ttk.Label(controls, text="Controls", style="Card.TLabel", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        btn_unpin = ttk.Button(controls, text="Unpin (Not Topmost)", command=lambda: self._set_top(False))
        btn_unpin.pack(anchor="w", pady=(8, 4))
        btn_pin = ttk.Button(controls, text="Re-Pin (Topmost)", command=lambda: self._set_top(True))
        btn_pin.pack(anchor="w", pady=(0, 8))

        # Cosmetic meters
        meters = ttk.Frame(cards, style="Card.TFrame", padding=14)
        meters.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ttk.Label(meters, text="Live Telemetry", style="Card.TLabel", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.pb1 = ttk.Progressbar(meters, mode="determinate", maximum=100)
        self.pb2 = ttk.Progressbar(meters, mode="determinate", maximum=100)
        self.pb3 = ttk.Progressbar(meters, mode="determinate", maximum=100)
        self.pb1.pack(fill="x", pady=(8, 4))
        self.pb2.pack(fill="x", pady=(4, 4))
        self.pb3.pack(fill="x", pady=(4, 0))

        self._animate_meters()

        # Footer tip
        tip = ttk.Label(self, text="Pro tip: Use the Refresh button in Selector if your target window was opened later.", style="Muted.TLabel")
        tip.pack(anchor="w", pady=(10, 0))

    def _set_top(self, on: bool):
        try:
            set_topmost(self.hwnd, on)
            state = "ENABLED" if on else "DISABLED"
            messagebox.showinfo("Topmost", f"Topmost {state} for\n{self.title}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set topmost: {e}")

    def _animate_meters(self):
        # Simple loop to fake telemetry
        def loop():
            while True:
                for pb in (self.pb1, self.pb2, self.pb3):
                    try:
                        pb["value"] = max(0, min(100, pb["value"] + random.randint(-15, 20)))
                    except tk.TclError:
                        return
                time.sleep(0.25)
        threading.Thread(target=loop, daemon=True).start()

# --------------------------
# App Shell
# --------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Window Selector — AOT Edition")
        self.geometry("800x550")
        self.minsize(720, 480)
        self.configure(bg=DARK_BG)
        self._current = None
        Themer.apply(self)
        self.show_login()

    def clear(self):
        if self._current is not None:
            self._current.destroy()
            self._current = None

    def show_login(self):
        self.clear()
        self._current = LoginFrame(self, on_success=self.show_loading)
        self._current.pack(fill="both", expand=True)

    def show_loading(self):
        self.clear()
        self._current = LoadingFrame(self, on_done=self.show_selector)
        self._current.pack(fill="both", expand=True)

    def show_selector(self):
        self.clear()
        self._current = SelectorFrame(self, on_selected=self.on_window_selected)
        self._current.pack(fill="both", expand=True)

    def on_window_selected(self, hwnd: int, title: str):
        try:
            set_topmost(hwnd, True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not set window Topmost: {e}")
            return
        # Transition to fancy control panel
        self.clear()
        self._current = ControlPanel(self, hwnd, title)
        self._current.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
