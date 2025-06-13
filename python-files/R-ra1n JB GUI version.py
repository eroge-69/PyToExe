import tkinter as tk
from tkinter import scrolledtext
import time
import threading
import random

# Fake jailbreak log messages
log_messages = [
    "[*] Initializing kernel patches...",
    "[*] Locating kernel base...",
    "[*] Bypassing code signing...",
    "[*] Injecting payload into trust cache...",
    "[*] Mounting root filesystem as rw...",
    "[*] Exploiting CVE-2025-1337...",
    "[*] Cleaning up...",
    "[✓] Jailbreak completed successfully!",
    "[🛈 ] Info: Tweak Loader installed ✅",
]

def type_log(text_widget, message, delay=0.03):
    for char in message:
        text_widget.insert(tk.END, char)
        text_widget.update()
        time.sleep(delay)
    text_widget.insert(tk.END, '\n')
    text_widget.see(tk.END)

def show_progress_bar(text_widget):
    bar_length = 30
    for i in range(bar_length + 1):
        bar = '=' * i + ' ' * (bar_length - i)
        text_widget.insert(tk.END, f"\r[{bar}] {int((i / bar_length) * 100)}%\n")
        text_widget.see(tk.END)
        text_widget.update()
        time.sleep(0.05)

def run_fake_jailbreak(text_widget, button):
    button.config(state=tk.DISABLED)
    text_widget.insert(tk.END, "\n🍏 R-ra1n Jailbreak iOS 17.0–18.4.1 v1.0\n")
    text_widget.insert(tk.END, "Device: iPhone Xs UK | Stikdebug is requred(): iOS 18.4.1\n\n")
    text_widget.see(tk.END)
    text_widget.update()

    time.sleep(0.8)
    text_widget.insert(tk.END, "[*] Bootstrapping exploit...\n")
    text_widget.see(tk.END)
    text_widget.update()

    show_progress_bar(text_widget)
    time.sleep(0.5)

    for msg in log_messages:
        type_log(text_widget, msg, delay=0.02)
        time.sleep(random.uniform(0.3, 0.8))

    text_widget.insert(tk.END, "\n[⟳] Respringing device...\n")
    text_widget.insert(tk.END, "✔️ Done. R-ra1n Loader now on home screen. Enjoy! 😎\n")
    text_widget.see(tk.END)
    button.config(state=tk.NORMAL, text="✔️ Jailbroken")

def start_jailbreak(text_widget, button):
    threading.Thread(target=run_fake_jailbreak, args=(text_widget, button), daemon=True).start()

# --- GUI Setup ---
window = tk.Tk()
window.title("R-ra1n Jailbreak")
window.geometry("600x400")
window.configure(bg="black")

title_label = tk.Label(window, text="R-ra1n Jailbreak", font=("Courier", 18), fg="lime", bg="black")
title_label.pack(pady=10)

log_box = scrolledtext.ScrolledText(window, width=70, height=15, font=("Courier", 10), bg="black", fg="lime", insertbackground="lime")
log_box.pack(padx=10, pady=10)

jailbreak_button = tk.Button(window, text="🔓 Start Jailbreak", font=("Courier", 12), bg="lime", fg="black", command=lambda: start_jailbreak(log_box, jailbreak_button))
jailbreak_button.pack(pady=10)

window.mainloop()
