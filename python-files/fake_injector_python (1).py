import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

# Fake Injection Logic
def start_injection():
    inject_button.config(state='disabled')
    log_box.delete(1.0, tk.END)
    logs = [
        "[INFO] Connecting to VRChat process...",
        "[INFO] Bypassing anti-cheat...",
        "[INFO] Loading DLL...",
        "[INFO] Injecting into memory...",
        "[INFO] Finalizing injection...",
        "[SUCCESS] Injection completed successfully!"
    ]

    def run_logs():
        for i, log in enumerate(logs):
            log_box.insert(tk.END, log + "\n")
            progress_var.set((i+1)*100//len(logs))
            root.update_idletasks()
            time.sleep(1.2)
        messagebox.showinfo("Success", "Injection completed successfully!")
        inject_button.config(state='normal')
        open_feature_ui()

    threading.Thread(target=run_logs).start()

def open_feature_ui():
    feature_window = tk.Toplevel(root)
    feature_window.title("Injected Features")
    feature_window.geometry("400x300")
    feature_window.configure(bg="black")

    title = tk.Label(feature_window, text="Features Enabled", fg="white", bg="black", font=("Consolas", 14, "bold"))
    title.pack(pady=10)

    features = ["Fly", "Spin Bot", "Third Person"]
    colors = ["red", "orange", "yellow", "green", "blue", "purple"]

    for i, feature in enumerate(features):
        label = tk.Label(feature_window, text=feature, font=("Consolas", 16, "bold"))
        label.pack(pady=10)
        animate_rainbow(label, colors)

def animate_rainbow(widget, colors, index=0):
    widget.config(fg=colors[index])
    widget.after(300, lambda: animate_rainbow(widget, colors, (index+1)%len(colors)))

# Main Window
root = tk.Tk()
root.title("VRChat Injector")
root.geometry("500x400")
root.configure(bg="black")

# Title Label
title = tk.Label(root, text="VRChat Injector", fg="white", bg="black", font=("Consolas", 16, "bold"))
title.pack(pady=10)

# DLL Path Entry
dll_label = tk.Label(root, text="DLL Path:", fg="white", bg="black")
dll_label.pack()
dll_entry = tk.Entry(root, width=50)
dll_entry.insert(0, "C:/Users/SkidGang/VRChatHack.dll")
dll_entry.pack(pady=5)

# Process Selection
process_label = tk.Label(root, text="Select Process:", fg="white", bg="black")
process_label.pack()
process_combo = ttk.Combobox(root, values=["VRChat.exe", "GameOverlayUI.exe"])
process_combo.current(0)
process_combo.pack(pady=5)

# Inject Button
inject_button = tk.Button(root, text="Inject", bg="red", fg="white", command=start_injection)
inject_button.pack(pady=10)

# Progress Bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, maximum=100, length=400, variable=progress_var)
progress_bar.pack(pady=10)

# Log Box
log_box = tk.Text(root, width=60, height=10, bg="black", fg="lime", state='normal')
log_box.pack(pady=10)

root.mainloop()
