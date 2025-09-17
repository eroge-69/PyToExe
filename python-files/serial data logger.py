import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import serial
import threading
import queue
import time
from datetime import datetime
import os

# Queue untuk komunikasi antar-thread
q = queue.Queue()
stop_event = threading.Event()

ser = None
writer_thread = None

# -------- Serial Reader Thread --------
def serial_reader(port, baud, parity, q):
    global ser
    try:
        ser = serial.Serial(port=port, baudrate=baud, parity=parity, timeout=1)
        while not stop_event.is_set():
            line = ser.readline()
            if line:
                try:
                    text = line.decode("utf-8", errors="replace").strip()
                except:
                    text = repr(line)
                timestamp = datetime.now().isoformat(sep=" ", timespec="milliseconds")
                q.put((timestamp, text))
        ser.close()
    except Exception as e:
        q.put(("ERROR", f"Serial error: {e}"))

# -------- File Writer Thread --------
def file_writer(filename, header, q):
    first_write = not os.path.exists(filename)
    try:
        with open(filename, "a", encoding="utf-8", buffering=1) as f:
            if first_write:
                f.write(f"# Log start: {datetime.now().isoformat()}\n")
                f.write(f"# {header}\n")
                f.write("# Columns: timestamp | raw_data\n")
            while not stop_event.is_set():
                try:
                    timestamp, text = q.get(timeout=0.5)
                except queue.Empty:
                    continue
                if timestamp == "ERROR":
                    continue
                f.write(f"{timestamp} | {text}\n")
    except Exception as e:
        q.put(("ERROR", f"File write error: {e}"))

# -------- GUI --------
class SerialLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Data Logger")

        # --- Frame Config ---
        config_frame = ttk.LabelFrame(root, text="Configuration")
        config_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(config_frame, text="Port:").grid(row=0, column=0, sticky="w")
        self.port_entry = ttk.Entry(config_frame)
        self.port_entry.insert(0, "COM3")
        self.port_entry.grid(row=0, column=1, padx=5)

        ttk.Label(config_frame, text="Baudrate:").grid(row=0, column=2, sticky="w")
        self.baud_entry = ttk.Entry(config_frame)
        self.baud_entry.insert(0, "9600")
        self.baud_entry.grid(row=0, column=3, padx=5)

        ttk.Label(config_frame, text="Parity:").grid(row=0, column=4, sticky="w")
        self.parity_cb = ttk.Combobox(config_frame, values=["N", "E", "O"], width=5)
        self.parity_cb.set("N")
        self.parity_cb.grid(row=0, column=5, padx=5)

        ttk.Label(config_frame, text="Save Path:").grid(row=1, column=0, sticky="w")
        self.path_entry = ttk.Entry(config_frame, width=40)
        self.path_entry.insert(0, "data_log.txt")
        self.path_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky="we")

        self.browse_btn = ttk.Button(config_frame, text="Browse", command=self.browse_file)
        self.browse_btn.grid(row=1, column=4, columnspan=2, padx=5)

        ttk.Label(config_frame, text="Custom Header:").grid(row=2, column=0, sticky="w")
        self.header_entry = ttk.Entry(config_frame, width=50)
        self.header_entry.insert(0, "Device: MySensor; Location: Plant A")
        self.header_entry.grid(row=2, column=1, columnspan=5, padx=5, sticky="we")

        # --- Frame Buttons ---
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=5, pady=5)

        self.connect_btn = ttk.Button(btn_frame, text="Connect", command=self.connect)
        self.connect_btn.pack(side="left", padx=5)

        self.disconnect_btn = ttk.Button(btn_frame, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_btn.pack(side="left", padx=5)

        # --- Frame Preview ---
        preview_frame = ttk.LabelFrame(root, text="Live Preview")
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.text_area = scrolledtext.ScrolledText(preview_frame, wrap="word", height=15)
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)

        self.update_preview()

    def browse_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file)

    def connect(self):
        global writer_thread
        port = self.port_entry.get()
        baud = int(self.baud_entry.get())
        parity = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}[self.parity_cb.get()]
        filename = self.path_entry.get()
        header = self.header_entry.get()

        if not filename:
            messagebox.showerror("Error", "Please select a save path.")
            return

        stop_event.clear()
        # Start writer
        writer_thread = threading.Thread(target=file_writer, args=(filename, header, q), daemon=True)
        writer_thread.start()
        # Start reader
        reader_thread = threading.Thread(target=serial_reader, args=(port, baud, parity, q), daemon=True)
        reader_thread.start()

        self.connect_btn.config(state="disabled")
        self.disconnect_btn.config(state="normal")
        self.text_area.insert(tk.END, f"[INFO] Connected to {port} @ {baud}, parity={self.parity_cb.get()}\n")

    def disconnect(self):
        stop_event.set()
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.text_area.insert(tk.END, "[INFO] Disconnected\n")

    def update_preview(self):
        try:
            while True:
                timestamp, text = q.get_nowait()
                if timestamp == "ERROR":
                    self.text_area.insert(tk.END, f"[ERROR] {text}\n")
                else:
                    self.text_area.insert(tk.END, f"{timestamp} | {text}\n")
                self.text_area.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(200, self.update_preview)

# -------- Run App --------
if __name__ == "__main__":
    root = tk.Tk()
    app = SerialLoggerApp(root)
    root.mainloop()
