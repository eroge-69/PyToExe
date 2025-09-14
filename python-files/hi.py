# kiosk_black.py
import tkinter as tk

def on_alt_e(event=None):
    """Exit handler bound to Alt+E."""
    root.destroy()

def ignore_close():
    """Called when the window manager requests a close (e.g. clicking X). Do nothing."""
    pass  # intentionally ignore

def block_alt_f4(event):
    """Prevent Alt+F4 from closing the window inside Tkinter."""
    return "break"  # stops further handling of the event

root = tk.Tk()

# Make window fullscreen (works cross-platform)
root.attributes("-fullscreen", True)

# Remove window decorations on some platforms (useful in kiosk)
root.overrideredirect(False)  # set True to remove decorations entirely; False keeps some behaviors
# If you want to totally hide decorations you can try: root.overrideredirect(True)
# but be careful: that will also remove any built-in ability to move/resize the window.

# Solid black background
root.configure(bg="black")

# Disable the window manager close (clicking X / programmatic WM_DELETE)
root.protocol("WM_DELETE_WINDOW", ignore_close)

# Prevent Alt+F4 from closing the Tk window (Tk-level)
root.bind_all("<Alt-F4>", block_alt_f4)

# Bind Alt+E to exit (both lowercase/uppercase)
root.bind_all("<Alt-e>", on_alt_e)
root.bind_all("<Alt-E>", on_alt_e)

# Optional: show a tiny hint only visible to admins if needed (comment out for true kiosk)
hint = tk.Label(root, text="(DM edyblox on discord to learn how to close this!)", bg="black", fg="white", font=("Helvetica", 10))
# place it where it won't be visible to most users, or remove entirely:
hint.place(relx=0.99, rely=0.99, anchor="se")

# Prevent the window from being resized
root.resizable(False, False)

# Keep the window on top (attempt; users can override at OS level)
root.attributes("-topmost", True)

root.mainloop()
