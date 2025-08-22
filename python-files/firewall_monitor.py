import tkinter as tk
from tkinter import scrolledtext
import subprocess
import datetime
import re

# ======= KONFIGURATION =======
SUSPICIOUS_IPS = {
    "192.168.1.100": "Verdächtige IP (möglicherweise Scanner)",
    "203.0.113.45": "Bekannter Bot/Angreifer",
}

blocked_ips = set()
ip_block_times = {}

# ======= HILFSFUNKTIONEN =======
def run_ufw_command(command, use_sudo=True):
    # Führt ein Kommando aus; wenn use_sudo=True, wird 'sudo' vorangestellt
    try:
        full_command = (['sudo'] if use_sudo else []) + command
        result = subprocess.run(full_command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Fehler: {e.stderr}"
    except Exception as e:
        return f"Unbekannter Fehler: {str(e)}"

def extract_ip_from_log(log_line):
    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', log_line)
    return match.group(1) if match else None

def get_suspicious_ip_reason(ip):
    return SUSPICIOUS_IPS.get(ip, "Unbekannte Quelle")

def get_timestamp_from_log(log_line):
    match = re.search(r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})', log_line)
    if match:
        now = datetime.datetime.now()
        # Jahr + Monats- und Zeitangabe aus Log
        return f"{now.year}-{match.group(1)}"
    return "Unbekannt"

def get_process_by_ip(ip):
    # Platzhalter, kann erweitert werden
    if ip == "192.168.1.100":
        return "ssh"
    elif ip == "203.0.113.45":
        return "httpd"
    return "Unbekannt"

# ======= FIREWALL-LOGIK =======
def update_firewall_status():
    output = run_ufw_command(['ufw', 'status', 'verbose'])
    output_text.delete(1.0, tk.END)

    if "Status: active" in output:
        firewall_status_label.config(text="Firewall Status: Aktiv", fg="green")
        # Buttons anpassen
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        refresh_button.config(state=tk.NORMAL)
    else:
        firewall_status_label.config(text="Firewall Status: Deaktiviert", fg="red")
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        refresh_button.config(state=tk.DISABLED)

    for line in output.splitlines():
        if "ALLOW" in line:
            output_text.insert(tk.END, line + '\n', 'green')
        elif "DENY" in line:
            output_text.insert(tk.END, line + '\n', 'yellow')
        elif "BLOCK" in line:
            output_text.insert(tk.END, line + '\n', 'red')
        else:
            output_text.insert(tk.END, line + '\n')

def enable_firewall():
    run_ufw_command(['ufw', 'enable'])
    update_firewall_status()

def disable_firewall():
    run_ufw_command(['ufw', 'disable'])
    update_firewall_status()

def show_firewall_logs():
    output = run_ufw_command(['cat', '/var/log/ufw.log'])
    log_text.delete(1.0, tk.END)

    alert_found = False
    for line in output.splitlines():
        if 'BLOCK' in line or 'DENY' in line:
            ip = extract_ip_from_log(line)
            if ip:
                reason = get_suspicious_ip_reason(ip)
                timestamp = get_timestamp_from_log(line)
                process = get_process_by_ip(ip)

                if ip not in blocked_ips:
                    blocked_ips.add(ip)
                    ip_block_times[ip] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                log_line = f"{timestamp} - {line} - Grund: {reason} - Prozess: {process}"

                if ip in SUSPICIOUS_IPS:
                    alert_found = True

                tag = 'red' if 'BLOCK' in line else 'yellow'
                log_text.insert(tk.END, log_line + '\n' + '-'*80 + '\n', tag)
            else:
                log_text.insert(tk.END, line + '\n' + '-'*80 + '\n', 'yellow')
        else:
            log_text.insert(tk.END, line + '\n' + '-'*80 + '\n', 'green')

    if alert_found:
        set_alarm_light("ALERT")
    else:
        set_alarm_light("NORMAL")

def auto_refresh_logs():
    show_firewall_logs()
    root.after(30000, auto_refresh_logs)  # Alle 30 Sekunden neu laden

# ======= ALARMLICHT =======
pulsing = False

def set_alarm_light(status):
    global pulsing
    if status == "ALERT":
        if not pulsing:
            pulsing = True
            pulse_light()
    else:
        pulsing = False
        alarm_light.config(bg="green")

def pulse_light():
    if pulsing:
        current = alarm_light.cget("bg")
        alarm_light.config(bg="white" if current == "red" else "red")
        alarm_light.after(500, pulse_light)

# ======= GEBLOCKTE IP-ANSICHT =======
def show_blocked_ips_window():
    if hasattr(root, 'blocked_ip_window') and root.blocked_ip_window.winfo_exists():
        root.blocked_ip_window.lift()
        return

    root.blocked_ip_window = tk.Toplevel(root)
    win = root.blocked_ip_window
    win.title("Geblockte IP-Adressen")
    win.geometry("700x400")
    win.configure(bg="#FFEEDD")

    header = tk.Label(win, text="Geblockte IP-Adressen", font=("Arial", 16, "bold"), bg="#FFEEDD")
    header.pack(pady=10)

    text_widget = tk.Text(win, width=80, height=20, wrap=tk.WORD, font=("Courier", 10))
    text_widget.pack(padx=10, pady=10)

    text_widget.insert(tk.END, f"{'Zeit':<20} {'IP':<18} {'Grund':<40}\n")
    text_widget.insert(tk.END, "-"*80 + "\n")

    for ip in blocked_ips:
        grund = get_suspicious_ip_reason(ip)
        zeit = ip_block_times.get(ip, "Unbekannt")
        text_widget.insert(tk.END, f"{zeit:<20} {ip:<18} {grund:<40}\n")

    text_widget.config(state=tk.DISABLED)

# ======= GUI SETUP =======
root = tk.Tk()
root.title("Firewall Monitor")
root.geometry("950x850")
root.configure(bg="#FF6A00")

main_frame = tk.Frame(root, bg="#FF6A00")
main_frame.pack(padx=20, pady=20)

# Alarmlicht
alarm_light = tk.Label(main_frame, text="Alarmlicht", width=20, height=4, bg="green", font=("Arial", 18, 'bold'))
alarm_light.pack(pady=10)

# Firewall Status Label
firewall_status_label = tk.Label(main_frame, text="Firewall Status: Unbekannt", font=("Arial", 14, 'bold'), bg="#FF6A00")
firewall_status_label.pack(pady=10)

# Buttons
start_button = tk.Button(main_frame, text="Firewall starten", command=enable_firewall, width=20, height=2, font=("Arial", 12, 'bold'))
start_button.pack(pady=5)

stop_button = tk.Button(main_frame, text="Firewall stoppen", command=disable_firewall, width=20, height=2, font=("Arial", 12, 'bold'), state=tk.DISABLED)
stop_button.pack(pady=5)

refresh_button = tk.Button(main_frame, text="Status aktualisieren", command=update_firewall_status, width=20, height=2, font=("Arial", 12, 'bold'), state=tk.DISABLED)
refresh_button.pack(pady=5)

log_button = tk.Button(main_frame, text="Logs anzeigen", command=show_firewall_logs, width=20, height=2, font=("Arial", 12, 'bold'))
log_button.pack(pady=5)

blocked_ip_button = tk.Button(main_frame, text="Geblockte IPs anzeigen", command=show_blocked_ips_window, width=25, height=2, font=("Arial", 12, 'bold'))
blocked_ip_button.pack(pady=10)

# Firewall Status Ausgabe
output_text = tk.Text(main_frame, height=15, width=100)
output_text.tag_config('green', foreground='green')
output_text.tag_config('yellow', foreground='orange')
output_text.tag_config('red', foreground='red')
output_text.pack(padx=10, pady=10)

# Log-Textbereich
log_text = tk.Text(main_frame, height=15, width=100)
log_text.tag_config('green', foreground='green')
log_text.tag_config('yellow', foreground='orange')
log_text.tag_config('red', foreground='red')
log_text.pack(padx=10, pady=10)

# Firewall Status direkt beim Start prüfen und Buttons anpassen
update_firewall_status()

# Automatisches Log-Update alle 30 Sekunden starten
auto_refresh_logs()

root.mainloop()


