import tkinter as tk
from tkinter import messagebox
import time

# === CONFIG ===
UNLOCK_CODE = "1234"
COUNTDOWN = 600  # 10 minutes
FAKE_WALLET = "1FakeBitcoinAddressForDemoOnly1234567890"
FAKE_EMAIL = "unlock@opsecmail.com"

# === MAIN WINDOW ===
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="#2d2d2d")  # WannaCry gray
root.overrideredirect(True)

# === LEFT PANEL ===
left_frame = tk.Frame(root, width=400, bg="#b00000")
left_frame.pack(side="left", fill="y")

# Lock icon (Unicode padlock)
tk.Label(left_frame, text="🔒", font=("Segoe UI", 100), fg="white", bg="#b00000").pack(pady=20)
tk.Label(left_frame, text="Ooops, your files have been encrypted!", font=("Segoe UI", 20, "bold"), fg="white", bg="#b00000", wraplength=380, justify="center").pack(pady=20)

# === RIGHT PANEL ===
right_frame = tk.Frame(root, bg="#2d2d2d")
right_frame.pack(side="right", expand=True, fill="both", padx=40)

main_text = (
    "What happened to my computer?\n\n"
    "Your important files are encrypted.\nMany of your documents, photos, videos, databases and other files are no longer accessible because they have been encrypted.\n\n"
    "Maybe you are busy looking for a way to recover your files, but don't waste your time.\nNobody can recover your files without our decryption service.\n\n"
    "Can I recover my files?\n\n"
    "Sure. We guarantee that you can recover all your files safely and easily.\nBut you have not so enough time.\n\n"
    "You can decrypt some of your files for free. Try now by clicking <Decrypt>.\nBut if you want to decrypt all your files, you need to pay.\n\n"
    "Payment information\n\n"
    f"Send $300 worth of Bitcoin to this address:\n{FAKE_WALLET}\n\n"
    "After payment, send your transaction ID and system ID to:\n"
    f"{FAKE_EMAIL}\n\n"
    "If you do not pay within 3 days, your files will be permanently deleted.\nIf you pay, all your files will be restored.\n\n"
    "Time left until permanent deletion:"
    "MADE MY OPSEC.\n\n"
)

tk.Label(right_frame, text=main_text, font=("Segoe UI", 12), fg="white", bg="#2d2d2d", justify="left", anchor="nw").pack(anchor="ne", pady=20)

# === COUNTDOWN TIMER ===
countdown_label = tk.Label(right_frame, text="", font=("Segoe UI", 14, "bold"), fg="yellow", bg="#2d2d2d")
countdown_label.pack(anchor="ne", pady=10)

def update_countdown():
    global COUNTDOWN
    if COUNTDOWN > 0:
        mins, secs = divmod(COUNTDOWN, 60)
        countdown_label.config(text=f"{mins:02d}:{secs:02d}")
        COUNTDOWN -= 1
        root.after(1000, update_countdown)
    else:
        countdown_label.config(text="00:00 — Files locked permanently.")

# === ENTRY FIELD ===
tk.Label(right_frame, text="Enter unlock code:", font=("Segoe UI", 12), fg="white", bg="#2d2d2d").pack(anchor="ne", pady=5)

entry = tk.Entry(right_frame, font=("Segoe UI", 14), fg="white", bg="black", insertbackground="white", justify="center")
entry.pack(anchor="ne", pady=5)

def check_code(event=None):
    if entry.get() == UNLOCK_CODE:
        messagebox.showinfo("Access Granted", "System unlocked.")
        root.destroy()
    else:
        messagebox.showerror("Access Denied", "Incorrect code.")
        entry.delete(0, tk.END)

entry.bind("<Return>", check_code)
entry.focus()

# === START ===
update_countdown()
root.mainloop()
