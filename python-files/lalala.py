import tkinter as tk
import threading
import time
import sys

# Config (tweak timings and fonts here)
HELLO_DURATION = 1.5   # seconds before showing the second text
SECOND_DURATION = 1.2  # seconds before showing fake BSOD
BSOD_DURATION = 6.0    # seconds to keep fake BSOD on screen (0 = until user presses ESC)
HELLO_FONT_SIZE = 72
SECOND_FONT_SIZE = 36

def center_window(win, w, h):
    win.update_idletasks()
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def show_messages_then_bsod():
    # Popup window with messages
    root = tk.Tk()
    root.title("Message")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    # Small window size (but scaled for readability)
    w, h = 900, 300
    center_window(root, w, h)

    # Use a frame with transparent-ish background (platform dependent)
    frame = tk.Frame(root, bg="black")
    frame.pack(fill="both", expand=True)

    hello_label = tk.Label(frame,
                           text="HELLO WORLD",
                           font=("Segoe UI", HELLO_FONT_SIZE, "bold"),
                           fg="white",
                           bg="black")
    hello_label.pack(side="bottom", pady=10)

    second_label = tk.Label(frame,
                            text="",
                            font=("Segoe UI", SECOND_FONT_SIZE),
                            fg="white",
                            bg="black")
    # place above the hello_label
    second_label.pack(side="top", pady=5)

    # allow quick quit by pressing Escape or closing
    def on_escape(event=None):
        try:
            root.destroy()
        except:
            pass
    root.bind("<Escape>", on_escape)

    def sequence():
        time.sleep(HELLO_DURATION)
        # show second text above
        second_label.config(text="nvm bro I hate you")
        time.sleep(SECOND_DURATION)
        try:
            root.destroy()
        except:
            pass
        time.sleep(0.15)
        show_fake_bsod()

    threading.Thread(target=sequence, daemon=True).start()
    root.mainloop()

def show_fake_bsod():
    # Fullscreen fake blue screen
    bsod = tk.Tk()
    bsod.title(" ")
    bsod.attributes("-fullscreen", True)
    bsod.attributes("-topmost", True)
    bsod.configure(bg="#0100A6")  # deep blue; adjust if you like

    # Close on ESC (so it's easy to recover)
    def close_bsod(event=None):
        try:
            bsod.destroy()
        except:
            pass
    bsod.bind("<Escape>", close_bsod)
    # Also close on any mouse click or keypress
    bsod.bind("<Button>", close_bsod)
    bsod.bind("<Key>", close_bsod)

    # Compose BSOD-like text. This is only cosmetic.
    big_text = tk.Label(bsod,
                        text=":(\nYour PC ran into a problem and needs to restart.",
                        font=("Segoe UI", 36),
                        fg="white",
                        bg="#0100A6",
                        justify="left")
    big_text.pack(anchor="nw", padx=60, pady=60)

    detail_lines = [
        "A problem has been detected and Windows has been shut down to prevent damage",
        "to your computer.",
        "",
        "If this is the first time you've seen this stop error screen,",
        "restart your computer. If this screen appears again, follow",
        "these steps to troubleshoot the issue.",
        "",
        "Collecting data for crash dump ...",
        "Initializing memory dump ...",
        "",
        "For more information, visit: https://support.microsoft.com",
        "If you call a support person, give them this info:",
        "Stop code: FAKE_FAULT_DEMO"
    ]
    details = tk.Label(bsod,
                       text="\n".join(detail_lines),
                       font=("Consolas", 16),
                       fg="white",
                       bg="#0100A6",
                       justify="left")
    details.pack(anchor="nw", padx=60, pady=(20,0))

    # Optional: make sure it's topmost on Windows (may require this attribute)
    try:
        bsod.attributes("-topmost", True)
    except Exception:
        pass

    if BSOD_DURATION > 0:
        def auto_close():
            time.sleep(BSOD_DURATION)
            try:
                bsod.destroy()
            except:
                pass
        threading.Thread(target=auto_close, daemon=True).start()

    bsod.mainloop()

if __name__ == "__main__":
    # Quick confirmation prompt on console so user knows it's harmless
    print("This script displays messages and a fake blue-screen window. It will NOT crash your computer.")
    if sys.platform.startswith("win") or sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        show_messages_then_bsod()
    else:
        print("Unsupported platform for this demo.")