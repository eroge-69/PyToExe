import tkinter as tk
from tkinter import ttk
import winsound

# Keep track of all error windows so we can close them later
error_windows = []

def show_error_window(count):
    winsound.MessageBeep(winsound.MB_ICONHAND)

    win = tk.Toplevel()
    win.title("Error")
    win.geometry("300x120")
    win.resizable(False, False)
    win.attributes('-topmost', True)

    # Staggered placement for meme effect
    x = 100 + (count * 10) % 400
    y = 100 + (count * 10) % 300
    win.geometry(f"+{x}+{y}")

    icon_label = tk.Label(win, text="🥶", font=("Segoe UI Emoji", 32))
    icon_label.pack(side="left", padx=(20, 10), pady=20)

    msg_label = tk.Label(win, text="error", font=("Tahoma", 11))
    msg_label.pack(anchor="w", pady=20)

    ok_btn = tk.Button(win, text="OK", width=10, command=win.destroy)
    ok_btn.pack(side="bottom", pady=10)

    win.lift()
    win.attributes('-topmost', True)

    error_windows.append(win)

def start_error_sequence(count=0):
    if count < 35:
        show_error_window(count)
        if count == 0:
            root.after(1000, lambda: start_error_sequence(count + 1))
        elif count == 1:
            root.after(1000, lambda: start_error_sequence(count + 1))
        else:
            root.after(200, lambda: start_error_sequence(count + 1))
    else:
        # After all error windows created, wait 2 seconds then show antivirus popup
        root.after(2000, show_antivirus_popup)

def close_all_errors():
    for w in error_windows:
        if w.winfo_exists():
            w.destroy()
    error_windows.clear()

def on_antivirus_no():
    # Show the "Replace this text with your text." popup
    popup = tk.Toplevel()
    popup.title("Message")
    popup.geometry("300x100")
    popup.resizable(False, False)
    popup.attributes('-topmost', True)

    label = tk.Label(popup, text="Replace this text with your text.", font=("Tahoma", 11))
    label.pack(pady=20)

    ok_btn = tk.Button(popup, text="OK", width=10, command=popup.destroy)
    ok_btn.pack(pady=5)

    popup.lift()
    popup.attributes('-topmost', True)

def on_antivirus_yes():
    # Close all error windows and the main window, then quit
    close_all_errors()
    root.destroy()

def show_antivirus_popup():
    # Popup with "Virus Detected! Fix? [y] [n]"
    popup = tk.Toplevel()
    popup.title("ur antivirus")
    popup.geometry("350x130")
    popup.resizable(False, False)
    popup.attributes('-topmost', True)

    label = tk.Label(popup, text="Virus Detected! Fix?", font=("Tahoma", 12, "bold"))
    label.pack(pady=15)

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=5)

    yes_btn = tk.Button(btn_frame, text="[y]", width=8, command=lambda: [popup.destroy(), on_antivirus_yes()])
    yes_btn.pack(side="left", padx=10)

    no_btn = tk.Button(btn_frame, text="[n]", width=8, command=lambda: [popup.destroy(), on_antivirus_no()])
    no_btn.pack(side="left", padx=10)

    popup.lift()
    popup.attributes('-topmost', True)

def update_progress(current=0.0):
    if current <= 100:
        progress['value'] = current
        if current >= 50 and not halfway_triggered[0]:
            root.title("downwoading mowe viwuses")
            halfway_triggered[0] = True
        root.after(1, update_progress, current + 0.01)
    else:
        progress.pack_forget()
        root.title("wouve been haked")
        root.after(1000, lambda: [root.withdraw(), start_error_sequence()])

root = tk.Tk()
root.title("towtowwy downwoading viwus")
root.geometry("400x100")
root.resizable(False, False)

progress = ttk.Progressbar(root, orient="horizontal", length=350, mode="determinate")
progress.pack(pady=30)
progress['maximum'] = 100

halfway_triggered = [False]

root.after(0, update_progress)
root.mainloop()