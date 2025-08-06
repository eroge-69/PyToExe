import tkinter as tk
from tkinter import messagebox
import csv
import threading
import subprocess
import time
from collections import defaultdict
import platform
import ipaddress
import concurrent.futures
import sys
import json

# Konfigurationsdateien
CONFIG_FILE = "devices.csv"
SETTINGS_FILE = "settings.json"

class PingTool:
    def __init__(self, master):
        """
        Initialisiert die PingTool-Anwendung.

        Args:
            master: Das Haupt-Tkinter-Fenster (Tk-Instanz).
        """
        self.master = master
        self.master.title("Ping Monitor")
        self.master.configure(bg="#2d2d2d") # Dunkler Hintergrund für das Hauptfenster

        # Standardeinstellungen und Zustandsvariablen
        self.interval = 5 # Standard-Ping-Intervall in Sekunden
        self.pinging = True # Steuert, ob der Ping-Loop aktiv ist
        self.devices_by_room = defaultdict(list) # Speichert Geräte, gruppiert nach Räumen
        self.device_widgets = {} 
        self.room_frames = {}    # Speichert Referenzen auf die Frames, den Toggle-Button und die Status-LED jedes Raumes
        self.room_states = {}    # Speichert den Sichtbarkeitsstatus (eingeklappt/ausgeklappt) jedes Raumes

        # NEU: Einstellungen für den Nachtmodus
        self.night_mode_active = False 
        self.manual_interval_before_night_mode = 5 # Speichert das manuelle Intervall, bevor der Nachtmodus aktiviert wird

        # === TOP AREA: Steuerungselemente ===
        self.top_frame = tk.Frame(master, bg="#2d2d2d")
        self.top_frame.pack(pady=5, anchor="w")

        # Schaltfläche zum Hinzufügen eines Geräts
        self.add_button = tk.Button(self.top_frame, text="+", command=self.add_device_dialog,
                                    bg="#555", fg="white", font=("Arial", 12, "bold"), width=2,
                                    cursor="hand2") # Mauszeiger ändert sich beim Überfahren
        self.add_button.pack(side="left", padx=(10, 10))

        # Schaltfläche zum Starten/Pausieren des Pings
        # Initialer Zustand: Pinging ist True, also Pause-Symbol anzeigen
        self.play_pause_button = tk.Button(self.top_frame, text="||", font=("Arial", 12), # Pause-Symbol
                                           bg="#28a745", fg="white", width=4, command=self.toggle_ping, # Grüner Hintergrund für "playing"
                                           cursor="hand2")
        self.play_pause_button.pack(side="left")

        # Schieberegler für das Ping-Intervall
        self.interval_slider = tk.Scale(self.top_frame, from_=1, to=60, orient="horizontal",
                                        label="Intervall (s)", command=self.update_interval,
                                        bg="#2d2d2d", fg="white", highlightthickness=0,
                                        troughcolor="#444") # Farbe des Schiebereglers
        self.interval_slider.set(self.interval) # Setzt den Anfangswert
        self.interval_slider.pack(side="left", padx=10)

        # === SCROLLABLE AREA: Bereich für die Gerätelisten ===
        self.canvas = tk.Canvas(master, bg="#2d2d2d", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(master, orient="vertical", command=self.canvas.yview)

        # Frame, der alle Raum-Sektionen enthält und scrollbar ist
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2d2d2d")
        # Erstellt ein "Fenster" auf dem Canvas, in das der scrollable_frame platziert wird
        self.scrollable_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Bindet das Configure-Ereignis des scrollable_frame, um den Scrollbereich des Canvas zu aktualisieren
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        # Bindet das Configure-Ereignis des Canvas, um die Breite des scrollable_frame anzupassen
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.canvas.configure(yscrollcommand=self.scrollbar.set) # Verbindet Scrollbar mit Canvas

        self.canvas.pack(side="left", fill="both", expand=True) # Canvas füllt den verfügbaren Platz
        self.scrollbar.pack(side="right", fill="y") # Scrollbar füllt die vertikale Höhe

        # === STATUS BAR: Anzeige der Online-/Offline-Zahlen ===
        self.status_frame = tk.Frame(master, bg="#2d2d2d")
        self.status_frame.pack(side="bottom", fill="x", pady=5, padx=10)
        self.status_label = tk.Label(self.status_frame, text="Online: 0 | Offline: 0", bg="#2d2d2d", fg="white", font=("Arial", 10))
        self.status_label.pack(side="left")

        # Lädt Einstellungen und Geräte
        self.load_settings()
        self.load_devices()
        self.create_ui()
        self._update_interval_ui_state() # Aktualisiert den Zustand des Schiebereglers basierend auf geladenen Einstellungen

        # NEU: Menüleiste nach allen anderen Initialisierungen erstellen
        self.create_menubar() 

        # Startet den Ping-Loop in einem separaten Daemon-Thread
        self.ping_thread = threading.Thread(target=self.ping_loop, daemon=True)
        self.ping_thread.start()

    def create_menubar(self):
        """Erstellt die Menüleiste am oberen Rand des Fensters."""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar) # Weist die Menüleiste dem Hauptfenster zu

        # "Datei" Menü
        file_menu = tk.Menu(menubar, tearoff=0, bg="#3a3a3a", fg="white")
        menubar.add_cascade(label="Datei", menu=file_menu)

        file_menu.add_command(label="Einstellungen", command=self.open_settings_dialog)
        file_menu.add_separator() 
        file_menu.add_command(label="Beenden", command=self.on_closing) # Ruft die Beenden-Funktion auf

        # "Hilfe" Menü
        help_menu = tk.Menu(menubar, tearoff=0, bg="#3a3a3a", fg="white")
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Benutzeroberfläche Info", command=self.show_ui_info_dialog)
        help_menu.add_command(label="Über", command=self.show_about_dialog)

        # Bindet die on_closing-Funktion an das Schließen des Fensters
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Wird aufgerufen, wenn das Fenster geschlossen wird. Fragt nach Bestätigung."""
        if messagebox.askokcancel("Beenden", "Möchten Sie die Anwendung wirklich beenden?"):
            self.master.destroy() # Zerstört das Hauptfenster und beendet die Anwendung
            sys.exit(0) # Beendet den Python-Prozess sauber

    def load_settings(self):
        """Lädt Einstellungen aus der settings.json-Datei."""
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                self.night_mode_active = settings.get("night_mode_active", False)
                self.manual_interval_before_night_mode = settings.get("manual_interval_before_night_mode", 5)
                # Setzt das aktuelle Intervall basierend auf dem Nachtmodus
                self.interval = 120 if self.night_mode_active else self.manual_interval_before_night_mode
        except FileNotFoundError:
            print(f"'{SETTINGS_FILE}' nicht gefunden. Standardeinstellungen werden verwendet.")
            self.night_mode_active = False
            self.manual_interval_before_night_mode = 5
            self.interval = 5
        except json.JSONDecodeError:
            print(f"Fehler beim Lesen von '{SETTINGS_FILE}'. Datei ist möglicherweise beschädigt.")
            self.night_mode_active = False
            self.manual_interval_before_night_mode = 5
            self.interval = 5
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Einstellungen: {e}")

    def save_settings(self):
        """Speichert Einstellungen in der settings.json-Datei."""
        settings = {
            "night_mode_active": self.night_mode_active,
            "manual_interval_before_night_mode": self.manual_interval_before_night_mode
        }
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Einstellungen: {e}")

    def open_settings_dialog(self):
        """Öffnet den Dialog für Einstellungen."""
        popup = tk.Toplevel(self.master)
        popup.title("Einstellungen")
        popup.configure(bg="#2d2d2d")
        popup.transient(self.master)
        popup.grab_set()

        # Variable für den Checkbutton-Zustand
        night_mode_var = tk.BooleanVar(value=self.night_mode_active)

        # Checkbutton für den Nachtmodus
        night_mode_checkbox = tk.Checkbutton(popup, text="Nachtmodus (Intervall: 120s)", 
                                             variable=night_mode_var,
                                             bg="#2d2d2d", fg="white", selectcolor="#444",
                                             font=("Arial", 10), cursor="hand2")
        night_mode_checkbox.pack(pady=10, padx=10, anchor="w")

        def apply_settings():
            self.night_mode_active = night_mode_var.get()

            if self.night_mode_active:
                self.interval = 120 # Festes Intervall für den Nachtmodus
            else:
                # Wenn Nachtmodus deaktiviert wird, kehre zum manuellen Intervall zurück
                self.interval = self.manual_interval_before_night_mode
                # Setze den Schieberegler auf diesen Wert
                self.interval_slider.set(self.interval) 

            self._update_interval_ui_state() # Aktualisiere den UI-Zustand des Schiebereglers
            self.save_settings() # Speichere die Einstellungen persistent
            popup.destroy()

        tk.Button(popup, text="Speichern", command=apply_settings, bg="#444", fg="white", cursor="hand2").pack(pady=5)
        tk.Button(popup, text="Abbrechen", command=popup.destroy, bg="#444", fg="white", cursor="hand2").pack(pady=5)

        self.master.wait_window(popup)

    def _update_interval_ui_state(self):
        """
        Aktualisiert den visuellen Zustand des Intervall-Schiebereglers
        basierend auf dem night_mode_active-Status.
        """
        if self.night_mode_active:
            self.interval_slider.config(state="disabled", troughcolor="#666", 
                                        label="Intervall (s) - Nachtmodus aktiv")
            self.interval_slider.set(120) # Visuell auf 120 setzen
        else:
            self.interval_slider.config(state="normal", troughcolor="#444", 
                                        label="Intervall (s)")
            self.interval_slider.set(self.manual_interval_before_night_mode) # Setzt den Schieberegler auf den gespeicherten Wert

    def show_ui_info_dialog(self):
        """Zeigt eine Info-Box zur Benutzeroberfläche an."""
        info_text = (
            "Willkommen beim Ping Monitor!\n\n"
            "Dies ist eine kurze Anleitung zur Benutzeroberfläche:\n\n"
            "• '+' Button: Fügt ein neues Gerät zur Überwachung hinzu.\n"
            "• '||' / '▶' Button: Startet oder pausiert die Ping-Überwachung.\n"
            "  (Grün: Aktiv, Rot: Pausiert)\n"
            "• 'Intervall (s)' Schieberegler: Stellt ein, wie oft Geräte angepingt werden.\n"
            "  (Ausgegraut im Nachtmodus)\n\n"
            "• Raum-Sektionen:\n"
            "  • '▼' / '▶' Button: Klappt die Geräteliste eines Raumes ein oder aus.\n"
            "  • Großer Kreis (●) neben dem Raumnamen: Zeigt den Status des Raumes an.\n"
            "    (Grün: Alle Geräte online, Rot: Mindestens ein Gerät offline)\n"
            "  • Kleiner Kreis (●) neben jedem Gerät: Zeigt den Status des einzelnen Geräts an.\n"
            "    (Grün: Online, Rot: Offline)\n"
            "  • Zahnrad (⚙️) Button: Öffnet ein Menü zum Bearbeiten oder Löschen des Geräts.\n\n"
            "• Statusleiste unten: Zeigt die Gesamtzahl der Online- und Offline-Geräte an.\n\n"
            "• Menüleiste (oben):\n"
            "  • 'Datei' -> 'Einstellungen': Hier können Sie den 'Nachtmodus' aktivieren.\n"
            "  • 'Datei' -> 'Beenden': Schließt die Anwendung.\n"
            "  • 'Hilfe' -> 'Benutzeroberfläche Info': Diese Informationsbox.\n"
            "  • 'Hilfe' -> 'Über': Informationen zur Anwendung."
        )
        messagebox.showinfo("Benutzeroberfläche Info", info_text)

    def show_about_dialog(self):
        """Zeigt einen 'Über'-Dialog an."""
        messagebox.showinfo("Über Ping Monitor", 
                            "Ping Monitor v1.0\n\n"
                            "Ein einfaches Tool zur Überwachung von Netzwerkgeräten.\n"
                            "Erstellt mit Python und Tkinter.")


    def on_canvas_resize(self, event):
        """
        Passt die Breite des scrollbaren Frames an die Breite des Canvas an.
        Wird aufgerufen, wenn sich die Größe des Canvas ändert (z.B. durch Fenstergröße).
        """
        self.canvas.update_idletasks() 
        self.canvas.itemconfig(self.scrollable_frame_id, width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _is_valid_ip(self, ip_string):
        """
        Prüft, ob eine gegebene Zeichenkette eine gültige IPv4-Adresse ist.
        """
        try:
            ipaddress.IPv4Address(ip_string)
            return True
        except ipaddress.AddressValueError:
            return False
        except Exception as e:
            print(f"Unerwarteter Fehler bei IP-Validierung: {e}")
            return False

    def load_devices(self):
        """Lädt Gerätekonfigurationen aus der CSV-Datei."""
        try:
            with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    device_data = {
                        "IP": row.get("IP", ""),
                        "Raum": row.get("Raum", ""),
                        "Name": row.get("Name", ""),
                        "Typ": row.get("Typ", "")
                    }
                    if self._is_valid_ip(device_data["IP"]):
                        self.devices_by_room[device_data["Raum"]].append(device_data)
                    else:
                        print(f"Ungültige IP-Adresse in CSV übersprungen: {device_data['IP']}")
        except FileNotFoundError:
            print(f"'{CONFIG_FILE}' nicht gefunden. Eine neue Datei wird beim Speichern erstellt.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Geräte: {e}")

    def save_devices(self):
        """Speichert die aktuellen Gerätekonfigurationen in der CSV-Datei."""
        fieldnames = ["IP", "Raum", "Name", "Typ"]
        try:
            with open(CONFIG_FILE, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for room in sorted(self.devices_by_room.keys()):
                    for dev in self.devices_by_room[room]:
                        writer.writerow(dev)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Geräte: {e}")

    def create_ui(self):
        """Erstellt die anfängliche Benutzeroberfläche basierend auf den geladenen Geräten."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.device_widgets = {} 
        self.room_frames = {}
        self.room_states = {}

        for room in sorted(self.devices_by_room.keys()):
            self._add_room_section_to_ui(room)

        self.master.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def _add_room_section_to_ui(self, room):
        """
        Hilfsfunktion zum Hinzufügen eines neuen Raumabschnitts zur UI.
        """
        outer_frame = tk.Frame(self.scrollable_frame, bg="#3a3a3a", bd=2, relief="groove")
        outer_frame.pack(fill="x", padx=10, pady=5)

        header = tk.Frame(outer_frame, bg="#3a3a3a")
        header.pack(fill="x")

        toggle_btn = tk.Button(header, text="▼", width=2, bg="#555", fg="white",
                               command=lambda r=room: self.toggle_room(r),
                               cursor="hand2")
        toggle_btn.pack(side="left")

        room_label = tk.Label(header, text=room, bg="#3a3a3a", fg="white", font=("Arial", 12, "bold"))
        room_label.pack(side="left", padx=5)

        room_status_led = tk.Label(header, text="●", font=("Arial", 16), fg="gray", bg="#3a3a3a")
        room_status_led.pack(side="right", padx=5)

        devices_frame = tk.Frame(outer_frame, bg="#2d2d2d")
        devices_frame.pack(fill="x", padx=10, pady=5)

        self.room_states[room] = True
        self.room_frames[room] = (outer_frame, devices_frame, toggle_btn, room_status_led) 

        if self.devices_by_room[room]: 
            header_row = tk.Frame(devices_frame, bg="#2d2d2d")
            header_row.pack(fill="x", pady=(0, 5))

            tk.Label(header_row, text="", width=4, bg="#2d2d2d").pack(side="left", padx=5) 
            tk.Label(header_row, text="Name (Typ) - IP", bg="#2d2d2d", fg="#aaaaaa", font=("Arial", 10, "bold"), anchor="w").pack(side="left", expand=True, fill="x")
            tk.Label(header_row, text="", width=4, bg="#2d2d2d").pack(side="right", padx=5) 

        self.device_widgets[room] = {} 
        for dev in self.devices_by_room[room]:
            w = self._add_device_widget_to_ui(devices_frame, dev)
            self.device_widgets[room][dev["IP"]] = w

        self.master.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def _add_device_widget_to_ui(self, parent, device):
        """
        Hilfsfunktion zum Hinzufügen eines neuen Geräte-Widgets zu einem Raum-Frame.
        """
        row = tk.Frame(parent, bg="#2d2d2d")
        row.pack(fill="x", pady=2)

        dot = tk.Label(row, text="●", font=("Arial", 12), fg="gray", bg="#2d2d2d")
        dot.pack(side="left", padx=5)

        label_text = f'{device["Name"]} ({device["Typ"]}) - {device["IP"]}'
        label = tk.Label(row, text=label_text, bg="#2d2d2d", fg="white", anchor="w")
        label.pack(side="left", expand=True, fill="x")

        settings_button = tk.Button(row, text="⚙️", command=lambda d=device: self.open_edit_device_dialog(d),
                                  bg="#555", fg="white", font=("Arial", 10), width=2,
                                  cursor="hand2")
        settings_button.pack(side="right", padx=5)

        return dot

    def update_interval(self, val):
        """
        Aktualisiert das Ping-Intervall basierend auf dem Wert des Schiebereglers.
        Wird nur ausgeführt, wenn der Nachtmodus NICHT aktiv ist.
        """
        if not self.night_mode_active:
            self.interval = int(val)
            self.manual_interval_before_night_mode = self.interval
            self.save_settings()

    def toggle_ping(self):
        """
        Schaltet den Ping-Zustand um (aktiv/pausiert) und aktualisiert die Schaltfläche.
        """
        self.pinging = not self.pinging
        if self.pinging:
            self.play_pause_button.config(text="||", fg="white", bg="#28a745")
        else:
            self.play_pause_button.config(text="▶", fg="white", bg="#dc3545")

    def ping_loop(self):
        """
        Hintergrund-Thread-Loop für das Pingen von Geräten.
        """
        while True:
            if self.pinging:
                self.master.after(0, self.check_all_devices)
            time.sleep(self.interval)

    def check_all_devices(self):
        """
        Prüft alle Geräte und aktualisiert deren Status in der UI.
        Pingt Geräte innerhalb jedes Raumes parallel.
        """
        total_online = 0
        total_offline = 0

        MAX_WORKERS_PER_ROOM = 10 

        for room in sorted(self.devices_by_room.keys()):
            devices_in_room = self.devices_by_room[room]

            if not devices_in_room:
                outer_frame, _, _, room_status_led = self.room_frames[room]
                outer_frame.config(bg="#3a3a3a") 
                room_status_led.config(fg="green")
                continue

            room_errors = 0

            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_PER_ROOM) as executor:
                future_to_ip = {executor.submit(self.ping, dev["IP"]): dev["IP"] for dev in devices_in_room}

                for future in concurrent.futures.as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        alive = future.result()

                        dot_widget = self.device_widgets[room].get(ip)
                        if dot_widget:
                            dot_widget.config(fg="green" if alive else "red")

                        if not alive:
                            room_errors += 1
                            total_offline += 1
                        else:
                            total_online += 1
                    except Exception as exc:
                        print(f'Ping für {ip} hat eine Ausnahme ausgelöst: {exc}')
                        dot_widget = self.device_widgets[room].get(ip)
                        if dot_widget:
                            dot_widget.config(fg="red")
                        room_errors += 1
                        total_offline += 1

            outer_frame, _, _, room_status_led = self.room_frames[room]
            outer_frame.config(bg="#3a3a3a" if room_errors == 0 else "#552222")
            room_status_led.config(fg="green" if room_errors == 0 else "red")

        self.status_label.config(text=f"Online: {total_online} | Offline: {total_offline}")

    def ping(self, ip):
        """
        Führt einen einzelnen Ping an die angegebene IP-Adresse aus.
        """
        param = "-n" if platform.system().lower() == "windows" else "-c"
        try:
            result = subprocess.run(["ping", param, "1", ip],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    check=False)
            return result.returncode == 0
        except FileNotFoundError:
            print("Fehler: 'ping'-Befehl nicht gefunden. Stellen Sie sicher, dass er im System-PATH ist.")
            return False
        except Exception as e:
            print(f"Fehler beim Pingen von {ip}: {e}")
            return False

    def toggle_room(self, room):
        """
        Schaltet die Sichtbarkeit der Geräteliste eines Raumes um (ein-/ausklappen).
        """
        outer_frame, dev_frame, toggle_btn, _ = self.room_frames[room]
        visible = self.room_states[room]
        if visible:
            dev_frame.forget()
            toggle_btn.config(text="▶")
        else:
            dev_frame.pack(fill="x", padx=10, pady=5)
            toggle_btn.config(text="▼")
        self.room_states[room] = not visible
        self.master.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def add_device_dialog(self):
        """Öffnet einen Dialog zum Hinzufügen eines neuen Geräts."""
        popup = tk.Toplevel(self.master)
        popup.title("Gerät hinzufügen")
        popup.configure(bg="#2d2d2d")
        popup.transient(self.master)
        popup.grab_set()

        entries = {}
        for i, label_text in enumerate(["IP", "Raum", "Name", "Typ"]):
            tk.Label(popup, text=label_text, bg="#2d2d2d", fg="white").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            entry = tk.Entry(popup, bg="#444", fg="white", insertbackground="white")
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            entries[label_text] = entry

        popup.grid_columnconfigure(1, weight=1)

        def submit():
            new_device = {key: entries[key].get().strip() for key in entries}

            if not self._is_valid_ip(new_device["IP"]):
                messagebox.showerror("Fehler", "Ungültige IP-Adresse. Bitte geben Sie eine gültige IPv4-Adresse ein.")
                return

            if all(new_device.values()):
                self.devices_by_room[new_device["Raum"]].append(new_device)
                self.save_devices()
                popup.destroy()
                self.update_ui_after_device_change()
            else:
                messagebox.showwarning("Fehler", "Bitte alle Felder ausfüllen!")

        tk.Button(popup, text="Abbrechen", command=popup.destroy, bg="#444", fg="white", cursor="hand2").grid(row=4, column=0, pady=10, padx=5)
        tk.Button(popup, text="Hinzufügen", command=submit, bg="#444", fg="white", cursor="hand2").grid(row=4, column=1, pady=10, padx=5)

        self.master.wait_window(popup)

    def open_edit_device_dialog(self, device_to_edit):
        """
        Öffnet einen Dialog zum Bearbeiten oder Löschen eines bestehenden Geräts.
        """
        popup = tk.Toplevel(self.master)
        popup.title("Gerät bearbeiten/löschen")
        popup.configure(bg="#2d2d2d")
        popup.transient(self.master)
        popup.grab_set()

        entries = {}
        for i, label_text in enumerate(["IP", "Raum", "Name", "Typ"]):
            tk.Label(popup, text=label_text, bg="#2d2d2d", fg="white").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            entry = tk.Entry(popup, bg="#444", fg="white", insertbackground="white")
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            entry.insert(0, device_to_edit[label_text])
            entries[label_text] = entry

        popup.grid_columnconfigure(1, weight=1)

        def save_changes():
            updated_device = {key: entries[key].get().strip() for key in entries}

            if not self._is_valid_ip(updated_device["IP"]):
                messagebox.showerror("Fehler", "Ungültige IP-Adresse. Bitte geben Sie eine gültige IPv4-Adresse ein.")
                return

            if all(updated_device.values()):
                old_room = device_to_edit["Raum"]
                if old_room in self.devices_by_room and device_to_edit in self.devices_by_room[old_room]:
                    self.devices_by_room[old_room].remove(device_to_edit)
                    if not self.devices_by_room[old_room]:
                        del self.devices_by_room[old_room]

                self.devices_by_room[updated_device["Raum"]].append(updated_device)

                self.save_devices()
                popup.destroy()
                self.update_ui_after_device_change()
            else:
                messagebox.showwarning("Fehler", "Bitte alle Felder ausfüllen!")

        def delete_device_from_dialog():
            popup.destroy()
            self.confirm_delete_device(device_to_edit)

        tk.Button(popup, text="Speichern", command=save_changes, bg="#444", fg="white", cursor="hand2").grid(row=4, column=0, pady=10, padx=5, sticky="ew")
        tk.Button(popup, text="Löschen", command=delete_device_from_dialog, bg="#663333", fg="white", cursor="hand2").grid(row=4, column=1, pady=10, padx=5, sticky="ew")
        tk.Button(popup, text="Abbrechen", command=popup.destroy, bg="#444", fg="white", cursor="hand2").grid(row=5, columnspan=2, pady=5, padx=5, sticky="ew")

        self.master.wait_window(popup)

    def update_ui_after_device_change(self):
        """
        Erstellt die gesamte UI neu, um Änderungen widerzuspiegeln (z.B. nach dem Hinzufügen/Löschen eines Geräts).
        """
        self.create_ui()

    def confirm_delete_device(self, device_to_delete):
        """
        Fragt nach Bestätigung, bevor ein Gerät gelöscht wird.
        """
        confirm = messagebox.askyesno(
            "Gerät löschen",
            f"Möchten Sie das Gerät '{device_to_delete['Name']} ({device_to_delete['IP']})' wirklich löschen?"
        )
        if confirm:
            self.delete_device(device_to_delete)

    def delete_device(self, device_to_delete):
        """
        Löscht ein Gerät aus den Daten und aktualisiert die UI.
        """
        room = device_to_delete["Raum"]
        if room in self.devices_by_room:
            if device_to_delete in self.devices_by_room[room]:
                self.devices_by_room[room].remove(device_to_delete)

            if not self.devices_by_room[room]:
                del self.devices_by_room[room]
                if room in self.room_frames:
                    self.room_frames[room][0].destroy()
                    del self.room_frames[room]
                    del self.room_states[room]
                    del self.device_widgets[room]

            self.save_devices()
            self.update_ui_after_device_change()


def main():
    """Startpunkt der Anwendung."""
    root = tk.Tk()
    app = PingTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
