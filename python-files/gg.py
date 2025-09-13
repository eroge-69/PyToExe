import tkinter as tk
from tkinter import messagebox, scrolledtext

# === DARK MODE SETTINGS ===
DARK_BG = "#1e1e1e"
DARK_FG = "#e0e0e0"
ENTRY_BG = "#2b2b2b"
ENTRY_FG = "#ffffff"
BUTTON_BG = "#228B22"
BUTTON_ACTIVE = "#32CD32"
FONT = ("Segoe UI", 10)

root = tk.Tk()
root.title("Discord Nuker </>HeshaN ModZ")
root.configure(bg=DARK_BG)

# === Disable resizing and maximize, keep minimize ===
root.resizable(False, False)
root.attributes('-toolwindow', True)  # Windows only: removes maximize but keeps minimize

# === Optional: Center the window on screen ===
window_width = 700
window_height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))
root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

# === GUI Elements ===

def style_widget(widget):
    widget.configure(bg=DARK_BG, fg=DARK_FG, font=FONT)

def style_entry(widget):
    widget.configure(bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG, font=FONT, relief="flat")

def style_button(widget):
    widget.configure(bg=BUTTON_BG, fg="#fff", activebackground=BUTTON_ACTIVE, activeforeground="#fff", font=FONT, relief="flat", cursor="hand2")

tk.Label(root, text="Token", bg=DARK_BG, fg=DARK_FG, font=FONT).grid(row=0, column=0, sticky="w", padx=5, pady=5)
token_entry = tk.Entry(root, width=60)
token_entry.grid(row=0, column=1, columnspan=2, pady=5, padx=5)
style_entry(token_entry)

tk.Label(root, text="Server Name", bg=DARK_BG, fg=DARK_FG, font=FONT).grid(row=1, column=0, sticky="w", padx=5, pady=5)
server_entry = tk.Entry(root, width=30)
server_entry.grid(row=1, column=1, pady=5, sticky="w")
style_entry(server_entry)

tk.Label(root, text="Message", bg=DARK_BG, fg=DARK_FG, font=FONT).grid(row=2, column=0, sticky="w", padx=5, pady=5)
msg_entry = tk.Entry(root, width=30)
msg_entry.grid(row=2, column=1, pady=5, sticky="w")
style_entry(msg_entry)

output_box = scrolledtext.ScrolledText(root, height=20, width=80, bg="#121212", fg="#00FF00", insertbackground="#00FF00", font=("Consolas", 10), relief="flat")
output_box.grid(row=4, column=0, columnspan=3, pady=10, padx=5)

def log(msg):
    output_box.insert(tk.END, msg + "\n")
    output_box.see(tk.END)

# === Dummy placeholder functions ===
def disable_account(token, log):
    log(f"Disabling account with token: {token}")

def nuke_account(token, server, message, log):
    log(f"Nuking server '{server}' with token: {token} and message: {message}")

def nuke_webhooks(filename, log):
    log(f"Nuking webhooks listed in: {filename}")

btn_disable = tk.Button(root, text="Run Account Disabler", command=lambda: disable_account(token_entry.get(), log))
btn_disable.grid(row=3, column=0, pady=10, padx=5)
style_button(btn_disable)

btn_nuke = tk.Button(root, text="Run Nuker", command=lambda: nuke_account(token_entry.get(), server_entry.get(), msg_entry.get(), log))
btn_nuke.grid(row=3, column=1, pady=10, padx=5)
style_button(btn_nuke)

btn_webhook = tk.Button(root, text="Webhook Nuke (webhooks.txt)", command=lambda: nuke_webhooks("webhooks.txt", log))
btn_webhook.grid(row=3, column=2, pady=10, padx=5)
style_button(btn_webhook)

root.mainloop()
