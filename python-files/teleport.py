import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import json
import os

CONNECTIONS_FILE = 'connections.json'
active_process = None

def load_connections():
    if os.path.exists(CONNECTIONS_FILE):
        with open(CONNECTIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_connections(conns):
    with open(CONNECTIONS_FILE, 'w') as f:
        json.dump(conns, f)

frequent_connections = load_connections()

# GUI Setup
root = tk.Tk()
root.title("Teleport SSH GUI")

# Map service names to their ports
service_ports = {
    "configService": ["8401", "5000"],
    "graphQL": ["65140"],
    "mqtt": ["1883"],
    "grafana": ["3000"],
    "packmlService": ["4852"]
}

# Create BooleanVars for services
service_options = {service: tk.BooleanVar() for service in service_ports}

def build_port_args():
    args = []
    for service, var in service_options.items():
        if var.get():
            for port in service_ports[service]:
                args.append('-L')
                args.append(f'127.0.0.1:{port}:127.0.0.1:{port}')
    return args

def append_output(text):
    output.configure(state='normal')
    output.insert(tk.END, text)
    output.yview(tk.END)
    output.configure(state='disabled')

def run_command_thread(cmd):
    global active_process
    try:
        env = os.environ.copy()
        active_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=False,
            env=env
        )
        for line in active_process.stdout:
            append_output(line)
    except Exception as e:
        append_output(f"[ERROR] {str(e)}\n")

def login():
    cmd = ['tsh', 'login', '--proxy=marel.teleport.sh']
    append_output(f"[INFO] Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, text=True, capture_output=True)
    append_output(result.stdout)

def logout():
    cmd = ['tsh', 'logout']
    append_output(f"[INFO] Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, text=True, capture_output=True)
    append_output(result.stdout)

def connect(use_request=False):
    target = target_entry.get()
    req_id = request_id_entry.get()

    if not target:
        append_output("[WARN] Please enter a connection target.\n")
        return

    if target not in frequent_connections:
        frequent_connections.append(target)
        save_connections(frequent_connections)
        dropdown['values'] = frequent_connections

    cmd = ['tsh', 'ssh'] + build_port_args() + ['--ttl', '240']
    if use_request:
        if not req_id:
            append_output("[WARN] Request ID is required for this option.\n")
            return
        cmd += ['--request-id', req_id]
    cmd.append(target)

    append_output(f"[INFO] Running: {' '.join(cmd)}\n")
    print("Running command:", " ".join(cmd))
    threading.Thread(target=run_command_thread, args=(cmd,), daemon=True).start()

def disconnect():
    global active_process
    if active_process:
        append_output("[INFO] Terminating active connection...\n")
        active_process.terminate()
        active_process = None
    else:
        append_output("[WARN] No active connection to disconnect.\n")

def send_command():
    cmd = cmd_input.get()
    if active_process and active_process.stdin:
        try:
            active_process.stdin.write(cmd + '\n')
            active_process.stdin.flush()
        except Exception as e:
            append_output(f"[ERROR] Could not send input: {str(e)}\n")
    else:
        append_output("[WARN] No active process to send input to.\n")

def on_dropdown_selected(event):
    selection = dropdown.get()
    target_entry.delete(0, tk.END)
    target_entry.insert(0, selection)

def delete_target():
    to_delete = dropdown.get()
    if to_delete in frequent_connections:
        frequent_connections.remove(to_delete)
        save_connections(frequent_connections)
        dropdown['values'] = frequent_connections
        target_entry.delete(0, tk.END)

tk.Label(root, text="Teleport Login GUI", font=('Arial', 16)).grid(column=0, row=0, columnspan=5, pady=10)

tk.Label(root, text="Connection Target:").grid(column=0, row=1, sticky='e')
target_entry = tk.Entry(root, width=30)
target_entry.grid(column=1, row=1)

dropdown = ttk.Combobox(root, values=frequent_connections)
dropdown.grid(column=2, row=1)
dropdown.bind("<<ComboboxSelected>>", on_dropdown_selected)

tk.Button(root, text="Delete", command=delete_target).grid(column=3, row=1)

tk.Label(root, text="Request ID (optional):").grid(column=0, row=2, sticky='e')
request_id_entry = tk.Entry(root, width=30)
request_id_entry.grid(column=1, row=2)

tk.Label(root, text="Port Forwarding:").grid(column=0, row=3, sticky='ne', pady=5)
ports_frame = tk.Frame(root)
ports_frame.grid(column=1, row=3, columnspan=3, sticky='w')
for i, service in enumerate(service_ports):
    tk.Checkbutton(ports_frame, text=service, variable=service_options[service]).grid(row=0, column=i, padx=5)

tk.Button(root, text="Login", command=login).grid(column=0, row=4, pady=10)
tk.Button(root, text="Login with Request ID", command=lambda: connect(True)).grid(column=1, row=4)
tk.Button(root, text="Connect", command=lambda: connect(False)).grid(column=2, row=4)
tk.Button(root, text="Disconnect", command=disconnect).grid(column=3, row=4)
tk.Button(root, text="Logout", command=logout).grid(column=4, row=4)

tk.Label(root, text="Console Output:").grid(column=0, row=5, sticky='nw', padx=5)
output = scrolledtext.ScrolledText(root, width=100, height=15, state='disabled', font=('Courier', 10))
output.grid(column=0, row=6, columnspan=5, padx=10, pady=5)

tk.Label(root, text="Console Input:").grid(column=0, row=7, sticky='e')
cmd_input = tk.Entry(root, width=70)
cmd_input.grid(column=1, row=7, columnspan=3, sticky='w')
tk.Button(root, text="Send", command=send_command).grid(column=4, row=7, sticky='w')

root.protocol("WM_DELETE_WINDOW", lambda: (disconnect(), root.destroy()))
root.mainloop()
