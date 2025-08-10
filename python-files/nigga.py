# prank_fullscreen_typing.py
# Harmless visual-only prank. DO NOT run on someone else's machine without permission.

import tkinter as tk
import tkinter.font as tkFont
import sys

TEXT = (
    "YOUR IMPORTANT FILES ARE ENCRYPTED...\n"
    "SEND 120€ TO THIS BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n"
    "YOUR PC WILL NOT WORK UNTIL YOU SEND MONEY (ATC:823)\n"
    "MADE BY VLADKY"
)

TYPING_DELAY_MS = 40          # ms per character (smaller => faster)
AUTO_CLOSE_AFTER_FULL_MS = 9000  # auto-close N ms after typing finishes

def reveal_and_close(event=None):
    print("reveal_and_close called", file=sys.stderr)
    try:
        root.destroy()
    except Exception:
        pass

def on_key(event):
    # debug print to console so you can see keys received
    print("Key pressed:", event.keysym, file=sys.stderr)
    if event.keysym in ("Return", "Escape"):
        reveal_and_close()

def type_step(i=0, cursor_on=True):
    # if typing not finished, show substring + blinking cursor
    if i <= len(TEXT):
        disp = TEXT[:i]
        if i < len(TEXT):
            disp += ("|" if cursor_on else " ")  # blinking cursor while typing
        label.config(text=disp)
        # schedule next character (toggle cursor boolean to blink)
        root.after(TYPING_DELAY_MS, type_step, i+1, not cursor_on)
    else:
        # finished typing: show final text (no cursor) and schedule auto-close
        label.config(text=TEXT)
        root.after(AUTO_CLOSE_AFTER_FULL_MS, reveal_and_close)

# --- Setup window ---
root = tk.Tk()
root.withdraw()  # hide while we configure

# compute full-screen geometry
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.geometry(f"{screen_w}x{screen_h}+0+0")

# remove window decorations and set on-top
root.overrideredirect(True)
root.wm_attributes("-topmost", True)

# create label (centered, wrapped)
font = tkFont.Font(family="Consolas", size=36, weight="bold")
label = tk.Label(root, text="", fg="red", bg="black", font=font, justify="center", wraplength=screen_w-100)
label.pack(expand=True, fill="both")

# show window and try to force focus so key bindings work
root.deiconify()
root.update_idletasks()
root.lift()
root.focus_force()   # try to force keyboard focus to this window

# bind keys AFTER trying to focus
root.bind_all("<Key>", on_key)

# small safety: also bind Return/Escape specifically
root.bind_all("<Return>", reveal_and_close)
root.bind_all("<Escape>", reveal_and_close)

# start typing after short delay
root.after(250, type_step)

# fallback auto-close in case typing/auto-close logic fails
root.after(30_000, reveal_and_close)  # hard timeout 30s

print("Prank started. Press Enter or Escape to close (or wait).", file=sys.stderr)
root.mainloop()
