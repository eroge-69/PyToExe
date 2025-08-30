import subprocess
import smtplib
import configparser
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, Toplevel
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class NetworkMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("AUTC - Netzwerk-Überwachungstool, Oliver Henshel")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.running = False
        self.response_times = []
        self.max_data_points = 30  # Erhöht auf 30 Werte

        # Variablen (wie zuvor)
        self.target = tk.StringVar()
        self.max_timeouts = tk.IntVar(value=3)
        self.ping_size = tk.IntVar(value=32)
        self.max_response_time = tk.IntVar(value=500)
        self.smtp_server = tk.StringVar()
        self.smtp_port = tk.IntVar(value=25)
        self.smtp_user = tk.StringVar()
        self.smtp_password = tk.StringVar()
        self.sender_email = tk.StringVar()
        self.receiver_email = tk.StringVar()
        self.encryption = tk.StringVar(value="Unverschlüsselt")
        self.use_auth = tk.BooleanVar(value=False)
        self.log_path = tk.StringVar(value=os.path.join(os.getcwd(), "Logs"))
        self.ini_path = tk.StringVar(value=os.path.join(os.getcwd(), "config.ini"))

        # GUI-Elemente
        self.setup_ui()
        self.load_config()

        # ASCII-Grafik-Fenster
        self.ascii_window = None
        self.ascii_text = None

    def setup_ui(self):
        # Zieladresse
        ttk.Label(self.root, text="Zieladresse (IP/DNS):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.target, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Max. Timeouts
        ttk.Label(self.root, text="Max. Timeouts:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.max_timeouts, width=30).grid(row=1, column=1, padx=5, pady=5)

        # Max. Antwortzeit (ms)
        ttk.Label(self.root, text="Max. Antwortzeit (ms):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.max_response_time, width=30).grid(row=2, column=1, padx=5, pady=5)

        # Ping-Paketgröße
        ttk.Label(self.root, text="Ping-Paketgröße (Bytes):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.ping_size, width=30).grid(row=3, column=1, padx=5, pady=5)

        # Protokoll-Pfad
        ttk.Label(self.root, text="Protokoll-Pfad:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.log_path, width=30).grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="...", command=lambda: self.choose_path(self.log_path), width=3).grid(row=4, column=2, padx=5, pady=5)

        # INI-Pfad
        ttk.Label(self.root, text="INI-Pfad:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.ini_path, width=30).grid(row=5, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="...", command=lambda: self.choose_path(self.ini_path, is_file=True), width=3).grid(row=5, column=2, padx=5, pady=5)

        # SMTP-Einstellungen (wie zuvor)
        ttk.Label(self.root, text="SMTP-Server:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.smtp_server, width=30).grid(row=6, column=1, padx=5, pady=5)
        ttk.Label(self.root, text="SMTP-Port:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.smtp_port, width=30).grid(row=7, column=1, padx=5, pady=5)
        ttk.Checkbutton(self.root, text="SMTP-Authentifizierung verwenden", variable=self.use_auth).grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        ttk.Label(self.root, text="SMTP-Benutzername:").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        self.smtp_user_entry = ttk.Entry(self.root, textvariable=self.smtp_user, width=30, state="disabled")
        self.smtp_user_entry.grid(row=9, column=1, padx=5, pady=5)
        ttk.Label(self.root, text="SMTP-Passwort:").grid(row=10, column=0, padx=5, pady=5, sticky="w")
        self.smtp_password_entry = ttk.Entry(self.root, textvariable=self.smtp_password, width=30, state="disabled", show="*")
        self.smtp_password_entry.grid(row=10, column=1, padx=5, pady=5)
        ttk.Label(self.root, text="Absender-E-Mail:").grid(row=11, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.sender_email, width=30).grid(row=11, column=1, padx=5, pady=5)
        ttk.Label(self.root, text="Empfänger-E-Mail:").grid(row=12, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.receiver_email, width=30).grid(row=12, column=1, padx=5, pady=5)
        ttk.Label(self.root, text="Verschlüsselung:").grid(row=13, column=0, padx=5, pady=5, sticky="w")
        ttk.Combobox(self.root, textvariable=self.encryption, values=["SSL", "TLS", "Unverschlüsselt"], width=27).grid(row=13, column=1, padx=5, pady=5)

        # Checkbox-Event für Authentifizierung
        self.use_auth.trace_add("write", self.toggle_auth_fields)

        # Start/Stop-Buttons
        ttk.Button(self.root, text="Überwachung starten", command=self.start_monitoring).grid(row=14, column=0, padx=5, pady=10)
        ttk.Button(self.root, text="Überwachung stoppen", command=self.stop_monitoring, state="disabled").grid(row=14, column=1, padx=5, pady=10)
        ttk.Button(self.root, text="ASCII-Grafik anzeigen", command=self.show_ascii_window).grid(row=14, column=2, padx=5, pady=10)

        # Log-Fenster
        ttk.Label(self.root, text="Aktivitätsprotokoll:").grid(row=15, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        self.log_area = scrolledtext.ScrolledText(self.root, width=60, height=10, wrap=tk.WORD)
        self.log_area.grid(row=16, column=0, columnspan=3, padx=5, pady=5)

        # Status-Anzeige
        self.status_label = ttk.Label(self.root, text="Status: Bereit")
        self.status_label.grid(row=17, column=0, columnspan=3, pady=5)

    def choose_path(self, path_var, is_file=False):
        """Öffnet einen Dialog zur Auswahl des Pfads/Datei."""
        if is_file:
            selected = filedialog.asksaveasfilename(
                title="INI-Datei speichern unter",
                initialfile="config.ini",
                defaultextension=".ini",
                filetypes=[("INI-Dateien", "*.ini")]
            )
        else:
            selected = filedialog.askdirectory(title="Pfad auswählen")

        if selected:
            path_var.set(selected)

    def toggle_auth_fields(self, *args):
        state = "normal" if self.use_auth.get() else "disabled"
        self.smtp_user_entry.config(state=state)
        self.smtp_password_entry.config(state=state)

    def log_message(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update()

    def show_ascii_window(self):
        """Öffnet ein separates Fenster für die ASCII-Grafik (30 Werte)."""
        if self.ascii_window is None or not self.ascii_window.winfo_exists():
            self.ascii_window = Toplevel(self.root)
            self.ascii_window.title("ASCII-Grafik: Ping-Antwortzeiten (ms)")
            self.ascii_window.geometry("800x450")  # Größeres Fenster für 30 Werte

            self.ascii_text = tk.Text(
                self.ascii_window,
                width=90,  # Breiter für 30 Werte
                height=25,
                font=("Courier", 10),
                wrap=tk.NONE
            )
            self.ascii_text.pack(padx=10, pady=10)

            # Initialisierung der Grafik
            self.update_ascii_graph(0)

    def update_ascii_graph(self, response_time):
        """Aktualisiert die ASCII-Grafik mit 30 Werten (1 Einheit = 10 ms)."""
        if self.ascii_window is None or not self.ascii_window.winfo_exists():
            return

        self.response_times.append(response_time)
        if len(self.response_times) > self.max_data_points:  # Maximal 30 Werte
            self.response_times.pop(0)

        # Grafik neu zeichnen
        self.ascii_text.delete(1.0, tk.END)

        # Titel
        self.ascii_text.insert(tk.END, "ASCII-Grafik: Ping-Antwortzeiten (ms) - Letzte 30 Werte\n")
        self.ascii_text.insert(tk.END, "Y (ms)\n")
        self.ascii_text.insert(tk.END, "   |\n")

        # Y-Achse: 0 bis 200 ms (Skalierung: 1 Einheit = 10 ms)
        max_y = 20  # 20 Einheiten * 10 ms = 200 ms
        for y in range(max_y, -1, -1):
            line = f"{y * 10:3d} | "
            for x, value in enumerate(self.response_times):
                if value >= y * 10:
                    line += "■ "  # Volles Kästchen
                else:
                    line += "  "
            self.ascii_text.insert(tk.END, f"{line}\n")

        # X-Achse (30 Werte)
        self.ascii_text.insert(tk.END, "     +")
        for x in range(self.max_data_points):
            if x % 5 == 0:  # Nur alle 5 Werte markieren
                self.ascii_text.insert(tk.END, "--+")
            else:
                self.ascii_text.insert(tk.END, "---")
        self.ascii_text.insert(tk.END, "\n")

        # X-Achsen-Beschriftung (alle 5 Werte)
        self.ascii_text.insert(tk.END, "      ")
        for x in range(self.max_data_points):
            if x % 5 == 0:
                self.ascii_text.insert(tk.END, f"{x:2d} ")
            else:
                self.ascii_text.insert(tk.END, "   ")
        self.ascii_text.insert(tk.END, "\n")

    def write_timeout_log(self, target, reason):
        """Fügt einen Fehler-Eintrag zur täglichen Protokolldatei hinzu."""
        if not os.path.exists(self.log_path.get()):
            os.makedirs(self.log_path.get())

        today = datetime.now().strftime("%Y-%m-%d")
        log_filename = os.path.join(self.log_path.get(), f"protokoll_{today}.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_filename, "a") as f:
            f.write(f"{timestamp} | Ziel: {target} | Grund: {reason}\n")

        self.log_message(f"Fehler protokolliert: {log_filename}")

    def ping(self, host):
        try:
            if subprocess.os.name == "nt":  # Windows
                command = ["ping", "-n", "1", "-l", str(self.ping_size.get()), host]
            else:  # Linux/macOS
                command = ["ping", "-c", "1", "-s", str(self.ping_size.get()), host]

            start_time = time.time()
            output = subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'
            )
            response_time = (time.time() - start_time) * 1000  # in Millisekunden

            if response_time > self.max_response_time.get():
                self.log_message(f"Ping an {host} zu langsam: {response_time:.2f} ms (Max: {self.max_response_time.get()} ms)")
                self.update_ascii_graph(response_time)
                return False, response_time, "Zu langsame Antwort"
            else:
                self.log_message(f"Ping an {host} erfolgreich. Antwortzeit: {response_time:.2f} ms")
                self.update_ascii_graph(response_time)
                return True, response_time, "OK"
        except subprocess.CalledProcessError as e:
            self.log_message(f"Ping an {host} fehlgeschlagen: {e.output.strip()}")
            self.update_ascii_graph(0)
            return False, 0, "Keine Antwort"
        except Exception as e:
            self.log_message(f"Fehler beim Ping: {str(e)}")
            self.update_ascii_graph(0)
            return False, 0, "Sonstiger Fehler"

    def send_email(self, subject, body):
        msg = MIMEMultipart()
        msg["From"] = self.sender_email.get()
        msg["To"] = self.receiver_email.get()
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            if self.encryption.get() == "SSL":
                server = smtplib.SMTP_SSL(self.smtp_server.get(), self.smtp_port.get())
            elif self.encryption.get() == "TLS":
                server = smtplib.SMTP(self.smtp_server.get(), self.smtp_port.get())
                server.starttls()
            else:
                server = smtplib.SMTP(self.smtp_server.get(), self.smtp_port.get())

            if self.use_auth.get():
                server.login(self.smtp_user.get(), self.smtp_password.get())

            server.sendmail(self.sender_email.get(), self.receiver_email.get(), msg.as_string())
            server.quit()
            self.log_message("E-Mail erfolgreich gesendet.")
            return True
        except Exception as e:
            self.log_message(f"Fehler beim Senden der E-Mail: {str(e)}")
            return False

    def start_monitoring(self):
        if self.running:
            return

        self.running = True
        target = self.target.get()
        max_timeouts = self.max_timeouts.get()
        timeouts = 0

        for child in self.root.winfo_children():
            if isinstance(child, ttk.Button):
                if child.cget("text") == "Überwachung starten":
                    child.config(state="disabled")
                elif child.cget("text") == "Überwachung stoppen":
                    child.config(state="normal")
        self.status_label.config(text="Status: Überwachung läuft...")

        def monitor():
            nonlocal timeouts
            if not self.running:
                return
            success, response_time, reason = self.ping(target)
            if not success:
                timeouts += 1
                self.status_label.config(text=f"Status: Timeout ({timeouts}/{max_timeouts}) - {reason}")
                self.write_timeout_log(target, reason)
                if timeouts >= max_timeouts:
                    self.send_email(
                        f"Netzwerkfehler: {target}",
                        f"Die Zieladresse {target} hat {max_timeouts} Mal den Grenzwert überschritten oder war nicht erreichbar.\n"
                        f"Grund: {reason}\n"
                        f"Maximale Antwortzeit: {self.max_response_time.get()} ms"
                    )
                    timeouts = 0
            else:
                timeouts = 0
                self.status_label.config(text=f"Status: OK (Ping erfolgreich, {response_time:.2f} ms)")
            self.root.after(5000, monitor)

        monitor()

    def stop_monitoring(self):
        self.running = False
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Button):
                if child.cget("text") == "Überwachung starten":
                    child.config(state="normal")
                elif child.cget("text") == "Überwachung stoppen":
                    child.config(state="disabled")
        self.status_label.config(text="Status: Gestoppt")
        self.log_message("Überwachung gestoppt.")

    def save_config(self):
        config = configparser.ConfigParser()
        config["Settings"] = {
            "target": self.target.get(),
            "max_timeouts": str(self.max_timeouts.get()),
            "max_response_time": str(self.max_response_time.get()),
            "ping_size": str(self.ping_size.get()),
            "log_path": self.log_path.get(),
            "ini_path": self.ini_path.get(),
            "smtp_server": self.smtp_server.get(),
            "smtp_port": str(self.smtp_port.get()),
            "use_auth": str(self.use_auth.get()),
            "smtp_user": self.smtp_user.get(),
            "sender_email": self.sender_email.get(),
            "receiver_email": self.receiver_email.get(),
            "encryption": self.encryption.get(),
        }
        with open(self.ini_path.get(), "w") as configfile:
            config.write(configfile)

    def load_config(self):
        if os.path.exists(self.ini_path.get()):
            config = configparser.ConfigParser()
            config.read(self.ini_path.get())
            settings = config["Settings"]
            self.target.set(settings.get("target", ""))
            self.max_timeouts.set(int(settings.get("max_timeouts", 3)))
            self.max_response_time.set(int(settings.get("max_response_time", 500)))
            self.ping_size.set(int(settings.get("ping_size", 32)))
            self.log_path.set(settings.get("log_path", os.path.join(os.getcwd(), "Logs")))
            self.smtp_server.set(settings.get("smtp_server", ""))
            self.smtp_port.set(int(settings.get("smtp_port", 25)))
            self.use_auth.set(settings.getboolean("use_auth", False))
            self.smtp_user.set(settings.get("smtp_user", ""))
            self.sender_email.set(settings.get("sender_email", ""))
            self.receiver_email.set(settings.get("receiver_email", ""))
            self.encryption.set(settings.get("encryption", "Unverschlüsselt"))

    def on_close(self):
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkMonitor(root)
    root.mainloop()
