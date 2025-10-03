Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
python protector.py

SyntaxError: invalid syntax
import tkinter as tk
from tkinter import simpledialog, messagebox

# Set password
CORRECT_PASSWORD = "2525"

# Create main window
root = tk.Tk()
... root.attributes("-fullscreen", True)   # Fullscreen
... root.configure(bg="white")
... 
... # Get screen size
... screen_width = root.winfo_screenwidth()
... screen_height = root.winfo_screenheight()
... 
... canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="white", highlightthickness=0)
... canvas.pack(fill="both", expand=True)
... 
... # Function to draw scalable heart
... def draw_heart(cx, cy, size):
...     offset = size // 2
...     canvas.create_polygon(
...         cx, cy,             # bottom point
...         cx - offset, cy - offset,  # left top
...         cx, cy - size,      # top
...         cx + offset, cy - offset,  # right top
...         cx, cy,             # back to bottom
...         fill="red", outline="red"
...     )
...     canvas.create_line(cx, cy, cx, cy + size, fill="red", width=3)  # balloon string
... 
... # Draw heart in center of screen
... draw_heart(screen_width//2, screen_height//2, 200)
... 
... # Password prompt
... def ask_password():
...     pwd = simpledialog.askstring("Password Required", "Enter Password:", show="*")
...     if pwd == CORRECT_PASSWORD:
...         root.destroy()
...     else:
...         messagebox.showerror("Error", "Wrong Password")
...         ask_password()
... 
... root.after(500, ask_password)
