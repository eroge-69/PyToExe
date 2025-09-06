import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os, shutil

def choose_video():
    global selected_video
    filepath = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mkv *.avi")])
    if filepath:
        selected_video = filepath
        video_label.config(text=f"Video: {os.path.basename(filepath)}")

def start_upscale():
    if not selected_video:
        status_label.config(text="⚠️ Please choose a video first!")
        return
    status_label.config(text=f"Upscaling {scale_var.get()} with {model_var.get()}...")
    progress_bar["value"] = 0

    # calculate delay based on upscale factor + model
    factor = scale_var.get()
    model = model_var.get()

    # base speed per progress step (ms)
    delay = 40

    if factor == "1.5x":
        delay *= 4
    elif factor == "2x":
        delay *= 8
    elif factor == "4x":
        delay *= 16

    if model == "main (slow)":
        delay *= 2

    fill_progress(0, delay)

def fill_progress(value, delay):
    if value <= 100:
        progress_bar["value"] = value
        root.after(delay, lambda: fill_progress(value + 2, delay))
    else:
        new_path = save_upscaled_copy()
        status_label.config(text="✅ Upscaling complete!")
        messagebox.showinfo("Upscaling Complete", f"Your video has been saved as:\n{new_path}")

def save_upscaled_copy():
    folder, filename = os.path.split(selected_video)
    name, ext = os.path.splitext(filename)
    new_name = f"{name}_upscaled{ext}"
    new_path = os.path.join(folder, new_name)
    shutil.copy(selected_video, new_path)
    return new_path

root = tk.Tk()
root.title("Simple Upscaler")
root.geometry("380x400")
root.configure(bg="#2b2b2b")
selected_video = None

# Styles
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10), padding=5)
style.configure("TLabel", background="#2b2b2b", foreground="white", font=("Segoe UI", 9))
style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground="#00c896", background="#2b2b2b")
style.configure("TProgressbar", thickness=18)

# Welcome sign
ttk.Label(root, text="Simple Upscaler", style="Title.TLabel").pack(pady=12)

# Choose video
ttk.Button(root, text="Choose Video", command=choose_video).pack(pady=5)
video_label = ttk.Label(root, text="No video selected", wraplength=350)
video_label.pack(pady=5)

# Choose upscale amount
scale_var = tk.StringVar(value="2x")
ttk.Label(root, text="Upscale Amount:").pack(pady=(12,4))
ttk.OptionMenu(root, scale_var, "2x", "1.5x", "2x", "4x").pack()

# Choose AI model
model_var = tk.StringVar(value="rapid (fast)")
ttk.Label(root, text="AI Model:").pack(pady=(12,4))
ttk.OptionMenu(root, model_var, "main (slow)", "main (slow)", "rapid (fast)").pack()

# Upscale button
ttk.Button(root, text="Upscale", command=start_upscale).pack(pady=12)

# Progress bar + status
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)
status_label = ttk.Label(root, text="")
status_label.pack(pady=6)

root.mainloop()
