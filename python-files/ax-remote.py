# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading

# PowerShell script wrapped with try/catch for step-by-step status
ps_script = r'''
$serviceName = "CommerceDataExchangeAsyncClientService"

try {
    Write-Output "Checking service status..."
    $service = Get-Service -Name $serviceName -ErrorAction Stop
    $startMode = (Get-WmiObject -Class Win32_Service -Filter "Name='$serviceName'").StartMode
    Write-Output "Service check: done"
} catch {
    Write-Output "Service check: failed"
}

try {
    if ($startMode -eq "Disabled") {
        Write-Output "Service is disabled. Enabling and starting..."
        Set-Service -Name $serviceName -StartupType Automatic
        Start-Service -Name $serviceName
        Write-Output "Service enable/start: done"
    }
    elseif ($service.Status -ne 'Running') {
        Write-Output "Service not running. Restarting..."
        Restart-Service -Name $serviceName -Force
        Write-Output "Service restart: done"
    }
    else {
        Write-Output "Service already running."
    }
} catch {
    Write-Output "Service start/restart: failed"
}

try {
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
    Write-Output "Disable firewall: done"
} catch {
    Write-Output "Disable firewall: failed"
}

try {
    w32tm /resync
    Write-Output "Time sync: done"
} catch {
    Write-Output "Time sync: failed"
}

try {
    net time \\10.192.30.2 /set /y
    Write-Output "Time set via net time: done"
} catch {
    Write-Output "Time set via net time: failed"
}

try {
    ipconfig /flushdns
    Write-Output "Flush DNS: done"
} catch {
    Write-Output "Flush DNS: failed"
}

try {
    gpupdate /force
    Write-Output "Group policy update: done"
} catch {
    Write-Output "Group policy update: failed"
}
'''

# Function to run the script on all IPs
def run_on_all_ips():
    ip_list = ip_text.get("1.0", tk.END).strip().splitlines()
    username = user_entry.get()
    password = pwd_entry.get()
    output_box.delete(1.0, tk.END)

    def worker(ip):
        command = [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            f"""
            $secpasswd = ConvertTo-SecureString '{password}' -AsPlainText -Force;
            $cred = New-Object System.Management.Automation.PSCredential('{username}', $secpasswd);
            Invoke-Command -ComputerName {ip.strip()} -Credential $cred -ScriptBlock {{ {ps_script} }}
            """
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=120)
            output = f"===== {ip.strip()} =====\n{result.stdout or ''}{result.stderr or ''}\n"
        except Exception as e:
            output = f"===== {ip.strip()} =====\nError: {str(e)}\n"

        output_box.insert(tk.END, output)
        output_box.see(tk.END)

    for ip in ip_list:
        if ip.strip():
            threading.Thread(target=worker, args=(ip.strip(),), daemon=True).start()

# GUI Layout
window = tk.Tk()
window.title("AX Management")

tk.Label(window, text="Enter IP of AX server (one per line):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
ip_text = tk.Text(window, width=40, height=10)
ip_text.grid(row=1, column=0, padx=5, pady=5)

form_frame = tk.Frame(window)
form_frame.grid(row=1, column=1, padx=10, pady=5, sticky='n')

tk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky='e')
user_entry = tk.Entry(form_frame, width=30)
user_entry.grid(row=0, column=1)

tk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky='e')
pwd_entry = tk.Entry(form_frame, width=30, show='*')
pwd_entry.grid(row=1, column=1)

run_button = tk.Button(form_frame, text="Run Script", command=run_on_all_ips)
run_button.grid(row=2, column=0, columnspan=2, pady=10)

output_box = scrolledtext.ScrolledText(window, width=100, height=25)
output_box.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

window.mainloop()
