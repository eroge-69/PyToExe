# fancy_exe_maker_glass.py
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys

# --- Frosted Glass Effect (Windows Specific) ---
# We use the ctypes library to interact with Windows APIs
import ctypes
from ctypes import wintypes

def apply_glass_effect(window_handle):
    """Applies the frosted glass (acrylic) effect to a window."""
    try:
        # This part is specific to Windows 11/10 APIs
        user32 = ctypes.windll.user32
        
        # Define constants for window composition attributes
        WCA_ACCENT_POLICY = 19
        ACCENT_ENABLE_ACRYLICBLURBEHIND = 4 # A modern blur effect

        # Define the data structures needed for the API call
        class ACCENTPOLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_uint),
                ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_uint)
            ]

        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_uint),
                ("Data", ctypes.POINTER(ACCENTPOLICY)),
                ("SizeOfData", ctypes.c_size_t)
            ]

        # Set up the policy for the acrylic blur effect
        accent = ACCENTPOLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.GradientColor = (0x990000) # Slightly transparent, can be fine-tuned

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.SizeOfData = ctypes.sizeof(accent)
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ACCENTPOLICY))

        # Apply the effect to the window
        user32.SetWindowCompositionAttribute(window_handle, ctypes.pointer(data))

    except (AttributeError, TypeError):
        # This will fail on non-Windows systems, so we just ignore the error.
        # The app will run with a solid color background instead.
        print("Glass effect not supported on this OS. Using solid color.")


# ---------- Functions ----------
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[
        ("Python files", ("*.py", "*.pyw")),
        ("All files", "*.*")
    ])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def create_exe():
    py_file = file_entry.get()
    if not os.path.isfile(py_file):
        messagebox.showerror("Error", "Please select a valid Python file.")
        return
    
    save_path = filedialog.askdirectory()
    if not save_path:
        return

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed", # Creates a GUI app without a console
        "--distpath",
        save_path,
        py_file
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        messagebox.showinfo("Success", f"EXE created successfully in:\n{save_path}")
    except subprocess.CalledProcessError as e:
        error_message = f"Failed to create EXE.\n\nError:\n{e.stderr}"
        messagebox.showerror("Error", error_message)
    except FileNotFoundError:
        messagebox.showerror("Error", "Could not find PyInstaller. Is it installed in your Python environment?")

# ---------- GUI Setup ----------
# Main Colors
BG_COLOR = "#daf7f6"
TEXT_COLOR = "#1f2937" # Dark gray for readability
ACCENT_COLOR_1 = "#3b82f6" # A nice blue for buttons
ACCENT_COLOR_2 = "#ef4444" # A red for the main action button
ENTRY_BG_COLOR = "#ffffff"
ENTRY_TEXT_COLOR = "#000000"

root = tk.Tk()
root.title("Glass EXE Maker ✨")
root.geometry("500x320")

# --- Applying the Glass Effect ---
# Make the root window background a color that Windows can make transparent (like black)
# The widgets we place on top will have our desired BG_COLOR
root.config(bg='black') 

# Make the window transparent (this is necessary for the glass effect)
# On Windows 11, the DWM handles the blur, so full transparency is not needed
root.attributes("-alpha", 0.95)

# After the window appears, apply the glass effect using its handle
def on_map(event):
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    apply_glass_effect(hwnd)
    # Remove the binding so it doesn't fire again
    root.unbind("<Map>")

root.bind("<Map>", on_map)


# A main frame with the desired background color that covers the whole window
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True)


# Fonts
font_title = ("Segoe UI", 16, "bold")
font_label = ("Segoe UI", 11)
font_button = ("Segoe UI", 10, "bold")

# Title
tk.Label(main_frame, text="Python → EXE Maker", font=font_title, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)

# File selection
frame_file = tk.Frame(main_frame, bg=BG_COLOR)
frame_file.pack(pady=10, padx=20, fill="x")
file_entry = tk.Entry(
    frame_file, 
    width=40, 
    font=font_label, 
    bg=ENTRY_BG_COLOR, 
    fg=ENTRY_TEXT_COLOR, 
    insertbackground=ENTRY_TEXT_COLOR, # Cursor color
    relief="solid",
    bd=1,
    highlightthickness=1,
    highlightcolor="#cccccc"
)
file_entry.pack(side="left", expand=True, fill="x", padx=5, ipady=4)
tk.Button(
    frame_file, 
    text="Browse", 
    command=select_file, 
    font=font_button, 
    bg=ACCENT_COLOR_1, 
    fg="#ffffff", 
    activebackground="#2563eb",
    relief="flat",
    padx=10
).pack(side="left")

# Create EXE button
tk.Button(
    main_frame, 
    text="Create EXE", 
    command=create_exe, 
    font=font_button, 
    bg=ACCENT_COLOR_2, 
    fg="#ffffff", 
    activebackground="#dc2626",
    relief="flat",
    width=20,
    pady=5
).pack(pady=25, ipady=5)

# Info label
tk.Label(main_frame, text="Select a .py or .pyw file to convert", font=("Segoe UI", 9), bg=BG_COLOR, fg="#6b7280").pack(pady=5)

# Keep window on top (optional)
root.attributes("-topmost", True)

root.mainloop()