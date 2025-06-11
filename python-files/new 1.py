import tkinter as tk

def copy_to_clipboard(text):
    r = tk.Tk()
    r.withdraw()  # Hide the main window
    r.clipboard_clear()
    r.clipboard_append(text)
    r.update()  # Now it stays on the clipboard after the window is closed
    r.destroy()

# Example usage
copy_to_clipboard("Hello, this is the text to copy!")
print("Text copied to clipboard.")
