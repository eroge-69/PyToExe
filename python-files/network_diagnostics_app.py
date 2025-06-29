
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import platform
import threading

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return str(e)

def run_diagnostics():
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "Running diagnostics...\n\n")

    diagnostics = []

    # DNS resolution
    diagnostics.append("Checking DNS resolution...")
    diagnostics.append(run_command("nslookup www.google.com"))

    # DHCP Client service
    diagnostics.append("\nChecking DHCP Client service...")
    diagnostics.append(run_command("sc query Dhcp"))

    # DHCP assignment
    diagnostics.append("\nChecking if IP is assigned via DHCP...")
    diagnostics.append(run_command('netsh interface ip show config'))

    # Internet access
    diagnostics.append("\nChecking internet access...")
    diagnostics.append(run_command('powershell -Command "try { $r = Invoke-WebRequest -Uri \"https://www.google.com\" -UseBasicParsing -TimeoutSec 5; if ($r.StatusCode -eq 200) { \"Internet is accessible\" } else { \"Internet is NOT accessible\" } } catch { \"Internet is NOT accessible\" }"'))

    # Network adapter status
    diagnostics.append("\nChecking network adapter status...")
    diagnostics.append(run_command("netsh interface show interface"))

    # Mapped network drives
    diagnostics.append("\nChecking mapped network drives...")
    diagnostics.append(run_command("net use"))

    # File server access
    diagnostics.append("\nChecking access to file server share...")
    diagnostics.append(run_command("dir \\to-fs-01\sharedfolder"))

    # Ping test
    diagnostics.append("\nPinging key machines...")
    machines = ["10.0.0.1", "www.bbc.co.uk", "to-fs-01", "to-dc-22", "to-dc-21", "to-hv-01", "to-hv-02", "to-hv-03", "to-ra-01", "to-prntserv-01"]
    for machine in machines:
        diagnostics.append(f"Pinging {machine}...")
        diagnostics.append(run_command(f"ping -n 1 {machine}"))

    # Display results
    output_text.insert(tk.END, "\n\n".join(diagnostics))

def start_diagnostics():
    threading.Thread(target=run_diagnostics).start()

# GUI setup
app = tk.Tk()
app.title("Network Diagnostics Tool")
app.geometry("800x600")

run_button = tk.Button(app, text="Run Diagnostics", command=start_diagnostics)
run_button.pack(pady=10)

output_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=100, height=30)
output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

app.mainloop()
