import tkinter as tk
from tkinter import ttk
import psutil
import time
import threading

class DataUsageApp:
    def __init__(self, root):
        self.root = root
        
        self.root.title("Network Usage Monitor")
        # self.root.geometry("00x400")
        self.root.resizable(False, False)

        self.prev_bytes_sent = psutil.net_io_counters().bytes_sent
        self.prev_bytes_recv = psutil.net_io_counters().bytes_recv

        self.reset_usage()

        # Widgets
        self.sent_label = ttk.Label(root, text="Sent: 0 B", font=("Arial", 12))
        self.sent_label.pack(pady=2)

        self.recv_label = ttk.Label(root, text="Received: 0 B", font=("Arial", 12))
        self.recv_label.pack(pady=2)

        self.total_label = ttk.Label(root, text="Total Data Used: 0 B", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=6)

        self.packet_sent_label = ttk.Label(root, text="Packets Sent: 0", font=("Arial", 12))
        self.packet_sent_label.pack(pady=2)

        self.packet_recv_label = ttk.Label(root, text="Packets Received: 0", font=("Arial", 12))
        self.packet_recv_label.pack(pady=2)

        self.upload_speed_label = ttk.Label(root, text="Upload Speed: 0 KB/s", font=("Arial", 12, "bold"))
        self.upload_speed_label.pack(pady=5)

        self.download_speed_label = ttk.Label(root, text="Download Speed: 0 KB/s", font=("Arial", 12, "bold"))
        self.download_speed_label.pack(pady=5)

        self.reset_button = ttk.Button(root, text="Reset", command=self.reset_usage)
        self.reset_button.pack(pady=10)

        # 🔘 Toggle Size Button
        self.toggle_button = ttk.Button(root, text="Toggle Size", command=self.toggle_size)
        self.toggle_button.pack(pady=5)

        self.small_view = False  # State flag

        # Start background update
        self.update_thread = threading.Thread(target=self.update_usage)
        self.update_thread.daemon = True
        self.update_thread.start()

    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def format_speed(self, size):
        size_kb = size / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f} KB/s"
        else:
            return f"{size_kb / 1024:.2f} MB/s"

    def reset_usage(self):
        net = psutil.net_io_counters()
        self.start_sent = net.bytes_sent
        self.start_recv = net.bytes_recv
        self.start_packets_sent = net.packets_sent
        self.start_packets_recv = net.packets_recv

    def toggle_size(self):
        if self.small_view:
            self.root.geometry("200x400")
            self.small_view = False
        else:
            self.root.geometry("100x100")
            self.small_view = True

    def update_usage(self):
        while True:
            net = psutil.net_io_counters()

            # Usage data
            sent = net.bytes_sent - self.start_sent
            recv = net.bytes_recv - self.start_recv
            total = sent + recv
            packets_sent = net.packets_sent - self.start_packets_sent
            packets_recv = net.packets_recv - self.start_packets_recv

            # Speed
            curr_bytes_sent = net.bytes_sent
            curr_bytes_recv = net.bytes_recv
            upload_speed = curr_bytes_sent - self.prev_bytes_sent
            download_speed = curr_bytes_recv - self.prev_bytes_recv
            self.prev_bytes_sent = curr_bytes_sent
            self.prev_bytes_recv = curr_bytes_recv

            # Update UI
            self.sent_label.config(text=f"Sent: {self.format_bytes(sent)}")
            self.recv_label.config(text=f"Received: {self.format_bytes(recv)}")
            self.total_label.config(text=f"Total Data Used: {self.format_bytes(total)}")
            self.packet_sent_label.config(text=f"Packets Sent: {packets_sent}")
            self.packet_recv_label.config(text=f"Packets Received: {packets_recv}")
            self.upload_speed_label.config(text=f"Upload Speed: {self.format_speed(upload_speed)}")
            self.download_speed_label.config(text=f"Download Speed: {self.format_speed(download_speed)}")

            time.sleep(1)

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("250x300")
    app = DataUsageApp(root)
    root.mainloop()
