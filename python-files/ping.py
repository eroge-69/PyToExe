import tkinter as tk
import subprocess
import threading
import time
import platform
 
# Function to run ping command
def ping(ip):
    param = "-n" if platform.system().lower()=="windows" else "-c"
    try:
        output = subprocess.run(
            ["ping", param, "1", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if output.returncode == 0:
            return "Reachable"
        else:
            return "Unreachable"
    except Exception as e:
        return f"Error: {e}"
 
# Thread function to update ping results continuously
def ping_loop(ip1, ip2, text_widget, stop_event):
    while not stop_event.is_set():
        result1 = ping(ip1)
        result2 = ping(ip2)
 
        # Update GUI
        text_widget.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {ip1} → {result1}\n")
        text_widget.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {ip2} → {result2}\n")
        text_widget.see(tk.END)  # Auto scroll
 
        time.sleep(1)  # Delay between checks
 
# Start button action
def start_ping():
    ip1 = entry_ip1.get()
    ip2 = entry_ip2.get()
    if not ip1 or not ip2:
        return
 
    global stop_event
    stop_event = threading.Event()
 
    # Run ping loop in background thread
    t = threading.Thread(target=ping_loop, args=(ip1, ip2, text_output, stop_event))
    t.daemon = True
    t.start()
 
# Stop button action
def stop_ping():
    if stop_event:
        stop_event.set()
 
# GUI setup
root = tk.Tk()
root.title("Honeywell IP Ping Checker")
 
tk.Label(root, text="IP Address 1:").grid(row=0, column=0, padx=5, pady=5)
entry_ip1 = tk.Entry(root)
entry_ip1.grid(row=0, column=1, padx=5, pady=5)
 
tk.Label(root, text="IP Address 2:").grid(row=1, column=0, padx=5, pady=5)
entry_ip2 = tk.Entry(root)
entry_ip2.grid(row=1, column=1, padx=5, pady=5)
 
start_btn = tk.Button(root, text="Start", command=start_ping)
start_btn.grid(row=2, column=0, padx=5, pady=5)
 
stop_btn = tk.Button(root, text="Stop", command=stop_ping)
stop_btn.grid(row=2, column=1, padx=5, pady=5)
 
text_output = tk.Text(root, width=50, height=15)
text_output.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
 
stop_event = None
 
root.mainloop()