import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import collections
import time
import threading
import requests
import re

# ----------------------
# Theme
BG = "#2c2f33"
ENTRY_BG = "#23272a"
BTN_BG = "#5865f2"
BTN_HOVER = "#7289da"
TEXT = "white"
MUTED = "#99aab5"
SUCCESS = "#43b581"
ERROR = "#f04747"

URL_REGEX = re.compile(r"^https?://", re.IGNORECASE)

# Safety limits
BULK_SAFE_THRESHOLD = 10    # typed confirmation if more than this
BULK_HARD_CAP = 200        # refuse runs over this many

# ----------------------
def post_once(url, payload, timeout=10):
    """Perform a single POST. Returns tuple (ok:bool, message:str)."""
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        ok = resp.status_code in (200, 201, 202, 204)
        return ok, f"HTTP {resp.status_code}: {resp.reason}"
    except Exception as e:
        return False, str(e)

# ----------------------
class VixerWebhookTester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VIXER webhook sender")
        self.geometry("1200x620")
        self.configure(bg=BG)
        try:
            self.iconbitmap("vixer.ico")
        except:
            pass

        # State
        self.payload = {"content": "hi"}
        self.recent = collections.deque(maxlen=10)

        self._build_ui()
        self._update_preview()

    # ----------------------
    def _build_ui(self):
        # ASCII banner
        banner_text = (
            " __      _________   ________ _____  \n"
            " \\ \\    / /_   _\\ \\ / /  ____|  __ \\ \n"
            "  \\ \\  / /  | |  \\ V /| |__  | |__) |\n"
            "   \\ \\/ /   | |   > < |  __| |  _  / \n"
            "    \\  /   _| |_ / . \\| |____| | \\ \\ \n"
            "     \\/   |_____/_/ \\_\\______|_|  \\_\\\n"
        )
        banner = tk.Label(self, text=banner_text, font=("Courier", 11, "bold"),
                          bg=BG, fg=MUTED, justify="center")
        banner.pack(pady=8)

        # Top frame
        top_frame = tk.Frame(self, bg=BG)
        top_frame.pack(fill="x", padx=24)

        left_col = tk.Frame(top_frame, bg=BG)
        left_col.pack(side="left", fill="both", expand=True)

        right_col = tk.Frame(top_frame, bg=BG)
        right_col.pack(side="right", fill="y", padx=(12, 0))

        # Webhook entry
        tk.Label(left_col, text="Webhook URL:",
                 bg=BG, fg=TEXT, font=("Arial", 11, "bold")).pack(anchor="w")
        self.url_var = tk.StringVar()
        self.entry = tk.Entry(left_col, textvariable=self.url_var, width=80,
                              bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                              relief="flat", font=("Consolas", 12))
        self.entry.pack(pady=(6, 10), ipady=6, fill="x")

        # Payload preview
        tk.Label(left_col, text="Payload Preview", bg=BG, fg=MUTED,
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.preview = tk.Text(left_col, bg=ENTRY_BG, fg=TEXT, bd=0,
                               font=("Consolas", 11), relief="flat",
                               wrap="none", height=8, padx=10, pady=8)
        self.preview.pack(fill="x")
        self.preview.configure(state="disabled")

        # Controls row
        ctrl_row = tk.Frame(left_col, bg=BG)
        ctrl_row.pack(pady=10, anchor="w")

        self.send_btn = tk.Button(ctrl_row, text="Send (single)", command=self.on_send_single,
                                  bg=BTN_BG, fg="white", font=("Arial", 11, "bold"),
                                  relief="flat", activebackground=BTN_HOVER)
        self.send_btn.pack(side="left", ipadx=12, ipady=6, padx=6)

        edit_btn = tk.Button(ctrl_row, text="Edit message", command=self.edit_payload,
                             bg=ENTRY_BG, fg=TEXT, relief="flat", activebackground=BTN_HOVER)
        edit_btn.pack(side="left", ipadx=10, ipady=6, padx=6)

        reset_btn = tk.Button(ctrl_row, text="Reset", command=self.reset_payload,
                              bg=ENTRY_BG, fg=TEXT, relief="flat", activebackground=BTN_HOVER)
        reset_btn.pack(side="left", ipadx=10, ipady=6, padx=6)

        # Status
        self.status = tk.Label(left_col, text="Ready", bg=BG, fg=MUTED, font=("Arial", 10))
        self.status.pack(anchor="w", pady=(6, 8))

        # History list
        tk.Label(left_col, text="Recent:", bg=BG, fg=MUTED,
                 font=("Arial", 9)).pack(anchor="w")
        self.history = tk.Listbox(left_col, bg=ENTRY_BG, fg=TEXT, bd=0, highlightthickness=0,
                                  activestyle="none", font=("Consolas", 10), height=5)
        self.history.pack(fill="x", pady=(6, 10))
        self.history.bind("<Double-Button-1>", self.use_selected_history)

        # Right column: bulk-test controls
        right_title = tk.Label(right_col, text="Bulk", bg=BG, fg=TEXT, font=("Arial", 11, "bold"))
        right_title.pack(anchor="n", pady=(4, 8))

        # Count + interval inputs
        tk.Label(right_col, text="Messages to send:", bg=BG, fg=MUTED, font=("Arial", 10)).pack(anchor="w")
        self.count_var = tk.IntVar(value=5)
        self.count_spin = tk.Spinbox(right_col, from_=1, to=BULK_HARD_CAP, textvariable=self.count_var,
                                     width=10, bg=ENTRY_BG, fg=TEXT, relief="flat", font=("Consolas", 10))
        self.count_spin.pack(pady=6)

        tk.Label(right_col, text="Interval between sends (ms):", bg=BG, fg=MUTED, font=("Arial", 10)).pack(anchor="w")
        self.interval_var = tk.IntVar(value=100)
        self.interval_spin = tk.Spinbox(right_col, from_=0, to=10000, increment=50, textvariable=self.interval_var,
                                        width=10, bg=ENTRY_BG, fg=TEXT, relief="flat", font=("Consolas", 10))
        self.interval_spin.pack(pady=6)

        # Start test button
        self.bulk_btn = tk.Button(right_col, text="Start", command=self.on_start_bulk,
                                  bg="#2a9df4", fg="white", relief="flat", font=("Arial", 10, "bold"))
        self.bulk_btn.pack(pady=(8,6), ipadx=8, ipady=6)

        # Log and progress
        self.bulk_progress_label = tk.Label(right_col, text="Sent: 0/0", bg=BG, fg=MUTED, font=("Arial", 10))
        self.bulk_progress_label.pack(pady=(12, 6))

        self.bulk_log = tk.Text(right_col, bg="#071018", fg=TEXT, height=16, width=36, bd=0, font=("Consolas", 9))
        self.bulk_log.pack()

        # Watermark
        watermark = tk.Label(self, text="𝐵𝒴 𝒯𝒟𝒴", bg=BG, fg=MUTED, font=("Arial", 18, "italic"))
        watermark.place(relx=1.0, rely=1.0, anchor="se", x=-320, y=-530)

        # Hover effects
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg=BTN_HOVER))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=BTN_BG))
        self.bulk_btn.bind("<Enter>", lambda e: self.bulk_btn.config(bg="#5ab7ff"))
        self.bulk_btn.bind("<Leave>", lambda e: self.bulk_btn.config(bg="#2a9df4"))

    # ----------------------
    def _update_preview(self):
        pretty = json.dumps(self.payload, indent=2)
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", pretty)
        self.preview.configure(state="disabled")

    def edit_payload(self):
        txt = simpledialog.askstring("Edit JSON", "Modify payload JSON:",
                                     initialvalue=json.dumps(self.payload, indent=2))
        if txt is None:
            return
        try:
            parsed = json.loads(txt)
            self.payload = parsed
            self._update_preview()
            self._set_status("Payload updated", MUTED)
        except Exception as e:
            messagebox.showerror("Invalid JSON", str(e))

    def reset_payload(self):
        self.payload = {"content": "hi"}
        self._update_preview()
        self._set_status("Payload reset", MUTED)

    def _set_status(self, text, color):
        self.status.configure(text=text, fg=color)

    # ----------------------
    # Single send
    def on_send_single(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste the webhook/endpoint URL first.")
            return
        if not URL_REGEX.match(url):
            messagebox.showwarning("Invalid URL", "URL must be a discord url://")
            return



        if url not in self.recent:
            self.recent.appendleft(url)
            self._refresh_history()

        self.send_btn.configure(state="disabled", text="Sending…")
        self._set_status("Sending single message...", MUTED)

        def worker():
            ok_flag, msg = post_once(url, self.payload)
            def finish():
                self.send_btn.configure(state="normal", text="Send (single)")
                if ok_flag:
                    messagebox.showinfo("Success", "Message delivered.")
                    self._set_status(msg, SUCCESS)
                else:
                    messagebox.showerror("Failed", f"Send failed:\n{msg}")
                    self._set_status(msg, ERROR)
            self.after(20, finish)

        threading.Thread(target=worker, daemon=True).start()

    # ----------------------
    # Controlled bulk
    def on_start_bulk(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste the webhook")
            return
        if not URL_REGEX.match(url):
            messagebox.showwarning("Invalid URL", "URL must be a discord webhook://")
            return

        try:
            total = int(self.count_var.get())
        except Exception:
            messagebox.showerror("Invalid count", "Enter a valid number.")
            return

        if total < 1:
            messagebox.showerror("Invalid count", "Number must be >= 1.")
            return
        if total > BULK_HARD_CAP:
            messagebox.showwarning("Too many", f"The hard cap is {BULK_HARD_CAP}.")
            return

        if total > BULK_SAFE_THRESHOLD:
            confirm = simpledialog.askstring("Confirm",
                                             f"You requested {total} messages.\n"
                                             "Type CONFIRM to proceed:")
            if (confirm or "").strip().upper() != "CONFIRM":
                messagebox.showinfo("Aborted", "Bulk test aborted.")
                return

        ok = messagebox.askyesno("Confirm", "Are you sure")
        if not ok:
            return

        if url not in self.recent:
            self.recent.appendleft(url)
            self._refresh_history()

        self.bulk_log.configure(state="normal")
        self.bulk_log.delete("1.0", "end")
        self.bulk_log.insert("end", f"Starting controlled test: {total} messages\n")
        self.bulk_log.configure(state="disabled")
        self.bulk_progress_label.configure(text=f"Sent: 0/{total}")
        self.bulk_btn.configure(state="disabled")
        self.send_btn.configure(state="disabled")
        self._set_status("Running controlled test...", MUTED)

        interval_ms = max(0, int(self.interval_var.get()))

        def worker():
            for i in range(1, total + 1):
                ok_flag, msg = post_once(url, self.payload)
                timestamp = time.strftime("%H:%M:%S")
                line = f"[{timestamp}] {i}/{total}: {'OK' if ok_flag else 'FAIL'} - {msg}\n"
                def ui_update(line=line, i=i, ok_flag=ok_flag):
                    self.bulk_log.configure(state="normal")
                    self.bulk_log.insert("end", line)
                    self.bulk_log.see("end")
                    self.bulk_log.configure(state="disabled")
                    self.bulk_progress_label.configure(text=f"Sent: {i}/{total}")
                    self._set_status(f"Last: {'OK' if ok_flag else 'FAIL'} ({i}/{total})",
                                     SUCCESS if ok_flag else ERROR)
                self.after(1, ui_update)
                time.sleep(interval_ms / 1000.0)

            def finish_ui():
                self.bulk_btn.configure(state="normal")
                self.send_btn.configure(state="normal")
                self._set_status(f"Controlled test complete: {total} messages", SUCCESS)
            self.after(50, finish_ui)

        threading.Thread(target=worker, daemon=True).start()

    # ----------------------
    def _refresh_history(self):
        self.history.delete(0, "end")
        for u in self.recent:
            short = u if len(u) <= 60 else f"{u[:57]}..."
            self.history.insert("end", short)

    def use_selected_history(self, _ev=None):
        sel = self.history.curselection()
        if not sel:
            return
        idx = sel[0]
        url = list(self.recent)[idx]
        self.url_var.set(url)
        self._set_status("Loaded URL from history", MUTED)

# ----------------------
if __name__ == "__main__":
    app = VixerWebhookTester()
    app.mainloop()
