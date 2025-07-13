# === IMPORTATIONS ===
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import serial
import serial.tools.list_ports
import threading
import time
import json
from math import radians
from vpython import *
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

try:
    import winsound  # Windows son (optionnel)
except ImportError:
    winsound = None


# === CONSTANTES ===
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 1
SERVO_COUNT = 7


# === MULTI LANGUES SIMPLE ===
LANGUAGES = {
    "fr": {
        "connexion": "Connexion à l'Arduino",
        "connecter": "Se connecter",
        "deconnecter": "Déconnecter",
        "non_connecte": "Non connecté",
        "connecte": "Connecté à",
        "controle": "Contrôle manuel",
        "positions_favorites": "Positions favorites:",
        "appliquer": "Appliquer",
        "sauvegarder_position": "Sauvegarder position",
        "calibration": "Calibration automatique",
        "simulation_3d": "Simulation 3D",
        "programmation_mouvements": "Programmation des mouvements",
        "ajouter_position": "Ajouter la position actuelle",
        "lire_sequence": "Lire la séquence",
        "enregistrer_programme": "Enregistrer le programme",
        "charger_programme": "Charger un programme",
        "logs": "Logs",
        "mode_demo": "Mode Démo",
        "erreur_connexion": "Erreur de connexion",
        "tentative_reconnexion": "Tentative de reconnexion...",
        "reconnexion_echouee": "Reconnexion échouée",
        "perte_communication": "Perte de communication avec Arduino.",
        "nom_position_favorite": "Entrez le nom :",
    },
    "en": {
        "connexion": "Arduino Connection",
        "connecter": "Connect",
        "deconnecter": "Disconnect",
        "non_connecte": "Not connected",
        "connecte": "Connected to",
        "controle": "Manual Control",
        "positions_favorites": "Favorite positions:",
        "appliquer": "Apply",
        "sauvegarder_position": "Save position",
        "calibration": "Auto Calibration",
        "simulation_3d": "3D Simulation",
        "programmation_mouvements": "Movement Programming",
        "ajouter_position": "Add current position",
        "lire_sequence": "Play sequence",
        "enregistrer_programme": "Save program",
        "charger_programme": "Load program",
        "logs": "Logs",
        "mode_demo": "Demo Mode",
        "erreur_connexion": "Connection error",
        "tentative_reconnexion": "Reconnection attempt...",
        "reconnexion_echouee": "Reconnection failed",
        "perte_communication": "Lost communication with Arduino.",
        "nom_position_favorite": "Enter name:",
    }
}


# === CLASSE PRINCIPALE ===
class RobotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PolyScope - Contrôle du bras robotisé")
        self.state('zoomed')  # plein écran
        self.configure(bg="#1e1e1e")

        self.serial_conn = None
        self.read_thread = None
        self.read_thread_running = False
        self.reconnect_attempts = 0
        self.position_favorites = {}  # nom -> liste positions
        self.lang = "fr"
        self.demo_mode = False

        # Queue pour angles en temps réel (graphe)
        self.queue_angles = queue.Queue()

        # === MENU LANGUES ===
        self.create_lang_menu()

        # Menu latéral gauche
        self.navbar = tk.Frame(self, bg="#2c3e50", width=220)
        self.navbar.pack(side="left", fill="y")
        self.container = tk.Frame(self, bg="#2e2e2e")
        self.container.pack(side="right", expand=True, fill="both")

        self.frames = {}
        for Page in (ConnexionPage, ControlePage, Simulation3DPage, ProgrammationPage, LogPage, GraphiqueTempsReelPage):
            frame = Page(self.container, self)
            self.frames[Page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Boutons nav + bouton mode demo
        self.add_nav_button("🔌 Connexion", ConnexionPage)
        self.add_nav_button("🎮 Contrôle", ControlePage)
        self.add_nav_button("🖼️ Simulation", Simulation3DPage)
        self.add_nav_button("🎬 Programme", ProgrammationPage)
        self.add_nav_button("📈 Graphiques", GraphiqueTempsReelPage)
        self.add_nav_button("📝 Logs", LogPage)
        demo_btn = tk.Button(self.navbar, text=self._t("mode_demo"), bg="#34495e", fg="white",
                             font=("Arial", 12), relief="flat", command=self.toggle_demo_mode)
        demo_btn.pack(fill="x", pady=2)

        # Barre de statut en bas
        self.status_bar = tk.Label(self, text=self._t("non_connecte"), bg="#2c3e50", fg="white", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

        self.show_frame(ConnexionPage)

    def add_nav_button(self, text, page):
        btn = tk.Button(self.navbar, text=text, bg="#34495e", fg="white", font=("Arial", 12), relief="flat",
                        command=lambda: self.show_frame(page))
        btn.pack(fill="x", pady=2)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

    def _t(self, key):
        """Traduction simple"""
        return LANGUAGES.get(self.lang, LANGUAGES["fr"]).get(key, key)

    def set_language(self, lang_code):
        self.lang = lang_code
        for frame in self.frames.values():
            if hasattr(frame, "update_text"):
                frame.update_text(self.lang)
        self.status_bar.config(text=self._t("non_connecte"))
        # Mise à jour bouton mode demo aussi
        for widget in self.navbar.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") in [LANGUAGES["fr"]["mode_demo"], LANGUAGES["en"]["mode_demo"]]:
                widget.config(text=self._t("mode_demo"))

    def create_lang_menu(self):
        menubar = tk.Menu(self)
        langmenu = tk.Menu(menubar, tearoff=0)
        langmenu.add_command(label="Français", command=lambda: self.set_language("fr"))
        langmenu.add_command(label="English", command=lambda: self.set_language("en"))
        menubar.add_cascade(label="Language", menu=langmenu)
        self.config(menu=menubar)

    def toggle_demo_mode(self):
        self.demo_mode = not self.demo_mode
        status = "Activé" if self.demo_mode else "Désactivé"
        self.frames[LogPage].ajouter_log(f"Mode Démo {status}")
        if self.demo_mode:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            self.serial_conn = None
            self.status_bar.config(text=self._t("non_connecte"))
        else:
            # On pourrait tenter reconnexion ou demander utilisateur
            self.frames[LogPage].ajouter_log("Mode Démo désactivé. Connectez-vous pour contrôler le robot.")

    def start_read_thread(self):
        if not self.read_thread_running and self.serial_conn and self.serial_conn.is_open:
            self.read_thread_running = True
            self.read_thread = threading.Thread(target=self.read_serial_loop, daemon=True)
            self.read_thread.start()

    def stop_read_thread(self):
        self.read_thread_running = False
        if self.read_thread:
            self.read_thread.join(timeout=1)
            self.read_thread = None

    def read_serial_loop(self):
        log_frame = self.frames[LogPage]
        while self.read_thread_running:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode(errors='ignore').strip()
                    if line:
                        log_frame.ajouter_log(f"Arduino >> {line}")
                        # Si ligne contient angles, on peut parser et envoyer à graphe
                        # Exemple format: "ANGLES:0,90,45,0,0,0,0"
                        if line.startswith("ANGLES:"):
                            try:
                                parts = line.split(":")[1].split(",")
                                angles = [int(p) for p in parts]
                                if len(angles) == SERVO_COUNT:
                                    self.queue_angles.put((time.time(), angles))
                            except:
                                pass
            except Exception as e:
                log_frame.ajouter_log(f"{self._t('erreur_connexion')} : {e}")
                self.reconnect_attempts += 1
                if self.reconnect_attempts < 5:
                    log_frame.ajouter_log(self._t("tentative_reconnexion"))
                    time.sleep(2)
                    try:
                        if self.serial_conn:
                            self.serial_conn.close()
                            self.serial_conn.open()
                        self.reconnect_attempts = 0
                    except Exception as e2:
                        log_frame.ajouter_log(f"{self._t('reconnexion_echouee')} : {e2}")
                        if self.reconnect_attempts >= 5:
                            if winsound:
                                winsound.Beep(1000, 500)
                            messagebox.showerror("Erreur", self._t("perte_communication"))
                            self.stop_read_thread()
                            self.serial_conn = None
                            self.status_bar.config(text=self._t("non_connecte"))
                else:
                    self.stop_read_thread()
            time.sleep(0.1)


# === PAGE CONNEXION ===
class ConnexionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller

        self.label = ttk.Label(self, text=self.controller._t("connexion"), font=("Arial", 20))
        self.label.pack(pady=20)

        self.port_combo = ttk.Combobox(self, values=self.list_ports())
        self.port_combo.pack(pady=5)

        self.connect_btn = ttk.Button(self, text=self.controller._t("connecter"), command=self.connect)
        self.connect_btn.pack(pady=10)

        self.disconnect_btn = ttk.Button(self, text=self.controller._t("deconnecter"), command=self.disconnect)
        self.disconnect_btn.pack(pady=5)

        self.status = ttk.Label(self, text=self.controller._t("non_connecte"))
        self.status.pack(pady=10)

        self.refresh_ports_btn = ttk.Button(self, text="↻ Refresh Ports", command=self.refresh_ports)
        self.refresh_ports_btn.pack()

    def list_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def refresh_ports(self):
        self.port_combo['values'] = self.list_ports()
        self.controller.frames[LogPage].ajouter_log("Ports série rafraîchis")

    def connect(self):
        try:
            port = self.port_combo.get()
            if not port:
                messagebox.showwarning("Attention", "Sélectionnez un port série valide.")
                return
            self.controller.serial_conn = serial.Serial(port, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
            self.status.config(text=f"{self.controller._t('connecte')} {port}")
            self.controller.status_bar.config(text=f"{self.controller._t('connecte')} {port}")
            self.controller.frames[LogPage].ajouter_log(f"Connecté à {port}")
            self.controller.start_read_thread()
        except Exception as e:
            messagebox.showerror(self.controller._t("erreur_connexion"), str(e))
            self.controller.frames[LogPage].ajouter_log(f"Erreur connexion: {e}")

    def disconnect(self):
        if self.controller.serial_conn and self.controller.serial_conn.is_open:
            self.controller.serial_conn.close()
            self.status.config(text=self.controller._t("non_connecte"))
            self.controller.status_bar.config(text=self.controller._t("non_connecte"))
            self.controller.frames[LogPage].ajouter_log("Déconnecté.")
            self.controller.stop_read_thread()


    def update_text(self, lang):
        self.label.config(text=self.controller._t("connexion"))
        self.connect_btn.config(text=self.controller._t("connecter"))
        self.disconnect_btn.config(text=self.controller._t("deconnecter"))
        self.status.config(text=self.controller._t("non_connecte"))
        self.refresh_ports_btn.config(text="↻ Refresh Ports")


# === PAGE CONTROLE ===
class ControlePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller

        self.title_label = tk.Label(self, text=self.controller._t("controle"), font=("Arial", 18), fg="white", bg="#2e2e2e")
        self.title_label.pack(pady=10)

        self.sliders = []
        self.value_labels = []

        for i in range(SERVO_COUNT):
            frame = tk.Frame(self, bg="#2e2e2e")
            frame.pack(pady=3, fill="x", padx=20)
            tk.Label(frame, text=f"Servo {i+1}", bg="#2e2e2e", fg="white", width=8).pack(side="left")
            slider = tk.Scale(frame, from_=0, to=180, orient="horizontal",
                              command=lambda val, idx=i: self.move_servo(idx, val),
                              bg="#1e1e1e", fg="white", troughcolor="#3498db", highlightthickness=0, length=400)
            slider.pack(side="left")
            self.sliders.append(slider)
            val_label = tk.Label(frame, text="90", bg="#2e2e2e", fg="white", width=4)
            val_label.pack(side="left", padx=5)
            self.value_labels.append(val_label)

            # Boutons + et -
            btn_frame = tk.Frame(frame, bg="#2e2e2e")
            btn_frame.pack(side="left", padx=10)
            btn_plus = tk.Button(btn_frame, text="+", width=2, command=lambda idx=i: self.increment_servo(idx, 5))
            btn_plus.pack(side="left")
            btn_minus = tk.Button(btn_frame, text="-", width=2, command=lambda idx=i: self.increment_servo(idx, -5))
            btn_minus.pack(side="left")

            slider.set(90)
            self.value_labels[i].config(text="90")

        # Positions favorites
        fav_frame = tk.Frame(self, bg="#2e2e2e")
        fav_frame.pack(pady=15)
        tk.Label(fav_frame, text=self.controller._t("positions_favorites"), bg="#2e2e2e", fg="white").pack(side="left")
        self.fav_combo = ttk.Combobox(fav_frame, values=list(controller.position_favorites.keys()), state="readonly", width=30)
        self.fav_combo.pack(side="left", padx=5)
        tk.Button(fav_frame, text=self.controller._t("appliquer"), command=self.appliquer_favorite).pack(side="left", padx=5)
        tk.Button(fav_frame, text=self.controller._t("sauvegarder_position"), command=self.sauvegarder_position_favorite).pack(side="left", padx=5)

        # Calibration
        cal_btn = ttk.Button(self, text=self.controller._t("calibration"), command=self.calibration)
        cal_btn.pack(pady=10)

    def move_servo(self, idx, val):
        val = int(float(val))
        self.value_labels[idx].config(text=str(val))
        if self.controller.demo_mode:
            self.controller.frames[LogPage].ajouter_log(f"[DEMO] Servo {idx+1} réglé à {val}")
            return
        if self.controller.serial_conn and self.controller.serial_conn.is_open:
            try:
                cmd = f"S{idx}:{val}\n"
                self.controller.serial_conn.write(cmd.encode())
                self.controller.frames[LogPage].ajouter_log(f"Envoyé >> {cmd.strip()}")
            except Exception as e:
                self.controller.frames[LogPage].ajouter_log(f"Erreur envoi commande: {e}")

    def increment_servo(self, idx, delta):
        current_val = self.sliders[idx].get()
        new_val = min(180, max(0, current_val + delta))
        self.sliders[idx].set(new_val)

    def appliquer_favorite(self):
        nom = self.fav_combo.get()
        if nom in self.controller.position_favorites:
            pos = self.controller.position_favorites[nom]
            for i, val in enumerate(pos):
                self.sliders[i].set(val)
            self.controller.frames[LogPage].ajouter_log(f"Position favorite '{nom}' appliquée.")

    def sauvegarder_position_favorite(self):
        nom = simpledialog.askstring("Nom position favorite", self.controller._t("nom_position_favorite"))
        if nom:
            pos = [slider.get() for slider in self.sliders]
            self.controller.position_favorites[nom] = pos
            self.fav_combo['values'] = list(self.controller.position_favorites.keys())
            self.controller.frames[LogPage].ajouter_log(f"Position favorite '{nom}' sauvegardée.")

    def calibration(self):
        for slider in self.sliders:
            slider.set(90)
        self.controller.frames[LogPage].ajouter_log("Calibration automatique lancée (positions à 90°).")
        if self.controller.serial_conn and self.controller.serial_conn.is_open:
            for i in range(SERVO_COUNT):
                try:
                    cmd = f"S{i}:90\n"
                    self.controller.serial_conn.write(cmd.encode())
                    self.controller.frames[LogPage].ajouter_log(f"Envoyé >> {cmd.strip()}")
                except Exception as e:
                    self.controller.frames[LogPage].ajouter_log(f"Erreur calibration servo {i} : {e}")

    def update_text(self, lang):
        self.title_label.config(text=self.controller._t("controle"))
        # Mettre à jour labels, boutons
        # positions favorites
        self.fav_combo.set('')
        self.fav_combo['values'] = list(self.controller.position_favorites.keys())


# === PAGE LOGS ===
class LogPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller
        self.text = tk.Text(self, bg="#1e1e1e", fg="white", state="disabled", font=("Consolas", 10))
        self.text.pack(expand=True, fill="both", padx=10, pady=10)

    def ajouter_log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.text.config(state="normal")
        self.text.insert("end", f"[{timestamp}] {msg}\n")
        self.text.see("end")
        self.text.config(state="disabled")

    def update_text(self, lang):
        pass  # Pas de texte statique


# === PAGE SIMULATION 3D ===
class Simulation3DPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller

        # VPython Canvas dans un frame
        self.vpython_frame = tk.Frame(self, bg="#2e2e2e")
        self.vpython_frame.pack(expand=True, fill="both")

        # Initialisation VPython
        self.canvas = canvas(width=700, height=600, background=color.gray(0.15), center=vector(0, 1, 0))
        self.canvas.bind('keydown', self.keydown)
        self.canvas.bind('keyup', self.keyup)

        self.construct_robot()

        # Mise à jour régulière
        self.after(100, self.update_simulation)

    def construct_robot(self):
        # Simplification du bras en segments articulés
        self.base = box(pos=vector(0, 0, 0), size=vector(2, 0.4, 2), color=color.blue)
        self.arm1 = box(pos=vector(0, 1, 0), size=vector(0.5, 2, 0.5), color=color.red)
        self.arm2 = box(pos=vector(0, 3, 0), size=vector(0.4, 1.5, 0.4), color=color.orange)
        self.forearm = box(pos=vector(0, 4.75, 0), size=vector(0.3, 1.5, 0.3), color=color.yellow)
        self.wrist = box(pos=vector(0, 6.5, 0), size=vector(0.2, 0.5, 0.2), color=color.green)
        self.pince_left = box(pos=vector(-0.1, 7, 0), size=vector(0.1, 0.5, 0.1), color=color.gray(0.7))
        self.pince_right = box(pos=vector(0.1, 7, 0), size=vector(0.1, 0.5, 0.1), color=color.gray(0.7))

    def update_simulation(self):
        # TODO: lire angles actuels et appliquer rotations sur les objets 3D
        # Exemple simple: on fait tourner arm1 autour y selon servo 0, etc.

        # Si mode demo ou données angles dispo dans queue
        if not self.controller.queue_angles.empty():
            _, angles = self.controller.queue_angles.get()
            # Pour test : tourner arm1 selon servo 0
            angle_rad = radians(angles[0])
            self.arm1.axis = vector(0, 1, 0).rotate(angle=angle_rad, axis=vector(0, 1, 0))

            # Autres articulations à implémenter selon besoin...

        self.after(100, self.update_simulation)

    def keydown(self, evt):
        pass

    def keyup(self, evt):
        pass

    def update_text(self, lang):
        pass


# === PAGE PROGRAMMATION ===
class ProgrammationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller

        self.title_label = tk.Label(self, text=self.controller._t("programmation_mouvements"), font=("Arial", 18), fg="white", bg="#2e2e2e")
        self.title_label.pack(pady=10)

        self.sequence = []

        self.listbox = tk.Listbox(self, bg="#1e1e1e", fg="white", font=("Consolas", 10))
        self.listbox.pack(expand=True, fill="both", padx=10, pady=10)

        btn_frame = tk.Frame(self, bg="#2e2e2e")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text=self.controller._t("ajouter_position"), command=self.ajouter_position).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.controller._t("lire_sequence"), command=self.lire_sequence).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.controller._t("enregistrer_programme"), command=self.enregistrer_programme).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.controller._t("charger_programme"), command=self.charger_programme).pack(side="left", padx=5)

    def ajouter_position(self):
        # Récupérer positions actuelles des servos
        controle = self.controller.frames[ControlePage]
        positions = [s.get() for s in controle.sliders]
        self.sequence.append(positions)
        self.listbox.insert("end", str(positions))
        self.controller.frames[LogPage].ajouter_log("Position ajoutée à la séquence.")

    def lire_sequence(self):
        if self.controller.demo_mode:
            self.controller.frames[LogPage].ajouter_log("[DEMO] Lecture de la séquence")
            for pos in self.sequence:
                self.controller.frames[LogPage].ajouter_log(f"[DEMO] Position: {pos}")
                time.sleep(0.5)
            return

        if not self.controller.serial_conn or not self.controller.serial_conn.is_open:
            messagebox.showwarning("Attention", "Connectez-vous à l'Arduino d'abord.")
            return

        def play():
            for pos in self.sequence:
                for i, val in enumerate(pos):
                    cmd = f"S{i}:{val}\n"
                    try:
                        self.controller.serial_conn.write(cmd.encode())
                    except Exception as e:
                        self.controller.frames[LogPage].ajouter_log(f"Erreur envoi commande: {e}")
                    time.sleep(0.5)

        threading.Thread(target=play, daemon=True).start()

    def enregistrer_programme(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self.sequence, f)
            self.controller.frames[LogPage].ajouter_log(f"Programme enregistré dans {file_path}")

    def charger_programme(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                self.sequence = json.load(f)
            self.listbox.delete(0, "end")
            for pos in self.sequence:
                self.listbox.insert("end", str(pos))
            self.controller.frames[LogPage].ajouter_log(f"Programme chargé depuis {file_path}")

    def update_text(self, lang):
        self.title_label.config(text=self.controller._t("programmation_mouvements"))


# === PAGE GRAPHIQUE TEMPS REEL ===
class GraphiqueTempsReelPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller

        self.fig, self.ax = plt.subplots(figsize=(8, 4), facecolor='#1e1e1e')
        self.ax.set_facecolor('#2e2e2e')
        self.ax.grid(True, color='gray')
        self.ax.set_ylim(0, 180)
        self.ax.set_title("Angles servos en temps réel", color='white')
        self.ax.set_xlabel("Temps (s)", color='white')
        self.ax.set_ylabel("Angle (°)", color='white')

        self.lines = [self.ax.plot([], [], label=f"Servo {i+1}")[0] for i in range(SERVO_COUNT)]
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        self.timestamps = []
        self.data = [[] for _ in range(SERVO_COUNT)]

        self.update_graph()

    def update_graph(self):
        while not self.controller.queue_angles.empty():
            ts, angles = self.controller.queue_angles.get()
            self.timestamps.append(ts)
            for i in range(SERVO_COUNT):
                self.data[i].append(angles[i])
            # Limite historique
            if len(self.timestamps) > 100:
                self.timestamps.pop(0)
                for d in self.data:
                    d.pop(0)

        for i, line in enumerate(self.lines):
            line.set_data(self.timestamps, self.data[i])

        if self.timestamps:
            self.ax.set_xlim(self.timestamps[0], self.timestamps[-1])

        self.canvas.draw_idle()
        self.after(1000, self.update_graph)

    def update_text(self, lang):
        pass


# === LANCEMENT ===
if __name__ == "__main__":
    app = RobotApp()
    app.mainloop()


    # --- Fonction pour envoyer une liste complète de positions ---
    def envoyer_positions(controller, positions):
        """
        Envoie une liste d'angles [0..180] pour chaque servo via la connexion série
        """
        if controller.demo_mode:
            controller.frames[LogPage].ajouter_log(f"[DEMO] Envoi positions: {positions}")
            return
        if not controller.serial_conn or not controller.serial_conn.is_open:
            messagebox.showwarning("Attention", "Connectez-vous à l'Arduino d'abord.")
            return
        try:
            for i, val in enumerate(positions):
                cmd = f"S{i}:{val}\n"
                controller.serial_conn.write(cmd.encode())
                controller.frames[LogPage].ajouter_log(f"Envoyé >> {cmd.strip()}")
                time.sleep(0.05)  # petit délai entre commandes
        except Exception as e:
            controller.frames[LogPage].ajouter_log(f"Erreur envoi positions: {e}")


    # --- Arrêt d'urgence ---
    def arret_urgence(controller):
        """
        Remet tous les servos à 90 degrés immédiatement
        """
        positions = [90] * SERVO_COUNT
        envoyer_positions(controller, positions)
        # Mise à jour sliders si on est sur la page contrôle
        controle = controller.frames.get(ControlePage)
        if controle:
            for i, val in enumerate(positions):
                controle.sliders[i].set(val)
        controller.frames[LogPage].ajouter_log("[ARRÊT D'URGENCE] Tous les servos à 90°")


    # --- Suppression d'une position dans la séquence de programmation ---
    def supprimer_position_sequence(programmation_page):
        """
        Supprime la position sélectionnée dans la liste de la programmation
        """
        idx = programmation_page.listbox.curselection()
        if not idx:
            messagebox.showinfo("Info", "Sélectionnez une position à supprimer.")
            return
        index = idx[0]
        programmation_page.sequence.pop(index)
        programmation_page.listbox.delete(index)
        programmation_page.controller.frames[LogPage].ajouter_log(f"Position {index + 1} supprimée de la séquence.")


    # --- Fonction ajoutée à ProgrammationPage pour supprimer position ---
    def programmation_supprimer_position(self):
        supprimer_position_sequence(self)


    # --- Raccourcis clavier dans ControlePage ---
    def controle_on_key(self, event):
        """
        Déplace le servo 0 (base) avec flèche gauche/droite, servo 6 (pince) avec +/-
        """
        if event.keysym == 'Left':
            self.increment_servo(0, -5)
        elif event.keysym == 'Right':
            self.increment_servo(0, 5)
        elif event.keysym in ('plus', 'equal'):
            self.increment_servo(6, 5)
        elif event.keysym in ('minus', 'underscore'):
            self.increment_servo(6, -5)


    # --- Alerte perte connexion série ---
    def alerte_perte_connexion(controller):
        if winsound:
            winsound.Beep(1000, 500)
        messagebox.showerror("Erreur", controller._t("perte_communication"))
        controller.frames[LogPage].ajouter_log(controller._t("perte_communication"))
        controller.status_bar.config(text=controller._t("non_connecte"))
        controller.stop_read_thread()
        if controller.serial_conn and controller.serial_conn.is_open:
            controller.serial_conn.close()
        controller.serial_conn = None


    # --- PATCH pour ajouter les boutons et liaisons ---

    # Ajout méthodes dans ProgrammationPage
    ProgrammationPage.programmation_supprimer_position = programmation_supprimer_position

    original_prog_init = ProgrammationPage.__init__


    def new_prog_init(self, parent, controller):
        original_prog_init(self, parent, controller)
        # Ajouter bouton Supprimer position
        btn_frame = self.winfo_children()[-1]  # Le dernier frame boutons créé
        tk.Button(btn_frame, text="Supprimer position", command=self.programmation_supprimer_position).pack(side="left",
                                                                                                            padx=5)


    ProgrammationPage.__init__ = new_prog_init

    # Ajout bouton Arrêt d'urgence dans ControlePage
    original_controle_init = ControlePage.__init__


    def new_controle_init(self, parent, controller):
        original_controle_init(self, parent, controller)
        stop_btn = ttk.Button(self, text="Arrêt d'urgence", command=lambda: arret_urgence(self.controller))
        stop_btn.pack(pady=10)
        # Bind clavier pour raccourcis
        self.bind_all("<Key>", lambda e: controle_on_key(self, e))


    ControlePage.__init__ = new_controle_init

    # Patch pour read_serial_loop dans RobotApp pour utiliser alerte_perte_connexion
    original_read_serial_loop = RobotApp.read_serial_loop


    def new_read_serial_loop(self):
        log_frame = self.frames[LogPage]
        while self.read_thread_running:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode(errors='ignore').strip()
                    if line:
                        log_frame.ajouter_log(f"Arduino >> {line}")
                        if line.startswith("ANGLES:"):
                            try:
                                parts = line.split(":")[1].split(",")
                                angles = [int(p) for p in parts]
                                if len(angles) == SERVO_COUNT:
                                    self.queue_angles.put((time.time(), angles))
                            except:
                                pass
            except Exception as e:
                log_frame.ajouter_log(f"{self._t('erreur_connexion')} : {e}")
                self.reconnect_attempts += 1
                if self.reconnect_attempts < 5:
                    log_frame.ajouter_log(self._t("tentative_reconnexion"))
                    time.sleep(2)
                    try:
                        if self.serial_conn:
                            self.serial_conn.close()
                            self.serial_conn.open()
                        self.reconnect_attempts = 0
                    except Exception as e2:
                        log_frame.ajouter_log(f"{self._t('reconnexion_echouee')} : {e2}")
                        if self.reconnect_attempts >= 5:
                            alerte_perte_connexion(self)
                else:
                    alerte_perte_connexion(self)
            time.sleep(0.1)


    RobotApp.read_serial_loop = new_read_serial_loop
# --- VARIABLES GLOBALES AJOUTÉES ---
APP_SETTINGS = {
    "theme": "dark",  # "dark" ou "light"
    "servo_limits": [(0, 180)] * SERVO_COUNT,  # limites angulaires mini/maxi
    "profiles": {},  # profils utilisateur (nom -> positions favorites, séquences)
}

# --- THEME MANAGER ---
def apply_theme(root, theme):
    if theme == "dark":
        bg_color = "#1e1e1e"
        fg_color = "white"
        btn_bg = "#34495e"
        entry_bg = "#2e2e2e"
    else:  # light
        bg_color = "white"
        fg_color = "black"
        btn_bg = "#3498db"
        entry_bg = "white"
    # Application globale
    root.configure(bg=bg_color)
    for widget in root.winfo_children():
        _apply_theme_rec(widget, bg_color, fg_color, btn_bg, entry_bg)

def _apply_theme_rec(widget, bg, fg, btn_bg, entry_bg):
    try:
        cls = widget.winfo_class()
        if cls in ("TFrame", "Frame"):
            widget.configure(bg=bg)
        elif cls in ("TLabel", "Label"):
            widget.configure(bg=bg, fg=fg)
        elif cls in ("TButton", "Button"):
            widget.configure(bg=btn_bg, fg=fg)
        elif cls in ("TEntry", "Entry", "Combobox"):
            widget.configure(bg=entry_bg, fg=fg)
        elif cls == "Text":
            widget.configure(bg=entry_bg, fg=fg)
    except Exception:
        pass
    for child in widget.winfo_children():
        _apply_theme_rec(child, bg, fg, btn_bg, entry_bg)


# --- PAGE PARAMÈTRES ---
class ParametresPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#1e1e1e")
        tk.Label(self, text="Paramètres généraux", font=("Arial", 18), fg="white", bg="#1e1e1e").pack(pady=10)

        # Choix thème
        self.var_theme = tk.StringVar(value=APP_SETTINGS["theme"])
        frame_theme = tk.Frame(self, bg="#1e1e1e")
        frame_theme.pack(pady=10)
        tk.Label(frame_theme, text="Thème :", fg="white", bg="#1e1e1e").pack(side="left")
        tk.Radiobutton(frame_theme, text="Sombre", variable=self.var_theme, value="dark",
                       command=self.change_theme, fg="white", bg="#1e1e1e", selectcolor="#34495e").pack(side="left")
        tk.Radiobutton(frame_theme, text="Clair", variable=self.var_theme, value="light",
                       command=self.change_theme, fg="black", bg="#1e1e1e", selectcolor="#bdc3c7").pack(side="left")

        # Bouton pour réinitialiser positions favorites
        tk.Button(self, text="Réinitialiser positions favorites", command=self.reset_positions).pack(pady=10)

    def change_theme(self):
        APP_SETTINGS["theme"] = self.var_theme.get()
        apply_theme(self.controller, APP_SETTINGS["theme"])

    def reset_positions(self):
        self.controller.position_favorites.clear()
        self.controller.frames[ControlePage].fav_combo['values'] = []
        self.controller.frames[LogPage].ajouter_log("Positions favorites réinitialisées.")


# --- PROGRAMMATION VISUELLE BASIQUE AVEC DRAG & DROP ---
class ProgrammationVisuellePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller
        tk.Label(self, text="Programmation Visuelle", font=("Arial", 18), fg="white", bg="#2e2e2e").pack(pady=10)

        self.commands = []  # liste des commandes programmées (dicts)
        self.listbox = tk.Listbox(self, bg="#1e1e1e", fg="white", font=("Consolas", 10), selectmode="extended")
        self.listbox.pack(expand=True, fill="both", padx=10, pady=10)

        # Boutons d'actions
        frame_btn = tk.Frame(self, bg="#2e2e2e")
        frame_btn.pack(pady=5)

        tk.Button(frame_btn, text="Ajouter Position actuelle", command=self.ajouter_position).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Supprimer sélection", command=self.supprimer_selection).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Déplacer Haut", command=self.deplacer_haut).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Déplacer Bas", command=self.deplacer_bas).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Exécuter Séquence", command=self.lire_sequence).pack(side="left", padx=5)

    def ajouter_position(self):
        controle = self.controller.frames[ControlePage]
        positions = [s.get() for s in controle.sliders]
        self.commands.append({"positions": positions})
        self.listbox.insert("end", str(positions))
        self.controller.frames[LogPage].ajouter_log("Position ajoutée à la programmation visuelle.")

    def supprimer_selection(self):
        selection = list(self.listbox.curselection())
        selection.reverse()
        for idx in selection:
            self.listbox.delete(idx)
            self.commands.pop(idx)
        self.controller.frames[LogPage].ajouter_log("Positions sélectionnées supprimées.")

    def deplacer_haut(self):
        idxs = list(self.listbox.curselection())
        if not idxs or min(idxs) == 0:
            return
        for idx in idxs:
            cmd = self.commands.pop(idx)
            self.commands.insert(idx-1, cmd)
        for idx in idxs:
            self.listbox.insert(idx-1, self.listbox.get(idx))
            self.listbox.delete(idx+1)
        self.listbox.selection_clear(0, "end")
        for idx in [i-1 for i in idxs]:
            self.listbox.selection_set(idx)

    def deplacer_bas(self):
        idxs = list(self.listbox.curselection())
        if not idxs or max(idxs) == len(self.commands)-1:
            return
        for idx in reversed(idxs):
            cmd = self.commands.pop(idx)
            self.commands.insert(idx+1, cmd)
        for idx in reversed(idxs):
            self.listbox.insert(idx+1, self.listbox.get(idx))
            self.listbox.delete(idx)
        self.listbox.selection_clear(0, "end")
        for idx in [i+1 for i in idxs]:
            self.listbox.selection_set(idx)

    def lire_sequence(self):
        if self.controller.demo_mode:
            self.controller.frames[LogPage].ajouter_log("[DEMO] Lecture de la séquence visuelle")
            for cmd in self.commands:
                self.controller.frames[LogPage].ajouter_log(f"[DEMO] Position: {cmd['positions']}")
                time.sleep(0.5)
            return

        if not self.controller.serial_conn or not self.controller.serial_conn.is_open:
            messagebox.showwarning("Attention", "Connectez-vous à l'Arduino d'abord.")
            return

        def play():
            for cmd in self.commands:
                positions = cmd["positions"]
                envoyer_positions(self.controller, positions)
                time.sleep(0.5)
        threading.Thread(target=play, daemon=True).start()

    def update_text(self, lang):
        pass


# --- AJOUT DE LA PAGE PARAMETRES ET PROGRAMMATION VISUELLE À L'APP ---
def ajouter_pages_supplementaires(app):
    param_page = ParametresPage(app.container, app)
    app.frames[ParametresPage] = param_page
    param_page.grid(row=0, column=0, sticky="nsew")

    prog_vis_page = ProgrammationVisuellePage(app.container, app)
    app.frames[ProgrammationVisuellePage] = prog_vis_page
    prog_vis_page.grid(row=0, column=0, sticky="nsew")

    # Ajout boutons dans navbar
    app.add_nav_button("⚙️ Paramètres", ParametresPage)
    app.add_nav_button("🧱 Prog Visuelle", ProgrammationVisuellePage)


# --- MODIFICATION DANS RobotApp.__init__ POUR APPLIQUER THÈME ET AJOUTER PAGES ---
original_robotapp_init = RobotApp.__init__
def new_robotapp_init(self):
    original_robotapp_init(self)
    # Appliquer thème
    apply_theme(self, APP_SETTINGS["theme"])
    # Ajouter pages
    ajouter_pages_supplementaires(self)

RobotApp.__init__ = new_robotapp_init
# === SIMULATION 3D AMÉLIORÉE ===
class Simulation3DAmelioreePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller

        # Frame pour le canvas VPython
        self.vpython_frame = tk.Frame(self, bg="#2e2e2e")
        self.vpython_frame.pack(expand=True, fill="both")

        # Création du canvas VPython avec contrôle souris
        self.canvas = canvas(width=800, height=600, background=color.gray(0.1), center=vector(0, 3, 0), forward=vector(0,-0.5,-1))
        self.canvas.bind('mousedown', self.on_mouse_down)
        self.canvas.bind('mouseup', self.on_mouse_up)
        self.canvas.bind('mousemove', self.on_mouse_move)
        self.canvas.bind('wheel', self.on_mouse_wheel)

        # Variables pour contrôle caméra
        self.dragging = False
        self.last_mouse_pos = None
        self.camera_theta = 0.0  # rotation horizontale
        self.camera_phi = 0.3    # rotation verticale
        self.camera_radius = 10

        # Construction du bras robot (segments articulés)
        self.construct_robot()

        # Angles actuels (7 servos)
        self.angles = [90]*SERVO_COUNT  # init à 90°

        # Lancement de la boucle d'update
        self.update_loop()

    def construct_robot(self):
        # Base fixe
        self.base = box(pos=vector(0,0,0), size=vector(3,0.3,3), color=color.blue)

        # Segments du bras avec pivots
        # Chaque segment est un box pivotant sur un axe
        self.segments = []

        # Dimensions des segments
        dims = [
            (0.5, 2.5, 0.5),  # bras 1
            (0.4, 2.0, 0.4),  # bras 2
            (0.35, 1.8, 0.35),# avant-bras
            (0.3, 1.0, 0.3),  # poignet
        ]

        # Création segments posés "en série"
        self.pivots = []
        pos_y = 0.15  # base hauteur
        for i, size in enumerate(dims):
            pivot = frame()
            pivot.pos = vector(0, pos_y, 0)
            segment = box(frame=pivot, pos=vector(0, size[1]/2, 0), size=vector(*size), color=color.red if i%2==0 else color.orange)
            self.pivots.append(pivot)
            self.segments.append(segment)
            pos_y += size[1]

        # Pince: deux pinces mobiles
        self.pince_pivot = frame()
        self.pince_pivot.pos = self.pivots[-1].pos + vector(0, dims[-1][1], 0)
        self.pince_left = box(frame=self.pince_pivot, pos=vector(-0.15, 0.15, 0), size=vector(0.1,0.5,0.1), color=color.gray(0.7))
        self.pince_right = box(frame=self.pince_pivot, pos=vector(0.15, 0.15, 0), size=vector(0.1,0.5,0.1), color=color.gray(0.7))

    def update_loop(self):
        # Récupérer les angles actuels (plus récents) s'ils sont dispo dans queue
        while not self.controller.queue_angles.empty():
            _, angles = self.controller.queue_angles.get()
            self.angles = angles

        # Appliquer angles aux pivots
        # Supposons :
        # servo 0 : rotation base autour Y (la base fixe dans notre modèle ne tourne pas, mais on peut animer)
        # servo 1 : pivot bras 1 (rotation autour X)
        # servo 2 : pivot bras 2 (rotation autour X)
        # servo 3 : pivot avant-bras (rotation autour X)
        # servo 4 : poignet (rotation autour X)
        # servo 5 : pince ouverture/fermeture (rotation autour Z)
        # servo 6 : rotation pince (autour Y)

        # Base rotation (optionnel, on fait tourner la caméra autour du bras au lieu)
        # self.base.rotate(angle=radians(self.angles[0]-90), axis=vector(0,1,0), origin=self.base.pos)

        # On anime pivots :
        # bras1 pivot (servo 1)
        self.pivots[0].axis = vector(1,0,0)
        self.pivots[0].up = vector(0,1,0)
        self.pivots[0].rotate(angle=radians(self.angles[1]-90), axis=vector(1,0,0))

        # bras2 pivot (servo 2)
        self.pivots[1].axis = vector(1,0,0)
        self.pivots[1].up = vector(0,1,0)
        self.pivots[1].rotate(angle=radians(self.angles[2]-90), axis=vector(1,0,0))

        # avant-bras pivot (servo 3)
        self.pivots[2].axis = vector(1,0,0)
        self.pivots[2].up = vector(0,1,0)
        self.pivots[2].rotate(angle=radians(self.angles[3]-90), axis=vector(1,0,0))

        # poignet pivot (servo 4)
        self.pivots[3].axis = vector(1,0,0)
        self.pivots[3].up = vector(0,1,0)
        self.pivots[3].rotate(angle=radians(self.angles[4]-90), axis=vector(1,0,0))

        # pince rotation (servo 6)
        self.pince_pivot.axis = vector(0,0,1)
        self.pince_pivot.up = vector(0,1,0)
        self.pince_pivot.rotate(angle=radians(self.angles[6]-90), axis=vector(0,1,0))

        # pince ouverture/fermeture (servo 5)
        angle_pince = radians(self.angles[5]-90) * 0.5  # réduire amplitude pour visuel
        self.pince_left.pos = vector(-0.15, 0.15, 0) + vector(-angle_pince, 0, 0)
        self.pince_right.pos = vector(0.15, 0.15, 0) + vector(angle_pince, 0, 0)

        # Mise à jour caméra selon angles et distance
        self.update_camera()

        # Replanifier la mise à jour
        self.after(50, self.update_loop)

    def update_camera(self):
        # Calculer position caméra sphérique autour du bras
        x = self.camera_radius * cos(self.camera_phi) * sin(self.camera_theta)
        y = self.camera_radius * sin(self.camera_phi)
        z = self.camera_radius * cos(self.camera_phi) * cos(self.camera_theta)
        self.canvas.camera.pos = vector(x, y+3, z)
        self.canvas.camera.axis = vector(0, 3, 0) - self.canvas.camera.pos

    def on_mouse_down(self, evt):
        self.dragging = True
        self.last_mouse_pos = (evt.pos.x, evt.pos.y)

    def on_mouse_up(self, evt):
        self.dragging = False
        self.last_mouse_pos = None

    def on_mouse_move(self, evt):
        if not self.dragging or not self.last_mouse_pos:
            return
        dx = evt.pos.x - self.last_mouse_pos[0]
        dy = evt.pos.y - self.last_mouse_pos[1]
        self.camera_theta += dx * 0.01
        self.camera_phi = max(-1.3, min(1.3, self.camera_phi + dy * 0.01))
        self.last_mouse_pos = (evt.pos.x, evt.pos.y)

    def on_mouse_wheel(self, evt):
        self.camera_radius = max(3, min(20, self.camera_radius - evt.delta * 0.1))

    def update_text(self, lang):
        pass

# --- AJOUTER PAGE SIMULATION AMÉLIORÉE À L'APP ---
def ajouter_simulation_3d_amelioree(app):
    sim_page = Simulation3DAmelioreePage(app.container, app)
    app.frames[Simulation3DAmelioreePage] = sim_page
    sim_page.grid(row=0, column=0, sticky="nsew")
    app.add_nav_button("🕹️ Simulation 3D Avancée", Simulation3DAmelioreePage)

# --- INJECTION DANS RobotApp INIT ---
original_robotapp_init_2 = RobotApp.__init__
def new_robotapp_init_2(self):
    original_robotapp_init_2(self)
    ajouter_simulation_3d_amelioree(self)

RobotApp.__init__ = new_robotapp_init_2
# === PAGE JOYSTICK VIRTUEL ===
class JoystickPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2e2e2e")
        self.controller = controller

        self.title_label = tk.Label(self, text="Joystick virtuel", font=("Arial", 18), fg="white", bg="#2e2e2e")
        self.title_label.pack(pady=10)

        self.canvas_size = 300
        self.pad_radius = 120
        self.knob_radius = 20

        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(pady=20)

        # Centre du pad
        self.center = (self.canvas_size // 2, self.canvas_size // 2)
        # Position initiale du knob
        self.knob_pos = list(self.center)

        # Dessin pad + knob
        self.pad_circle = self.canvas.create_oval(
            self.center[0] - self.pad_radius, self.center[1] - self.pad_radius,
            self.center[0] + self.pad_radius, self.center[1] + self.pad_radius,
            fill="#34495e"
        )
        self.knob_circle = self.canvas.create_oval(
            self.knob_pos[0] - self.knob_radius, self.knob_pos[1] - self.knob_radius,
            self.knob_pos[0] + self.knob_radius, self.knob_pos[1] + self.knob_radius,
            fill="#e74c3c"
        )

        # Bindings souris
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.dragging = False

        # Servo indices à contrôler avec joystick (exemple servo 0 = base, servo 4 = poignet)
        self.servo_x = 0  # axe horizontal du joystick -> servo 0
        self.servo_y = 4  # axe vertical joystick -> servo 4

        # Valeurs min/max servo
        self.servo_min = 0
        self.servo_max = 180

        # Label affichage valeurs
        self.label_x = tk.Label(self, text="Servo 1 (base) : 90°", fg="white", bg="#2e2e2e", font=("Arial", 14))
        self.label_x.pack()
        self.label_y = tk.Label(self, text="Servo 5 (poignet) : 90°", fg="white", bg="#2e2e2e", font=("Arial", 14))
        self.label_y.pack()

        # Valeurs actuelles
        self.value_x = 90
        self.value_y = 90

    def on_press(self, event):
        # Si clic dans pad
        dx = event.x - self.center[0]
        dy = event.y - self.center[1]
        dist = (dx*dx + dy*dy)**0.5
        if dist <= self.pad_radius:
            self.dragging = True
            self.update_knob(event.x, event.y)

    def on_drag(self, event):
        if self.dragging:
            dx = event.x - self.center[0]
            dy = event.y - self.center[1]
            dist = (dx*dx + dy*dy)**0.5
            if dist > self.pad_radius:
                # Clamp dans le cercle
                dx = dx * self.pad_radius / dist
                dy = dy * self.pad_radius / dist
            new_x = self.center[0] + dx
            new_y = self.center[1] + dy
            self.update_knob(new_x, new_y)

    def on_release(self, event):
        self.dragging = False
        # Recentrer le knob
        self.update_knob(self.center[0], self.center[1])

    def update_knob(self, x, y):
        # Met à jour la position graphique
        self.knob_pos = [x, y]
        self.canvas.coords(
            self.knob_circle,
            x - self.knob_radius, y - self.knob_radius,
            x + self.knob_radius, y + self.knob_radius
        )
        # Calcul valeurs servo selon position relative au centre
        rel_x = (x - self.center[0]) / self.pad_radius  # entre -1 et 1
        rel_y = (self.center[1] - y) / self.pad_radius  # inversé y, entre -1 et 1

        # Map à servo 0..180
        val_x = int((rel_x + 1) / 2 * (self.servo_max - self.servo_min) + self.servo_min)
        val_y = int((rel_y + 1) / 2 * (self.servo_max - self.servo_min) + self.servo_min)

        self.value_x = val_x
        self.value_y = val_y

        self.label_x.config(text=f"Servo 1 (base) : {val_x}°")
        self.label_y.config(text=f"Servo 5 (poignet) : {val_y}°")

        # Envoyer commande si connecté et pas en demo
        if not self.controller.demo_mode and self.controller.serial_conn and self.controller.serial_conn.is_open:
            try:
                cmd_x = f"S{self.servo_x}:{val_x}\n"
                cmd_y = f"S{self.servo_y}:{val_y}\n"
                self.controller.serial_conn.write(cmd_x.encode())
                self.controller.serial_conn.write(cmd_y.encode())
                self.controller.frames[LogPage].ajouter_log(f"Joystick >> {cmd_x.strip()} | {cmd_y.strip()}")
            except Exception as e:
                self.controller.frames[LogPage].ajouter_log(f"Erreur joystick commande: {e}")

    def update_text(self, lang):
        # Pour l'instant en dur, mais tu peux étendre LANGUAGES
        pass

# --- AJOUTER PAGE JOYSTICK À L'APP ---
def ajouter_joystick_page(app):
    joystick_page = JoystickPage(app.container, app)
    app.frames[JoystickPage] = joystick_page
    joystick_page.grid(row=0, column=0, sticky="nsew")
    app.add_nav_button("🎮 Joystick", JoystickPage)

# --- INJECTION DANS RobotApp INIT ---
original_robotapp_init_3 = RobotApp.__init__
def new_robotapp_init_3(self):
    original_robotapp_init_3(self)
    ajouter_joystick_page(self)

RobotApp.__init__ = new_robotapp_init_3
