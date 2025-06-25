import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import os
import sys
import signal
import atexit
import tempfile  # برای استفاده از دایرکتوری موقت سیستم
import time

BOT_FILE = "bot_main.py"

class SingleInstance:
    def __init__(self):
        # فایل لاک در دایرکتوری موقت سیستم قرار می‌گیرد
        self.lockfile = os.path.join(tempfile.gettempdir(), "bot_gui.lock")
        
        # بررسی وجود فایل لاک و اطمینان از اجرای تنها یک نسخه از برنامه
        if os.path.exists(self.lockfile):
            messagebox.showerror("Error", "Another instance is already running.")
            sys.exit(0)

        # ایجاد فایل لاک جدید برای این نسخه از برنامه
        with open(self.lockfile, 'w') as f:
            f.write(str(os.getpid()))

        atexit.register(self.release)

    def release(self):
        try:
            if os.path.exists(self.lockfile):
                os.remove(self.lockfile)
        except Exception as e:
            print(f"Error while removing lock file: {e}")

class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Bot Controller")
        self.root.configure(bg="#121212")
        self.bot_process = None
        self.is_running = False

        font_button = ("Segoe UI", 16, "bold")
        font_log = ("Consolas", 14)

        frame_buttons = tk.Frame(root, bg="#121212")
        frame_buttons.pack(pady=(20,10), padx=20, fill="x")

        self.start_button = tk.Button(
            frame_buttons,
            text="🚀 Start Bot",
            command=self.toggle_bot,
            bg="#1E88E5", fg="white",
            activebackground="#1565C0",
            font=font_button,
            bd=0,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.start_button.pack(side="left", expand=True, fill="x", padx=(0,10))

        self.clear_button = tk.Button(
            frame_buttons,
            text="🧹 Clear Log",
            command=self.clear_log,
            bg="#757575", fg="white",
            activebackground="#494949",
            font=font_button,
            bd=0,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.clear_button.pack(side="left", expand=True, fill="x")

        self.log_box = scrolledtext.ScrolledText(
            root,
            width=90, height=25,
            bg="#1E1E1E", fg="white", insertbackground="white",
            font=font_log,
            bd=0,
            relief="sunken",
            padx=10, pady=10,
            wrap="word",
            state="disabled"
        )
        self.log_box.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # تعریف تگ رنگ‌ها با پس‌زمینه و متن
        self.log_box.tag_config("user_msg", foreground="#000000", background="#90EE90")   # LightGreen bg, black text
        self.log_box.tag_config("start", foreground="#000000", background="#87CEFA")      # LightSkyBlue bg, black text
        self.log_box.tag_config("stop", foreground="#FFFFFF", background="#F08080")       # LightCoral bg, white text
        self.log_box.tag_config("error", foreground="#FFFFFF", background="#CD5C5C")      # IndianRed bg, white text
        self.log_box.tag_config("system", foreground="#000000", background="#DCDCDC")     # Gainsboro bg, black text

        self.log("📋 Bot logs will appear here...\n", tag="system")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_bot(self):
        if self.is_running:
            self.stop_bot()
        else:
            self.start_bot()

    def start_bot(self):
        if not os.path.exists(BOT_FILE):
            messagebox.showerror("Error", f"File '{BOT_FILE}' not found!")
            return

        self.log("✅ Bot is starting...", tag="start")
        self.is_running = True
        self.start_button.config(text="🛑 Stop Bot", bg="#E53935", activebackground="#B71C1C")

        def run():
            try:
                self.bot_process = subprocess.Popen(
                    [sys.executable, BOT_FILE],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                for line in self.bot_process.stdout:
                    line = line.strip()
                    if line.startswith("MSG_FROM:"):
                        parts = line.split(":", 2)
                        if len(parts) == 3:
                            user_id, msg = parts[1], parts[2]
                            self.log(f"🗨️ Message from [{user_id}]: {msg}", tag="user_msg")
                        else:
                            self.log(line, tag="system")
                    elif re.search(r"(error|fail|crash|exception|traceback)", line, re.I):
                        self.log(line, tag="error")
                    else:
                        self.log(line, tag="system")
                self.bot_process.wait()
            except Exception as e:
                self.log(f"❌ Error running bot:\n{e}", tag="error")
            finally:
                self.is_running = False
                self.start_button.config(text="🚀 Start Bot", bg="#1E88E5", activebackground="#1565C0")
                self.log("⛔ Bot stopped.", tag="stop")

        threading.Thread(target=run, daemon=True).start()

    def stop_bot(self):
        if self.bot_process:
            self.log("🛑 Stopping bot...", tag="stop")
            try:
                if os.name == 'nt':
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.bot_process.pid)])
                else:
                    os.killpg(os.getpgid(self.bot_process.pid), signal.SIGTERM)
            except Exception as e:
                self.log(f"⚠️ Error stopping bot: {e}", tag="error")
            self.bot_process = None
            self.is_running = False
            self.start_button.config(text="🚀 Start Bot", bg="#1E88E5", activebackground="#1565C0")
            self.log("⛔ Bot stopped.", tag="stop")

    def log(self, message, tag=None):
        self.log_box.configure(state='normal')
        if tag:
            self.log_box.insert(tk.END, f"{message}\n", tag)
        else:
            self.log_box.insert(tk.END, f"{message}\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state='disabled')

    def clear_log(self):
        self.log_box.configure(state='normal')
        self.log_box.delete('1.0', tk.END)
        self.log_box.configure(state='disabled')

    def on_closing(self):
        if self.is_running:
            self.stop_bot()
        self.log("🛑 Application closing...", tag="stop")
        single_instance.release()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    single_instance = SingleInstance()
    root = tk.Tk()
    root.geometry("900x650")
    root.minsize(750, 550)
    gui = BotGUI(root)
    root.mainloop()
