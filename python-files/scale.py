import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import pyperclip
import time
import logging
from tkinter import messagebox

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='error_log.txt')
logger = logging.getLogger(__name__)

# Constantes
BAUDRATE = 9600
TIMEOUT = 0.5
UPDATE_INTERVAL = 100  # ms
WINDOW_SIZE = "300x140"
CONFIG_WINDOW_SIZE = "350x180"
TEST_COMMANDS = [b"P1\r\n", b"P2\r\n", b"P3\r\n"]
TARE_COMMAND = b"T\r\n"
CAL_COMMAND = b"CAL\r\n"

# Variables globales
ser = None
connected = False
copy_button = None
tare_button = None
adjust_button = None
unit_choice = None
history = {"Copier": 0, "Tare": 0, "Ajustage": 0}

def detect_usb_devices():
    """Liste les ports série disponibles.
    
    Returns:
        list: Liste de descriptions des ports série ou message d'erreur.
    """
    devices = []
    try:
        ports = serial.tools.list_ports.comports()
        if ports:
            devices.extend([f"{port.device} - {port.description}" for port in ports])
        else:
            devices.append("Aucun port série détecté")
            logger.info("Aucun port série détecté")
    except Exception as e:
        logger.error(f"Erreur lors de la détection des ports série : {e}")
        devices.append(f"Erreur : {e}")
    return devices or ["Aucun port série détecté"]

def test_balance_connection(serial_port):
    """Teste la connexion à un port série pour vérifier si une balance est connectée.
    
    Args:
        serial_port (str): Port à tester (ex. 'COM3').
    
    Returns:
        bool: True si la connexion est valide, False sinon.
    """
    try:
        ser = serial.Serial(serial_port, BAUDRATE, timeout=TIMEOUT)
        for command in TEST_COMMANDS:
            ser.write(command)
            response = ser.readline().decode().strip()
            if response:
                ser.close()
                logger.info(f"Connexion réussie au port {serial_port}")
                return True
        ser.close()
    except serial.SerialException as e:
        logger.error(f"Erreur lors du test de connexion à {serial_port} : {e}")
    return False

def connect_to_device():
    """Tente une connexion automatique à une balance."""
    global ser, connected
    if ser and ser.is_open:
        try:
            ser.close()
            logger.info("Connexion série existante fermée")
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de la connexion existante : {e}")
    
    device_name = detect_usb_devices()
    if device_name and device_name[0] != "Aucun port série détecté" and "Erreur" not in device_name[0]:
        for device in device_name:
            port = device.split(" - ")[0]
            if test_balance_connection(port):
                try:
                    ser = serial.Serial(port, BAUDRATE, timeout=TIMEOUT)
                    connected = True
                    status_label.config(text=f"Connecté à {port}", fg="lime")
                    copy_button.config(state="normal")
                    tare_button.config(state="normal")
                    adjust_button.config(state="normal")
                    logger.info(f"Connecté à la balance sur le port {port}")
                    return
                except serial.SerialException as e:
                    logger.error(f"Échec de connexion à {port} : {e}")
        status_label.config(text="Aucune balance détectée", fg="red")
        connected = False
        copy_button.config(state="disabled")
        tare_button.config(state="disabled")
        adjust_button.config(state="disabled")
        ser = None
    else:
        status_label.config(text="Aucun port série détecté", fg="red")
        connected = False
        copy_button.config(state="disabled")
        tare_button.config(state="disabled")
        adjust_button.config(state="disabled")
        ser = None
        logger.info("Aucun port série détecté pour la connexion")

def read_weight():
    """Lit le poids depuis la balance et met à jour l'affichage avec conversion d'unité."""
    global ser, connected
    if ser and ser.is_open and connected:
        try:
            ser.write(b"P3\r\n")
            data = ser.readline().decode().strip()
            if data:
                try:
                    weight = float(data)
                    unit = unit_choice.get()
                    if unit == "mg":
                        weight *= 1000
                        weight_display.config(text=f"{weight:.2f} mg")
                    elif unit == "kg":
                        weight /= 1000
                        weight_display.config(text=f"{weight:.4f} kg")
                    else:  # g
                        weight_display.config(text=f"{weight:.2f} g")
                    logger.info(f"Poids lu : {weight} g (affiché en {unit})")
                except ValueError:
                    weight_display.config(text="Erreur")
                    logger.error(f"Données invalides reçues : {data}")
            else:
                weight_display.config(text=f"--- {unit_choice.get()}")
                logger.debug("Aucune donnée reçue de la balance")
        except serial.SerialException as e:
            weight_display.config(text="Erreur")
            status_label.config(text="Déconnecté (erreur)", fg="red")
            connected = False
            copy_button.config(state="disabled")
            tare_button.config(state="disabled")
            adjust_button.config(state="disabled")
            ser = None
            logger.error(f"Erreur de lecture du poids : {e}")
    else:
        weight_display.config(text=f"--- {unit_choice.get()}")
        logger.debug("Aucune connexion active")
    root.after(UPDATE_INTERVAL, read_weight)

def copy_weight():
    """Copie le poids affiché dans le presse-papiers."""
    weight = weight_display.cget("text")
    if weight.startswith("---"):
        messagebox.showwarning("Avertissement", "Aucun poids valide à copier")
        logger.warning("Tentative de copie d'un poids invalide")
        return
    try:
        pyperclip.copy(weight)
        update_history("Copier")
        logger.info(f"Poids '{weight}' copié dans le presse-papiers")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de la copie : {e}")
        logger.error(f"Erreur lors de la copie : {e}")

def tare():
    """Envoie la commande de tare à la balance."""
    global ser, connected
    if ser and ser.is_open and connected:
        try:
            ser.write(TARE_COMMAND)
            update_history("Tare")
            logger.info("Commande de tare envoyée")
        except serial.SerialException as e:
            messagebox.showerror("Erreur", f"Échec de l'envoi de la commande : {e}")
            logger.error(f"Erreur lors de l'envoi de la commande de tare : {e}")
            status_label.config(text="Déconnecté (erreur)", fg="red")
            connected = False
            copy_button.config(state="disabled")
            tare_button.config(state="disabled")
            adjust_button.config(state="disabled")
            ser = None
    else:
        messagebox.showwarning("Avertissement", "Aucune balance connectée")
        logger.warning("Tentative de tare sans connexion active")
        update_history("Tare")  # Historique mis à jour même sans connexion

def adjust():
    """Envoie la commande d'ajustage à la balance."""
    global ser, connected
    if ser and ser.is_open and connected:
        try:
            ser.write(CAL_COMMAND)
            update_history("Ajustage")
            logger.info("Commande d'ajustage envoyée")
        except serial.SerialException as e:
            messagebox.showerror("Erreur", f"Échec de l'envoi de la commande : {e}")
            logger.error(f"Erreur lors de l'envoi de la commande d'ajustage : {e}")
            status_label.config(text="Déconnecté (erreur)", fg="red")
            connected = False
            copy_button.config(state="disabled")
            tare_button.config(state="disabled")
            adjust_button.config(state="disabled")
            ser = None
    else:
        messagebox.showwarning("Avertissement", "Aucune balance connectée")
        logger.warning("Tentative d'ajustage sans connexion active")
        update_history("Ajustage")  # Historique mis à jour même sans connexion

def update_history(action):
    """Met à jour l'historique des actions dans l'onglet Historique.
    
    Args:
        action (str): Nom de l'action (Copier, Tare, Ajustage).
    """
    if action in history:
        history[action] += 1
        history_label.config(text=f"Copier: {history['Copier']} | Tare: {history['Tare']} | Ajustage: {history['Ajustage']}")
        logger.info(f"Historique mis à jour : {action} ({history[action]})")

def refresh_devices():
    """Actualise la liste des périphériques dans l'onglet Paramètres."""
    device_list["values"] = detect_usb_devices()
    if device_list["values"] and "Aucun" not in device_list["values"][0] and "Erreur" not in device_list["values"][0]:
        device_list.current(0)
    logger.info("Liste des périphériques actualisée")

def on_closing():
    """Ferme la connexion série et l'application."""
    global ser
    if ser and ser.is_open:
        try:
            ser.close()
            logger.info("Connexion série fermée")
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de la connexion : {e}")
    root.destroy()

# Fenêtre principale
root = tk.Tk()
root.title("Balance et Périphériques")
root.geometry(WINDOW_SIZE)
root.configure(bg="#121212")
root.resizable(False, False)

# Styles modernes
style = ttk.Style()
style.theme_create("dark", parent="alt", settings={
    "TNotebook": {"configure": {"tabmargins": [2, 2, 2, 2], "background": "#121212"}},
    "TNotebook.Tab": {
        "configure": {"padding": [5, 2], "background": "#333333", "foreground": "white", "font": ("Segoe UI", 9, "bold")},
        "map": {"background": [("selected", "#555555"), ("active", "#777777")]},
    },
    "TFrame": {"configure": {"background": "#121212"}},
    "TCombobox": {
        "configure": {
            "selectbackground": "#333333",
            "selectforeground": "white",
            "background": "#1E1E1E",
            "foreground": "white",
            "font": ("Segoe UI", 9)
        }
    },
    "TButton": {"configure": {"padding": [5, 2], "background": "#333333", "foreground": "white", "font": ("Segoe UI", 9, "bold")}}
})
style.theme_use("dark")

# Ajout des onglets
tab_control = ttk.Notebook(root)
main_tab = ttk.Frame(tab_control)
settings_tab = ttk.Frame(tab_control)
history_tab = ttk.Frame(tab_control)
info_tab = ttk.Frame(tab_control)
tab_control.add(main_tab, text="Balance")
tab_control.add(settings_tab, text="Paramètres")
tab_control.add(history_tab, text="Historique")
tab_control.add(info_tab, text="Infos")
tab_control.pack(expand=1, fill="both")

# Indicateur de connexion
status_label = tk.Label(main_tab, text="Aucun port série détecté", font=("Segoe UI", 8), fg="red", bg="#121212")
status_label.pack(pady=2)

# Affichage digital du poids
try:
    weight_display = tk.Label(main_tab, text="--- g", font=("Digital-7", 24, "bold"), fg="lime", bg="#2E2E2E", relief="flat", padx=10, pady=5)
except tk.TclError:
    weight_display = tk.Label(main_tab, text="--- g", font=("Segoe UI", 24, "bold"), fg="lime", bg="#2E2E2E", relief="flat", padx=10, pady=5)
weight_display.pack(pady=2)

# Menu des unités
unit_frame = tk.Frame(main_tab, bg="#121212")
unit_frame.pack(pady=2)
tk.Label(unit_frame, text="Unité:", font=("Segoe UI", 9), fg="white", bg="#121212").pack(side=tk.LEFT, padx=2)
unit_choice = ttk.Combobox(unit_frame, values=["mg", "g", "kg"], width=5, state="readonly")
unit_choice.current(1)
unit_choice.pack(side=tk.LEFT)

# Cadre des boutons
button_frame = tk.Frame(main_tab, bg="#121212")
button_frame.pack(pady=2)

tare_button = ttk.Button(button_frame, text="Tare", command=tare, width=8, state="disabled")
tare_button.pack(side=tk.LEFT, padx=2)
tare_button.bind("<Enter>", lambda e: status_label.config(text="Réinitialiser la balance") if not connected else status_label.config(text=f"Connecté à {ser.port}"))
tare_button.bind("<Leave>", lambda e: status_label.config(text="Aucun port série détecté" if not connected else f"Connecté à {ser.port}"))

adjust_button = ttk.Button(button_frame, text="Adj", command=adjust, width=8, state="disabled")
adjust_button.pack(side=tk.LEFT, padx=2)
adjust_button.bind("<Enter>", lambda e: status_label.config(text="Ajuster la balance") if not connected else status_label.config(text=f"Connecté à {ser.port}"))
adjust_button.bind("<Leave>", lambda e: status_label.config(text="Aucun port série détecté" if not connected else f"Connecté à {ser.port}"))

copy_button = ttk.Button(button_frame, text="Copier", command=copy_weight, width=8, state="disabled")
copy_button.pack(side=tk.LEFT, padx=2)
copy_button.bind("<Enter>", lambda e: status_label.config(text="Copier le poids") if not connected else status_label.config(text=f"Connecté à {ser.port}"))
copy_button.bind("<Leave>", lambda e: status_label.config(text="Aucun port série détecté" if not connected else f"Connecté à {ser.port}"))

# Onglet Historique
history_label = tk.Label(history_tab, text="Copier: 0 | Tare: 0 | Ajustage: 0", font=("Segoe UI", 9), fg="white", bg="#121212")
history_label.pack(pady=10)

# Onglet Paramètres
device_list = ttk.Combobox(settings_tab, width=40, state="readonly")
device_list.pack(pady=5)
device_list["values"] = detect_usb_devices()
if device_list["values"] and "Aucun" not in device_list["values"][0] and "Erreur" not in device_list["values"][0]:
    device_list.current(0)

button_frame_settings = tk.Frame(settings_tab, bg="#121212")
button_frame_settings.pack(pady=5)

auto_button = ttk.Button(button_frame_settings, text="Auto", command=connect_to_device, width=8)
auto_button.pack(side=tk.LEFT, padx=2)
refresh_button = ttk.Button(button_frame_settings, text="Refresh", command=refresh_devices, width=8)
refresh_button.pack(side=tk.LEFT, padx=2)

# Onglet Infos
info_label = tk.Label(info_tab, text="Créé par Ali.K\nApplication de gestion de balance\nVersion 1.0", font=("Segoe UI", 9), fg="white", bg="#121212", justify="center")
info_label.pack(pady=10)

# Protocole de fermeture
root.protocol("WM_DELETE_WINDOW", on_closing)

# Démarrage
connect_to_device()
read_weight()

root.mainloop()