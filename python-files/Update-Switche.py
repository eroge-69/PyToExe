import tkinter as tk
from tkinter import ttk, messagebox
import paramiko
import time
import ipaddress
import threading
import re

class SwitchUpdaterGUI:
    def __init__(self, root):
        self.root = root
        root.title("Switch Firmware Updater")

        # IP Range Scan Eingabe + Button
        ttk.Label(root, text="IP Range (z.B. 192.168.1.1-192.168.1.254):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5, columnspan=5)
        self.ip_range_entry = ttk.Entry(root, width=40)
        self.ip_range_entry.grid(row=1, column=0, padx=5, pady=5, columnspan=4)
        self.scan_button = ttk.Button(root, text="Scan starten", command=self.start_scan)
        self.scan_button.grid(row=1, column=4, padx=5, pady=5)

        # Scrollable Frame für Switches mit Buttons und Hersteller-Spalte
        self.switches_frame = ttk.Frame(root)
        self.switches_frame.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.switches_frame)
        self.scrollbar = ttk.Scrollbar(self.switches_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Überschriften für Liste
        headings = ["IP Adresse", "Hersteller", "Version", "Version prüfen", "Firmware hochladen", "Neustart"]
        for col, text in enumerate(headings):
            ttk.Label(self.scrollable_frame, text=text, font=("Arial", 9, "bold")).grid(row=0, column=col, padx=5, pady=3)

        # Eingabefelder für Credentials und Infos unten
        self.entries = {}
        fields = ['Benutzer', 'Passwort', 'Firmware-Pfad', 'TFTP Server']
        for i, field in enumerate(fields):
            label = ttk.Label(root, text=field)
            label.grid(row=i+3, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(root, width=30, show="*" if field == 'Passwort' else None)
            entry.grid(row=i+3, column=1, columnspan=4, padx=5, pady=5, sticky="ew")
            self.entries[field] = entry

        # Textfeld für Ausgabe
        self.output = tk.Text(root, height=14, width=85)
        self.output.grid(row=7, column=0, columnspan=5, pady=10, padx=5, sticky="ew")

        self.ssh_connections = {}  # IP -> (ssh, shell, vendor)
        self.lock = threading.Lock()
        self.switch_rows = 1  # Zähler für dynamische Zeilen

    def log(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def parse_ip_range(self, ip_range_str):
        try:
            start_ip, end_ip = ip_range_str.split('-')
            start = ipaddress.IPv4Address(start_ip.strip())
            end = ipaddress.IPv4Address(end_ip.strip())
            ips = [str(ipaddress.IPv4Address(ip)) for ip in range(int(start), int(end)+1)]
            return ips
        except Exception:
            self.log("Ungültige IP-Range. Format: 192.168.1.1-192.168.1.254")
            return []

    def scan_ip(self, ip, username, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=3)
            shell = ssh.invoke_shell()
            time.sleep(1)
            shell.recv(1000)
            vendor, _ = self.detect_vendor(shell)
            ssh.close()
            self.log(f"Switch gefunden: {ip} - Hersteller: {vendor if vendor else 'Unbekannt'}")
            self.root.after(0, self.add_switch_row, ip, vendor if vendor else "unbekannt")
        except Exception:
            pass  # nicht erreichbar oder kein SSH

    def start_scan(self):
        for widget in self.scrollable_frame.winfo_children():
            if int(widget.grid_info()['row']) > 0:
                widget.destroy()  # alte Zeilen löschen
        self.ssh_connections.clear()
        self.switch_rows = 1

        ip_range = self.ip_range_entry.get()
        username = self.entries['Benutzer'].get()
        password = self.entries['Passwort'].get()

        if not username or not password:
            messagebox.showerror("Fehler", "Benutzer und Passwort für Scan erforderlich")
            return

        ips = self.parse_ip_range(ip_range)
        if not ips:
            return

        self.log(f"Starte Scan für {len(ips)} IPs...")

        def thread_scan():
            for ip in ips:
                self.scan_ip(ip, username, password)
            self.log("Scan abgeschlossen.")

        threading.Thread(target=thread_scan, daemon=True).start()

    def add_switch_row(self, ip, vendor):
        row = self.switch_rows
        self.switch_rows += 1

        ttk.Label(self.scrollable_frame, text=ip).grid(row=row, column=0, padx=5, pady=2, sticky="w")
        vendor_lbl = ttk.Label(self.scrollable_frame, text=vendor)
        vendor_lbl.grid(row=row, column=1, padx=5, pady=2)

        version_lbl = ttk.Label(self.scrollable_frame, text="noch nicht geprüft")
        version_lbl.grid(row=row, column=2, padx=5, pady=2)

        version_btn = ttk.Button(self.scrollable_frame, text="Version prüfen", command=lambda ip=ip, lbl=version_lbl: self.check_version(ip, lbl))
        version_btn.grid(row=row, column=3, padx=5, pady=2)
        upload_btn = ttk.Button(self.scrollable_frame, text="Hochladen", command=lambda ip=ip: self.upload_firmware(ip))
        upload_btn.grid(row=row, column=4, padx=5, pady=2)
        restart_btn = ttk.Button(self.scrollable_frame, text="Neustarten", command=lambda ip=ip: self.restart_switch(ip))
        restart_btn.grid(row=row, column=5, padx=5, pady=2)

    def get_ssh_connection(self, ip):
        with self.lock:
            if ip in self.ssh_connections:
                return self.ssh_connections[ip]
            else:
                user = self.entries['Benutzer'].get()
                password = self.entries['Passwort'].get()
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip, username=user, password=password, timeout=10)
                    shell = ssh.invoke_shell()
                    time.sleep(1)
                    shell.recv(1000)
                    vendor, _ = self.detect_vendor(shell)
                    self.ssh_connections[ip] = (ssh, shell, vendor)
                    self.log(f"Verbunden mit {ip} - Hersteller: {vendor if vendor else 'unbekannt'}")
                    return ssh, shell, vendor
                except Exception as e:
                    self.log(f"Verbindungsfehler zu {ip}: {e}")
                    return None, None, None

    def detect_vendor(self, shell):
        # Versuche verschiedene Commands, suche Hersteller-Keywords
        commands = {
            "cisco": "show version",
            "aruba": "show version",
            "huawei": "display version",
            "hp": "show version",
            "hpe": "show version"
        }
        output = ""
        vendor_detected = None
        for vendor, cmd in commands.items():
            shell.send(cmd + '\n')
            time.sleep(3)
            try:
                out = shell.recv(10000).decode().lower()
            except Exception:
                out = ""
            output += f"\n--- Output for {vendor} command ---\n{out}\n"
            # Einfache Keyword-Suchen
            if vendor in out:
                vendor_detected = vendor
                break
            if "aruba" in out:
                vendor_detected = "aruba"
                break
            if "huawei" in out:
                vendor_detected = "huawei"
                break
            if "cisco" in out:
                vendor_detected = "cisco"
                break
            if "hp" in out or "hpe" in out:
                vendor_detected = "hp"
                break
        return vendor_detected, output

    def send_command(self, shell, command, wait=2):
        shell.send(command + '\n')
        time.sleep(wait)
        try:
            resp = shell.recv(10000).decode()
        except Exception:
            resp = ""
        return resp

    def extract_version(self, output, vendor):
        lines = output.splitlines()
        version_line = None
        # Aruba/HPE parsing
        if vendor.lower() in ["aruba", "hp", "hpe"]:
            version_regex = re.compile(r"^\s*Version\s*[:=]\s*(.+)$", re.IGNORECASE)
            for line in lines:
                match = version_regex.match(line)
                if match:
                    version_line = match.group(1).strip()
                    break
        # Cisco parsing
        elif vendor.lower() == "cisco":
            # Normalerweise 'Cisco IOS Software, ... Version XX.XX...'
            for line in lines:
                if "version" in line.lower() and "ios" in line.lower():
                    version_line = line.strip()
                    break
        # Huawei parsing
        elif vendor.lower() == "huawei":
            version_regex = re.compile(r"^\s*VRP \(R\S+\)\s+Version\s+(\S+)", re.IGNORECASE)
            for line in lines:
                match = version_regex.match(line)
                if match:
                    version_line = match.group(1).strip()
                    break
        # Fallback: erste Zeile ohne Prompt oder Command
        if not version_line:
            for line in lines:
                if (line.strip() and
                    "show version" not in line.lower() and
                    "display version" not in line.lower() and
                    not line.strip().startswith("#") and
                    not line.strip().startswith(">")):
                    version_line = line.strip()
                    break
        return version_line if version_line else "Version nicht gefunden"

    def check_version(self, ip, label_widget):
        def task():
            ssh, shell, vendor = self.get_ssh_connection(ip)
            if not ssh:
                self.log(f"{ip}: Keine Verbindung zum Switch")
                self.update_label_text(label_widget, "Fehler")
                return
            if not vendor:
                self.log(f"{ip}: Hersteller unbekannt")
                self.update_label_text(label_widget, "Unbekannt")
                return

            self.log(f"{ip}: Version wird abgefragt...")
            if vendor == "cisco":
                cmd = "show version"
            elif vendor in ["aruba", "hp", "hpe"]:
                cmd = "show version"
            elif vendor == "huawei":
                cmd = "display version"
            else:
                self.log(f"{ip}: Hersteller nicht unterstützt")
                self.update_label_text(label_widget, "Nicht unterstützt")
                return
            output = self.send_command(shell, cmd)
            self.log(f"{ip} Version Ausgabe:\n{output}")
            version_str = self.extract_version(output, vendor)
            self.update_label_text(label_widget, version_str[:60])  # kürzt Text im Label

        threading.Thread(target=task, daemon=True).start()

    def update_label_text(self, label, text):
        def update():
            label.config(text=text)
        self.root.after(0, update)

    def upload_firmware(self, ip):
        def task():
            ssh, shell, vendor = self.get_ssh_connection(ip)
            if not ssh:
                self.log(f"{ip}: Keine Verbindung")
                return
            if not vendor:
                self.log(f"{ip}: Hersteller unbekannt")
                return

            tftp_server = self.entries['TFTP Server'].get()
            fw_path = self.entries['Firmware-Pfad'].get()

            self.log(f"{ip}: Starte Firmware Upload...")
            try:
                if vendor == "cisco":
                    cmd = f"copy tftp://{tftp_server}/{fw_path} flash:"
                    self.send_command(shell, cmd, wait=5)
                    self.send_command(shell, '\n', wait=5)
                elif vendor in ["aruba", "hp", "hpe"]:
                    cmd = f"copy tftp {tftp_server} {fw_path} primary"
                    self.send_command(shell, cmd, wait=10)
                elif vendor == "huawei":
                    cmd = f"ftp {tftp_server} put {fw_path} flash:"
                    self.send_command(shell, cmd, wait=10)
                else:
                    self.log(f"{ip}: Hersteller nicht unterstützt für Upload")
                    return
                self.log(f"{ip}: Firmware Upload abgeschlossen.")
            except Exception as e:
                self.log(f"{ip}: Fehler Upload - {e}")

        threading.Thread(target=task, daemon=True).start()

    def restart_switch(self, ip):
        def task():
            ssh, shell, vendor = self.get_ssh_connection(ip)
            if not ssh:
                self.log(f"{ip}: Keine Verbindung")
                return
            if not vendor:
                self.log(f"{ip}: Hersteller unbekannt")
                return

            fw_path = self.entries['Firmware-Pfad'].get()

            self.log(f"{ip}: Starte Neustart...")
            try:
                if vendor == "cisco":
                    self.send_command(shell, "configure terminal")
                    self.send_command(shell, f"boot system flash:{fw_path.split('/')[-1]}")
                    self.send_command(shell, "end")
                    self.send_command(shell, "write memory")
                    self.send_command(shell, "reload", wait=5)
                    self.send_command(shell, "\n", wait=2)
                elif vendor in ["aruba", "hp", "hpe"]:
                    self.send_command(shell, f"boot system flash primary")
                    self.send_command(shell, "save")
                    self.send_command(shell, "reload", wait=5)
                    self.send_command(shell, "y", wait=2)
                elif vendor == "huawei":
                    self.send_command(shell, f"startup system-software flash:{fw_path.split('/')[-1]}")
                    self.send_command(shell, "save")
                    self.send_command(shell, "reboot", wait=5)
                    self.send_command(shell, "y", wait=2)
                else:
                    self.log(f"{ip}: Hersteller nicht unterstützt für Neustart")
                    return
                self.log(f"{ip}: Neustart angestoßen.")
            except Exception as e:
                self.log(f"{ip}: Fehler beim Neustart - {e}")

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SwitchUpdaterGUI(root)
    root.mainloop()
