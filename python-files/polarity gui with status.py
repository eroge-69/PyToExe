import socket
import tkinter as tk
from tkinter import messagebox

# Server IP and Ports
IP_ADDRESS = "10.100.60.254"
PORTS = {
    "4022": 4022,
    "4023": 4023
}

status_labels = {}

# Send PO+ or PO- to set polarity, then read and update status
def send_set_command(command, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(60)
            s.connect((IP_ADDRESS, port))
            s.sendall(command.encode())
            s.recv(1024)  # Optional: read response
            print(f"Sent '{command}' to port {port}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send '{command}' to port {port}\n{e}")
        update_status_label(port, "Error", "gray")
        return

    # After setting, read status
    read_status(port)

# Send PO command to read polarity status
def read_status(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(60)
            s.connect((IP_ADDRESS, port))
            s.sendall("PO".encode())
            response = s.recv(1024).decode().strip()
            print(f"Read PO from port {port}, Received: {response}")
            if response == "1":
                update_status_label(port, "Positive", "green")
            elif response == "0":
                update_status_label(port, "Negative", "red")
            else:
                update_status_label(port, f"Unknown ({response})", "gray")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read from port {port}\n{e}")
        update_status_label(port, "Error", "gray")

# Update GUI label
def update_status_label(port, text, color):
    label = status_labels.get(port)
    if label:
        label.config(text=f"Polarity: {text}", fg=color)

# GUI Setup
root = tk.Tk()
root.title("Remote Polarity Controller")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="PO+ / PO- Command and Polarity Status", font=("Arial", 14)).grid(row=0, column=0, columnspan=3, pady=10)

for idx, (port_name, port_num) in enumerate(PORTS.items()):
    col = idx
    tk.Label(frame, text=f"Port {port_name}", font=("Arial", 12)).grid(row=1, column=col, pady=(0, 5))

    tk.Button(frame, text="Send PO+", width=15,
              command=lambda p=port_num: send_set_command("PO+", p)).grid(row=2, column=col, padx=10, pady=2)

    tk.Button(frame, text="Send PO-", width=15,
              command=lambda p=port_num: send_set_command("PO-", p)).grid(row=3, column=col, padx=10, pady=2)

    tk.Button(frame, text="Read Status", width=15,
              command=lambda p=port_num: read_status(p)).grid(row=4, column=col, padx=10, pady=(10, 2))

    status = tk.Label(frame, text="Polarity: Unknown", fg="gray", font=("Arial", 10, "bold"))
    status.grid(row=5, column=col, pady=(5, 10))
    status_labels[port_num] = status

# Automatically read initial status after GUI loads
def init_status_check():
    for port in PORTS.values():
        root.after(500, lambda p=port: read_status(p))

root.after(100, init_status_check)
root.mainloop()
