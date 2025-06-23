import struct
import tkinter as tk
from tkinter import filedialog, messagebox

def patch_mp4_metadata(input_path, output_path, fps):
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    def patch_mvhd():
        index = data.find(b'mvhd')
        if index == -1:
            raise ValueError("mvhd not found")
        version = data[index + 4]
        ts_off = index + 20 if version == 1 else index + 12
        dur_off = index + 24 if version == 1 else index + 16
        timescale = struct.unpack('>I', data[ts_off:ts_off+4])[0]
        duration = struct.unpack('>I', data[dur_off:dur_off+4])[0]
        new_timescale = max(1, timescale // int(fps))
        data[ts_off:ts_off+4] = struct.pack('>I', new_timescale)
        data[dur_off:dur_off+4] = struct.pack('>I', duration * 2)

    def patch_mdhd():
        i = 0
        found = False
        while True:
            i = data.find(b'mdhd', i)
            if i == -1:
                break
            found = True
            version = data[i + 4]
            ts_off = i + 20 if version == 1 else i + 12
            dur_off = i + 24 if version == 1 else i + 16
            timescale = struct.unpack('>I', data[ts_off:ts_off+4])[0]
            duration = struct.unpack('>I', data[dur_off:dur_off+4])[0]
            new_timescale = max(1, timescale // int(fps))
            data[ts_off:ts_off+4] = struct.pack('>I', new_timescale)
            data[dur_off:dur_off+4] = struct.pack('>I', duration * 2)
            i += 4
        if not found:
            raise ValueError("mdhd not found")

    def patch_stts():
        i = 0
        found = False
        while True:
            i = data.find(b'stts', i)
            if i == -1:
                break
            found = True
            entry_count_offset = i + 12
            entry_count = struct.unpack('>I', data[entry_count_offset:entry_count_offset+4])[0]
            for j in range(entry_count):
                delta_offset = i + 16 + (j * 8) + 4
                if delta_offset + 4 > len(data):
                    break
                old_delta = struct.unpack('>I', data[delta_offset:delta_offset+4])[0]
                new_delta = max(1, old_delta // int(fps))
                data[delta_offset:delta_offset+4] = struct.pack('>I', new_delta)
            i += 4
        if not found:
            raise ValueError("stts not found")

    patch_mvhd()
    patch_mdhd()
    patch_stts()

    with open(output_path, 'wb') as f:
        f.write(data)

def browse_and_patch():
    file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if file_path:
        input_fps = fps_entry.get()
        if not input_fps:
            messagebox.showerror("Error", "Please enter the original FPS.")
            return
        try:
            fps = float(input_fps)
            if fps <= 0:
                messagebox.showerror("Error", "FPS should be greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid FPS value.")
            return
        
        output_path = file_path.replace(".mp4", "_patched.mp4")
        try:
            patch_mp4_metadata(file_path, output_path, fps)
            # Success message with original FPS, new FPS, and output file path
            success_message = (
                f"File patched successfully!\n\n"
                f"Original FPS: {fps}\n"
                f"New FPS: 30\n"
                f"Output file:\n{output_path}"
            )
            messagebox.showinfo("Success", success_message)
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Create main GUI window
root = tk.Tk()
root.title("LianZGG PATCH v1.5")
root.geometry("500x250")
root.configure(bg="#2E2E2E")

# Add title label
label = tk.Label(root, text="MP4 Frame Rate Patcher", font=("Arial", 16, "bold"), fg="white", bg="#2E2E2E")
label.pack(pady=10)

# Source MP4 label and input field
source_label = tk.Label(root, text="Source MP4:", font=("Arial", 12), fg="white", bg="#2E2E2E")
source_label.pack(pady=5)

source_entry = tk.Entry(root, font=("Arial", 12), width=40)
source_entry.pack(pady=5)

# Browse button
browse_button = tk.Button(root, text="Browse...", font=("Arial", 12), bg="#4CAF50", fg="white", command=browse_and_patch)
browse_button.pack(pady=10)

# Original FPS label and input field
fps_label = tk.Label(root, text="Original FPS:", font=("Arial", 12), fg="white", bg="#2E2E2E")
fps_label.pack(pady=5)

fps_entry = tk.Entry(root, font=("Arial", 12), width=20)
fps_entry.insert(0, "60.0")  # Default FPS
fps_entry.pack(pady=5)

# Patch button
patch_button = tk.Button(root, text="Patch to 30 FPS", font=("Arial", 12, "bold"), bg="#008CBA", fg="white", command=browse_and_patch)
patch_button.pack(pady=20)

# Footer label
footer_label = tk.Label(root, text="Patch MP4 by LianZGG", font=("Arial", 8), fg="white", bg="#2E2E2E")
footer_label.pack(side="bottom", pady=10)

# Start the Tkinter event loop
root.mainloop()
