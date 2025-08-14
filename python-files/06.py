import struct
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD  # pip install tkinterdnd2

def check_gif_interlacing(filepath):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except Exception as e:
        return f"Error reading file: {e}"

    if not (data.startswith(b"GIF87a") or data.startswith(b"GIF89a")):
        return "Not a valid GIF file"

    offset = 13
    packed_field = data[10]
    global_color_table_flag = (packed_field & 0x80) >> 7
    if global_color_table_flag:
        gct_size = 3 * (2 ** ((packed_field & 0x07) + 1))
        offset += gct_size

    while offset < len(data):
        block_id = data[offset]
        offset += 1
        if block_id == 0x2C:
            offset += 8
            packed = data[offset]
            interlace_flag = (packed & 0x40) >> 6
            return "Interlaced" if interlace_flag else "Non-Interlaced"
        elif block_id == 0x21:
            offset += 1
            while True:
                block_size = data[offset]
                offset += 1
                if block_size == 0:
                    break
                offset += block_size
        elif block_id == 0x3B:
            break
        else:
            return "Unknown GIF structure"
    return "Image Descriptor not found"

def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select a GIF file",
        filetypes=[("GIF files", "*.gif")]
    )
    if file_path:
        entry_var.set(file_path)

def run_check():
    gif_file = entry_var.get().strip()
    if not gif_file:
        messagebox.showwarning("GIF Interlace Check", "Please select a GIF file first.")
        return
    result = check_gif_interlacing(gif_file)
    # Show only the result in the alert
    messagebox.showinfo("GIF Interlace Check", f"Result: {result}")

def reset_entry():
    entry_var.set("")

def drop_file(event):
    file_path = event.data.strip("{}")
    if file_path.lower().endswith(".gif"):
        entry_var.set(file_path)
    else:
        messagebox.showwarning("Invalid File", "Please drop a valid .gif file.")

# --- UI Setup ---
root = TkinterDnD.Tk()
root.title("GIF Interlace Checker (Drag & Drop + Browse)")
window_width = 575
window_height = 150

# Center the window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width - window_width) / 2)
y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Lock the window size
root.resizable(False, False)

entry_var = tk.StringVar()

frame = tk.Frame(root, pady=10, padx=10)
frame.pack(fill="both", expand=True)

# Highlight frame for drag-and-drop area
highlight_frame = tk.Frame(frame, bg="#DDEEFF", bd=2, relief="solid")
highlight_frame.grid(row=0, column=0, padx=5, pady=5, sticky="we")

entry = tk.Entry(highlight_frame, textvariable=entry_var, width=45, bg="#E8F4FF")
entry.pack(padx=2, pady=2, fill="x")

# Enable drag-and-drop on the entry
entry.drop_target_register(DND_FILES)
entry.dnd_bind('<<Drop>>', drop_file)

browse_btn = tk.Button(frame, text="Browse", command=browse_file)
browse_btn.grid(row=0, column=1, padx=5, pady=5)

btn_frame = tk.Frame(frame)
btn_frame.grid(row=1, column=0, columnspan=2, pady=10)

check_btn = tk.Button(btn_frame, text="Check", command=run_check, width=10)
check_btn.grid(row=0, column=0, padx=5)

reset_btn = tk.Button(btn_frame, text="Reset", command=reset_entry, width=10)
reset_btn.grid(row=0, column=1, padx=5)

# Bind ESC key to close the window
root.bind("<Escape>", lambda event: root.destroy())

root.mainloop()
