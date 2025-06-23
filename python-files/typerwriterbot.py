import sys
import subprocess
import time
import random
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json # Import for JSON handling

# --- Paketinstallation ---
def install_packages():
    """
    Überprüft, ob die erforderlichen Python-Pakete installiert sind,
    und installiert sie gegebenenfalls. Bei Fehlern wird eine Fehlermeldung
    angezeigt und das Programm beendet.
    """
    required = ['selenium', 'webdriver-manager', 'pynput']
    for package in required:
        try:
            __import__(package)
        except ImportError:
            print(f"Installiere fehlendes Paket: {package}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except Exception as e:
                messagebox.showerror("Installationsfehler",
                                     f"Konnte Paket '{package}' nicht installieren.\n"
                                     f"Bitte manuell installieren: pip install {package}\n\n"
                                     f"Fehlerdetails: {e}")
                sys.exit(1)

# Stellt sicher, dass alle Pakete vor dem Import installiert sind
install_packages()

# Importe nach der Paketinstallation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from pynput.keyboard import Controller

# Initialisierung des Tastatur-Controllers für pynput
keyboardpy = Controller()

# Dateipfad für die Speicherdatei der Anmeldedaten
CREDENTIALS_FILE = "credentials.json"
# Dateipfad für die Speicherdatei der Einstellungen
SETTINGS_FILE = "settings.json"

# --- Hilfsfunktionen für die Bot-Logik ---

def close_cookie_banner(driver):
    """
    Versucht, ein gängiges Cookie-Banner auf der Webseite zu schließen.
    Wartet auf das Overlay und den Zustimmen-Button und klickt diesen.
    Fehler werden ignoriert, falls kein Banner vorhanden ist.
    """
    try:
        # Warte, bis das Cookie-Overlay sichtbar ist
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "fc-dialog-overlay"))
        )
        # Warte, bis der Zustimmen-Button klickbar ist
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "fc-cta-consent"))
        )
        accept_button.click()
        time.sleep(1) # Kurze Pause, damit das Banner verschwinden kann
    except Exception:
        # Wenn kein Banner gefunden oder geklickt werden kann, einfach weitermachen
        pass

def start_browser(browser_choice):
    """
    Initialisiert und gibt eine WebDriver-Instanz basierend auf der Auswahl zurück.
    Unterstützt Firefox ('f'), Chrome ('c') und Edge ('e').
    """
    try:
        if browser_choice == "f":
            return webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()))
        elif browser_choice == "c":
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        elif browser_choice == "e":
            return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
        else:
            raise ValueError("Ungültige Browser-Auswahl. Bitte wählen Sie 'f', 'c' oder 'e'.")
    except Exception as e:
        # Wirft eine Ausnahme, die von der aufrufenden Funktion abgefangen wird
        raise Exception(f"Browser konnte nicht gestartet werden. Stellen Sie sicher, dass der Browser installiert ist "
                        f"und der WebDriver heruntergeladen werden kann.\nFehler: {e}")

def Login(driver, data):
    """
    Meldet sich mit den bereitgestellten Anmeldedaten auf der typewriter.at-Website an.
    """
    try:
        driver.get("https://at4.typewriter.at/index.php?r=site/index")
        driver.maximize_window()
        close_cookie_banner(driver)

        # Warte auf das Benutzername-Feld und gib die Daten ein
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "LoginForm_username")))
        driver.find_element(By.ID, "LoginForm_username").send_keys(data["username"])
        driver.find_element(By.ID, "LoginForm_pw").send_keys(data["password"])

        # Klicke auf den Login-Button mithilfe von JavaScript für Robustheit
        login_button = driver.find_element(By.NAME, "yt0")
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(3) # Wartezeit, bis die Seite nach dem Login-Versuch geladen ist

        if "login" in driver.current_url:
            raise Exception("Login fehlgeschlagen – bitte Anmeldedaten prüfen.")
    except Exception as e:
        raise Exception(f"Fehler während des Login-Vorgangs: {e}")
    print("Login erfolgreich.") # Ausgabe auf der Konsole zur Information
    return driver

def NextLesson(driver):
    """
    Navigiert zur nächsten Lektion und startet diese.
    """
    try:
        # Warte auf den Start-Button der nächsten Lektion und klicke ihn
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "cockpitStartButton"))).click()
        time.sleep(2) # Wartezeit, bis die Übungsseite geladen ist
    except Exception as e:
        raise Exception(f"Fehler beim Starten der nächsten Lektion: {e}")

def get_common_mistake_char(correct_char):
    """
    Gibt ein häufiges falsches Zeichen basierend auf dem richtigen Zeichen zurück,
    um realistischere Tippfehler zu simulieren.
    """
    # Eine einfache Zuordnung von häufigen Tippfehlern (Nachbartasten, häufige Vertauschungen)
    mistake_map = {
        'a': ['s', 'q', 'z'], 's': ['a', 'd', 'w', 'x'], 'd': ['s', 'f', 'e', 'c'],
        'f': ['d', 'g', 'r', 'v'], 'g': ['f', 'h', 't', 'b'], 'h': ['g', 'j', 'z', 'n'],
        'j': ['h', 'k', 'u', 'm'], 'k': ['j', 'l', 'i', ','], 'l': ['k', 'ö', 'o', '.'],
        'ö': ['l', 'ä', 'p', '-'], 'ä': ['ö', '#'], '#': ['+'],
        'q': ['w', 'a'], 'w': ['q', 'e', 's'], 'e': ['w', 'r', 'd'],
        'r': ['e', 't', 'f'], 't': ['r', 'z', 'g'], 'z': ['t', 'u', 'h'],
        'u': ['z', 'i', 'j'], 'i': ['u', 'o', 'k'], 'o': ['i', 'p', 'l'],
        'p': ['o', 'ü'], 'ü': ['p', '´'], '+': ['´', 'ß'],
        'y': ['t', 'h'], 'x': ['y', 'c'], 'c': ['x', 'v', 'd'],
        'v': ['c', 'b', 'f'], 'b': ['v', 'n', 'g'], 'n': ['b', 'm', 'h'],
        'm': ['n', 'j', ','], ',': ['m', '.', 'k'], '.': [',', '-', 'l'],
        '-': ['.', 'ß', 'ö'], 'ß': ['-', '#'],
        '1': ['2', 'q'], '2': ['1', '3', 'w'], '3': ['2', '4', 'e'],
        '4': ['3', '5', 'r'], '5': ['4', '6', 't'], '6': ['5', '7', 'z'],
        '7': ['6', '8', 'u'], '8': ['7', '9', 'i'], '9': ['8', '0', 'o'],
        '0': ['9', 'ß', 'p'],
        ' ': [' '] # Leerzeichen bleiben Leerzeichen, kann aber zu Doppel-Leerzeichen führen
    }
    # Versuche, einen Fehlercharakter zu finden. Wenn keiner definiert, nimm einen zufälligen Buchstaben.
    possible_mistakes = mistake_map.get(correct_char.lower(), None)
    if possible_mistakes:
        return random.choice(possible_mistakes)
    else:
        return random.choice("asdfjklöeiunmryxcv123456789!()/?")

def type_with_optional_mistake(char, makeMistakes, mistakeChance, mistakeClusterChance, typing_style_params):
    """
    Simuliert das Tippen eines Zeichens und fügt optional einen Tippfehler ein.
    Der falsche Buchstabe bleibt stehen und der richtige wird danach getippt.
    Beinhaltet auch die Fehlerhäufung basierend auf 'mistakeClusterChance'.
    Berücksichtigt Tippstil-spezifische Verzögerungen.
    """
    base_delay = typing_style_params.get("base_delay", 0.05) # Standard-Verzögerung pro Zeichen
    delay_variance = typing_style_params.get("delay_variance", 0.02) # Varianz der Verzögerung

    if makeMistakes and random.random() < (mistakeChance / 100.0):
        # Häufiger Fehler: Wähle einen realistischen falschen Buchstaben
        fake_char = get_common_mistake_char(char)
        keyboardpy.type(fake_char)
        time.sleep(random.uniform(base_delay, base_delay + delay_variance)) # Kurze Verzögerung für den Fehler

        # Fehlerhäufung: Chance, einen weiteren Fehler zu machen, ohne Korrektur
        if random.random() < (mistakeClusterChance / 100.0):
            additional_fake_char = get_common_mistake_char(char)
            keyboardpy.type(additional_fake_char)
            time.sleep(random.uniform(base_delay, base_delay + delay_variance)) # Kurze Verzögerung für den zusätzlichen Fehler

    keyboardpy.type(char) # Immer das korrekte Zeichen am Ende tippen

    # Zusätzliche Pause nach bestimmten Zeichen (z.B. Satzzeichen)
    if typing_style_params.get("pause_after_punctuation", False) and char in ['.', ',', ';', '!', '?']:
        time.sleep(random.uniform(0.1, 0.3))


def DoExercise(driver, speed, makeMistakes, mistakeChance, mistakeClusterChance, typing_style, is_running_flag):
    """
    Führt die Tippübung durch, indem Zeichen aus dem Übungsfeld gelesen
    und simuliert werden. Überprüft den is_running_flag, um bei Bedarf zu stoppen.
    Berücksichtigt verschiedene Tippstile.
    """
    # Parameter für die verschiedenen Tippstile
    TYPING_STYLES = {
        "Perfekt": {
            "speed_multiplier": 1.0, # Geschwindigkeit wird direkt als WPM genutzt
            "mistake_override": False, # Eigene Fehler-Einstellungen werden ignoriert
            "fixed_mistake_chance": 0,
            "fixed_mistake_cluster_chance": 0,
            "base_delay": 0.01, # Sehr schnell, sehr konstant
            "delay_variance": 0.005,
            "initial_pause_variance": 0.5, # Geringe Anfangsverzögerungsvarianz
            "long_pause_chance": 0, # Keine langen Pausen
            "long_pause_duration": (0, 0),
            "pause_after_punctuation": False,
        },
        "Anfänger": {
            "speed_multiplier": 0.4, # 40% der eingestellten Geschwindigkeit
            "mistake_override": True, # Eigene Fehler-Einstellungen werden genutzt, aber mit höherer Wahrscheinlichkeit
            "fixed_mistake_chance": 20, # Feste Fehlerquote für Anfänger
            "fixed_mistake_cluster_chance": 50, # Feste Fehlercluster-Chance für Anfänger
            "base_delay": 0.15, # Langsamere Grundverzögerung
            "delay_variance": 0.08, # Größere Varianz
            "initial_pause_variance": 3.0, # Hohe Anfangsverzögerungsvarianz
            "long_pause_chance": 0.15, # 15% Chance auf eine lange Pause nach Sätzen
            "long_pause_duration": (0.8, 2.5),
            "pause_after_punctuation": True,
        },
        "Fortgeschritten": {
            "speed_multiplier": 0.8, # 80% der eingestellten Geschwindigkeit
            "mistake_override": False, # Eigene Fehler-Einstellungen werden genutzt
            "fixed_mistake_chance": None, # Nicht überschreiben
            "fixed_mistake_cluster_chance": None, # Nicht überschreiben
            "base_delay": 0.03, # Schnelle Grundverzögerung
            "delay_variance": 0.03, # Etwas Varianz
            "initial_pause_variance": 1.0, # Mittlere Anfangsverzögerungsvarianz
            "long_pause_chance": 0.05, # Geringe Chance auf lange Pausen
            "long_pause_duration": (0.3, 1.0),
            "pause_after_punctuation": True,
        }
    }
    style_params = TYPING_STYLES.get(typing_style, TYPING_STYLES["Fortgeschritten"]) # Standard auf Fortgeschritten, falls unbekannt

    # Überschreibt die makeMistakes, mistakeChance und mistakeClusterChance basierend auf dem Stil
    current_make_mistakes = makeMistakes
    current_mistake_chance = mistakeChance
    current_mistake_cluster_chance = mistakeClusterChance

    if style_params["mistake_override"]:
        current_make_mistakes = True # Immer Fehler machen im Anfänger-Modus, auch wenn Checkbox aus ist
        current_mistake_chance = style_params["fixed_mistake_chance"]
        current_mistake_cluster_chance = style_params["fixed_mistake_cluster_chance"]
    elif typing_style == "Perfekt":
        current_make_mistakes = False # Nie Fehler im Perfekt-Modus
        current_mistake_chance = 0
        current_mistake_cluster_chance = 0
    # Ansonsten bleiben die Werte aus der GUI

    # Drücke Enter, um den Start der Übung zu bestätigen (falls erforderlich)
    keyboardpy.press(Keys.ENTER)
    time.sleep(1)

    try:
        # Warte, bis das Textfeld mit dem aktuellen Zeichen vorhanden ist
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "text_todo_1")))
        box = driver.find_element(By.ID, "text_todo_1")
        # Warte auf das Span-Element (das aktuelle Zeichen) innerhalb des Textfeldes
        WebDriverWait(box, 5).until(EC.presence_of_element_located((By.TAG_NAME, "span")))
        currentChar = box.find_element(By.TAG_NAME, "span").text
    except Exception as e:
        raise Exception(f"Textfeld oder Initialzeichen für die Übung nicht gefunden: {e}")

    # Erneutes Drücken von Enter, um die eigentliche Tippsequenz zu starten
    keyboardpy.press(Keys.ENTER)
    time.sleep(2.5 + random.uniform(0, style_params["initial_pause_variance"])) # Wartezeit, bis die Übung richtig aktiviert ist, mit Varianz

    # Tippe das allererste Zeichen
    try:
        # Lese das aktuelle Zeichen erneut, da es sich nach dem zweiten Enter geändert haben könnte
        currentChar = box.find_element(By.TAG_NAME, "span").text
        type_with_optional_mistake(currentChar, current_make_mistakes, current_mistake_chance, current_mistake_cluster_chance, style_params)
        time.sleep(2.5) # Anfangsverzögerung vor dem kontinuierlichen Tippen
    except Exception as e:
        raise Exception(f"Fehler beim Tippen des ersten Zeichens der Übung: {e}")

    # Hauptschleife für das Tippen
    while is_running_flag(): # Überprüft das Flag vom GUI-Thread, um die Ausführung zu steuern
        try:
            # Überprüft die verbleibenden Zeichen, um festzustellen, ob die Übung beendet ist
            amountRemaining_element = driver.find_element(By.ID, "amountRemaining")
            remainingInt = int(amountRemaining_element.text)
        except Exception:
            # Wenn das Element nicht gefunden wird oder die Konvertierung fehlschlägt,
            # wird angenommen, dass die Übung beendet ist
            print("Info: 'amountRemaining'-Element nicht gefunden oder ungültig. Übung wahrscheinlich beendet.")
            break # Schleife verlassen

        if remainingInt <= 0:
            break # Übung beendet

        try:
            # Überprüft, ob das Span-Element für das aktuelle Zeichen noch vorhanden ist
            # Eine sehr kurze Wartezeit, um schnell zu erkennen, ob die Übung abgeschlossen ist
            WebDriverWait(box, 0.1).until(EC.presence_of_element_located((By.TAG_NAME, "span")))
            currentChar = box.find_element(By.TAG_NAME, "span").text

            # Lange Pause einfügen
            if random.random() < style_params["long_pause_chance"]:
                time.sleep(random.uniform(style_params["long_pause_duration"][0], style_params["long_pause_duration"][1]))

            type_with_optional_mistake(currentChar, current_make_mistakes, current_mistake_chance, current_mistake_cluster_chance, style_params)
            
            # Berechnet die Verzögerung basierend auf der gewünschten Geschwindigkeit und dem Stil-Multiplikator
            effective_speed = int(speed * style_params["speed_multiplier"])
            if effective_speed <= 0: effective_speed = 50 # Mindestgeschwindigkeit, um Division durch Null zu vermeiden
            
            # Normale Verzögerung pro Zeichen, mit Varianz
            delay_per_char = 60 / effective_speed
            actual_delay = random.uniform(delay_per_char - style_params["delay_variance"], delay_per_char + style_params["delay_variance"])
            if actual_delay < 0.01: actual_delay = 0.01 # Mindestverzögerung
            time.sleep(actual_delay)

        except Exception:
            # Wenn das Span-Element nicht mehr gefunden wird, ist die Übung wahrscheinlich abgeschlossen
            print("Info: Aktuelles Zeichen-Element nicht gefunden. Übung wahrscheinlich beendet.")
            break # Schleife verlassen

def GotoHomeScreen(driver):
    """
    Navigiert zurück zur Übersichtsseite des Benutzers.
    """
    try:
        driver.get("https://at4.typewriter.at/index.php?r=user/overview")
        time.sleep(5) # Wartezeit, bis die Seite geladen ist
    except Exception as e:
        raise Exception(f"Fehler beim Navigieren zur Startseite: {e}")

# --- GUI-Anwendungsklasse ---
class TypeWriterBotApp:
    def __init__(self, master):
        """
        Initialisiert die GUI-Anwendung und richtet die UI ein.
        """
        self.master = master
        self.driver = None  # Speichert die Selenium WebDriver-Instanz
        self.is_running = False  # Flag zur Steuerung der Bot-Ausführung
        self.bot_thread = None  # Speichert den Thread für die Bot-Ausführung

        self._setup_ui() # Richtet die Benutzeroberfläche ein
        self._load_initial_values() # Lädt gespeicherte oder setzt Standardwerte
        self._bind_events() # Bindet Ereignisse an GUI-Elemente
        self._on_mode_change() # Ruft dies einmal auf, um den Anfangszustand der URL/Anzahl-Felder festzulegen
        self._on_typing_style_change() # Ruft dies einmal auf, um den Anfangszustand der Fehler-Felder festzulegen


    def _setup_ui(self):
        """
        Richtett die grafische Benutzeroberfläche ein.
        """
        self.master.title("TypeWriter Bot")
        self.master.geometry("450x740") # Angepasste Höhe für neuen Parameter (ca. +40px)
        self.master.resizable(True, True)
        self.master.configure(bg="#2e2e2e") # Dunkler Hintergrund für das Hauptfenster

        # Konfiguriert ttk-Stile für ein modernes Aussehen
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TLabel", background="#2e2e2e", foreground="white", font=("Segoe UI", 10))
        style.configure("TEntry", padding=5)
        style.configure("TButton",
                        background="#555",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        padding=6,
                        relief="flat")
        style.map("TButton", background=[("active", "#777")]) # Farbe beim Hover
        style.configure("TCheckbutton", background="#2e2e2e", foreground="white", font=("Segoe UI", 10))
        style.configure("TCombobox", padding=5)
        style.configure("Horizontal.TScale", background="#2e2e2e", troughcolor="#444", sliderrelief="flat")
        style.configure("TFrame", background="#2e2e2e") # Stellt sicher, dass der Frame-Hintergrund dunkel ist

        self.container = ttk.Frame(self.master, padding=20, style="TFrame")
        self.container.pack(expand=True, fill="both")

        # Variablen für die GUI-Eingabefelder
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.save_credentials_var = tk.BooleanVar()
        self.mistake_var = tk.BooleanVar()
        self.mistake_chance_var = tk.StringVar()
        self.mistake_cluster_chance_var = tk.StringVar()
        self.browser_var = tk.StringVar()
        self.mode_var = tk.StringVar()
        self.count_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.speed_var = tk.IntVar()
        self.typing_style_var = tk.StringVar() # NEU: Für Tippstil

        # Erstellen der Eingabefelder
        self._add_label_entry("Benutzername:", self.username_var)
        self._add_label_entry("Passwort:", self.password_var, is_password=True)

        # Checkbox zum Speichern der Anmeldedaten
        ttk.Checkbutton(self.container, text="Anmeldedaten speichern", variable=self.save_credentials_var).pack(anchor="w", pady=(5,0))

        ttk.Label(self.container, text="Browser:").pack(anchor="w", pady=(10, 0))
        self.browser_combobox = ttk.Combobox(self.container, textvariable=self.browser_var, values=["f", "c", "e"], state="readonly")
        self.browser_combobox.pack(fill="x")
        self.browser_combobox.set("f") # Standardwert

        ttk.Label(self.container, text="Modus:").pack(anchor="w", pady=(10, 0))
        self.mode_combobox = ttk.Combobox(self.container, textvariable=self.mode_var, values=["login", "exercise"], state="readonly")
        self.mode_combobox.pack(fill="x")
        self.mode_combobox.set("login") # Standardwert

        ttk.Label(self.container, text="Tippgeschwindigkeit (Zeichen/Min):").pack(anchor="w", pady=(10, 0))
        self.speed_slider = ttk.Scale(self.container, from_=50, to=1000, orient="horizontal",
                                         variable=self.speed_var, style="Horizontal.TScale")
        self.speed_slider.pack(fill="x")

        self.speed_display = ttk.Label(self.container, text=str(self.speed_var.get()))
        self.speed_display.pack(anchor="e")

        # NEU: Tippstil-Auswahl
        ttk.Label(self.container, text="Tippstil:").pack(anchor="w", pady=(10, 0))
        self.typing_style_combobox = ttk.Combobox(self.container, textvariable=self.typing_style_var,
                                                   values=["Perfekt", "Anfänger", "Fortgeschritten"], state="readonly")
        self.typing_style_combobox.pack(fill="x")
        self.typing_style_combobox.set("Fortgeschritten") # Standardwert

        self.mistake_checkbox = ttk.Checkbutton(self.container, text="Tippfehler simulieren", variable=self.mistake_var)
        self.mistake_checkbox.pack(anchor="w", pady=(10,0))
        self.mistake_chance_entry = self._add_label_entry("Basis-Fehlerquote (%):", self.mistake_chance_var)
        self.mistake_cluster_chance_entry = self._add_label_entry("Chance für zusätzlichen Fehler nach Tippfehler (%):", self.mistake_cluster_chance_var)

        self.count_entry = self._add_label_entry("Anzahl Übungen (nur bei 'login'):", self.count_var)
        self.url_entry = self._add_label_entry("Übungs-URL (nur bei 'exercise'):", self.url_var)

        # Statusanzeige
        self.status_label = ttk.Label(self.container, text="Bereit", foreground="white")
        self.status_label.pack(anchor="center", pady=(15, 5))

        # Buttons
        self.start_button = ttk.Button(self.container, text="Start", command=self._on_start_button_click)
        self.start_button.pack(pady=(10, 5), fill="x")

        self.stop_button = ttk.Button(self.container, text="Stop", command=self._stop_bot, state=tk.DISABLED)
        self.stop_button.pack(pady=(0, 10), fill="x")

    def _add_label_entry(self, label_text, variable, is_password=False):
        """
        Hilfsfunktion zum Erstellen eines Labels und eines Eingabefeldes.
        """
        ttk.Label(self.container, text=label_text).pack(anchor="w", pady=(5, 0))
        entry = ttk.Entry(self.container, textvariable=variable, show="*" if is_password else "")
        entry.pack(fill="x")
        return entry

    def _load_initial_values(self):
        """
        Lädt gespeicherte Anmeldedaten und Einstellungen aus den Dateien oder setzt Standardwerte.
        """
        # Anmeldedaten laden
        if os.path.exists(CREDENTIALS_FILE):
            try:
                with open(CREDENTIALS_FILE, 'r') as f:
                    data = json.load(f)
                    self.username_var.set(data.get("username", ""))
                    self.password_var.set(data.get("password", ""))
                    self.save_credentials_var.set(data.get("save_credentials", False))
            except json.JSONDecodeError:
                messagebox.showwarning("Ladefehler", "Fehler beim Lesen der Anmeldedatendatei. Setze Standardwerte.")
                self.username_var.set("")
                self.password_var.set("")
                self.save_credentials_var.set(False)
        else:
            self.username_var.set("")
            self.password_var.set("")
            self.save_credentials_var.set(False)

        # Einstellungen laden
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    self.mistake_var.set(data.get("mistake_sim", False))
                    self.mistake_chance_var.set(str(data.get("mistake_chance", 10)))
                    self.mistake_cluster_chance_var.set(str(data.get("mistake_cluster_chance", 30)))
                    self.browser_var.set(data.get("browser", "f"))
                    self.mode_var.set(data.get("mode", "login"))
                    self.count_var.set(str(data.get("count", 1)))
                    self.url_var.set(data.get("url", ""))
                    self.speed_var.set(data.get("speed", 300))
                    self.typing_style_var.set(data.get("typing_style", "Fortgeschritten")) # NEU: Tippstil laden
            except json.JSONDecodeError:
                messagebox.showwarning("Ladefehler", "Fehler beim Lesen der Einstellungsdatei. Setze Standardwerte.")
                self._set_default_settings()
        else:
            self._set_default_settings()

        self.speed_display.config(text=str(self.speed_var.get()))

    def _set_default_settings(self):
        """
        Setzt Standardwerte für die GUI-Variablen (außer Anmeldedaten).
        """
        self.mistake_var.set(False)
        self.mistake_chance_var.set("10")
        self.mistake_cluster_chance_var.set("30")
        self.browser_var.set("f")
        self.mode_var.set("login")
        self.count_var.set("1")
        self.url_var.set("")
        self.speed_var.set(300)
        self.typing_style_var.set("Fortgeschritten") # Standardwert für Tippstil

    def _save_credentials(self):
        """
        Speichert die Anmeldedaten in einer Datei, wenn die Checkbox aktiviert ist.
        """
        if self.save_credentials_var.get():
            data = {
                "username": self.username_var.get(),
                "password": self.password_var.get(),
                "save_credentials": True
            }
            try:
                with open(CREDENTIALS_FILE, 'w') as f:
                    json.dump(data, f, indent=4) # indent für bessere Lesbarkeit
            except Exception as e:
                messagebox.showerror("Speicherfehler", f"Konnte Anmeldedaten nicht speichern: {e}")
        else:
            # Lösche die Datei, wenn die Checkbox deaktiviert ist und die Datei existiert
            if os.path.exists(CREDENTIALS_FILE):
                try:
                    os.remove(CREDENTIALS_FILE)
                except Exception as e:
                    messagebox.showwarning("Löschfehler", f"Konnte Anmeldedatendatei nicht löschen: {e}")

    def _save_settings(self):
        """
        Speichert die aktuellen Einstellungen in einer Datei.
        """
        settings = {
            "mistake_sim": self.mistake_var.get(),
            "mistake_chance": float(self.mistake_chance_var.get()),
            "mistake_cluster_chance": float(self.mistake_cluster_chance_var.get()),
            "browser": self.browser_var.get(),
            "mode": self.mode_var.get(),
            "count": int(self.count_var.get()),
            "url": self.url_var.get(),
            "speed": self.speed_var.get(),
            "typing_style": self.typing_style_var.get() # NEU: Tippstil speichern
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            messagebox.showerror("Speicherfehler", f"Konnte Einstellungen nicht speichern: {e}")


    def _bind_events(self):
        """
        Bindet Ereignisse an GUI-Elemente (z.B. Slider-Bewegung, Moduswechsel).
        """
        self.speed_slider.bind("<ButtonRelease-1>", self._update_speed_display)
        self.speed_slider.bind("<B1-Motion>", self._update_speed_display)
        self.mode_var.trace_add("write", self._on_mode_change)
        self.typing_style_var.trace_add("write", self._on_typing_style_change) # NEU: Für Tippstil-Änderung
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """
        Wird aufgerufen, wenn das Fenster geschlossen wird.
        Stellt sicher, dass die Anmeldedaten und Einstellungen gespeichert werden und der Bot gestoppt wird.
        """
        self._save_credentials() # Speichert die Anmeldedaten
        self._save_settings() # Speichert die Einstellungen
        self._stop_bot() # Stoppt den Bot, falls er läuft
        self.master.destroy() # Schließt das Fenster

    def _update_speed_display(self, event=None):
        """
        Aktualisiert den angezeigten Geschwindigkeitswert des Sliders.
        Rundet auf die nächsten 10er-Schritte.
        """
        val = int(self.speed_var.get())
        val_rounded = (val // 10) * 10
        self.speed_var.set(val_rounded)
        self.speed_display.config(text=str(val_rounded))

    def _on_mode_change(self, *args):
        """
        Aktiviert/deaktiviert Eingabefelder basierend auf dem ausgewählten Modus.
        (z.B. URL-Feld nur im 'exercise'-Modus aktiv).
        """
        if self.mode_var.get() == "exercise":
            self.url_entry.config(state=tk.NORMAL)
            self.count_var.set("1") # Setzt die Anzahl auf 1 für den Übungsmodus (einzelne Übung)
            self.count_entry.config(state=tk.DISABLED)
        else: # login-Modus
            self.url_var.set("") # Löscht die URL für den Login-Modus
            self.url_entry.config(state=tk.DISABLED)
            self.count_entry.config(state=tk.NORMAL)

    def _on_typing_style_change(self, *args):
        """
        Passt die Zustände der Fehler-Checkboxen und Eingabefelder
        basierend auf dem ausgewählten Tippstil an.
        """
        selected_style = self.typing_style_var.get()
        if selected_style == "Perfekt":
            self.mistake_checkbox.config(state=tk.DISABLED)
            self.mistake_var.set(False) # Sicherstellen, dass Fehler aus sind
            self.mistake_chance_entry.config(state=tk.DISABLED)
            self.mistake_cluster_chance_entry.config(state=tk.DISABLED)
            self.mistake_chance_var.set("0")
            self.mistake_cluster_chance_var.set("0")
        elif selected_style == "Anfänger":
            self.mistake_checkbox.config(state=tk.DISABLED) # Fehler werden immer simuliert
            self.mistake_var.set(True)
            self.mistake_chance_entry.config(state=tk.DISABLED) # Feste Werte
            self.mistake_cluster_chance_entry.config(state=tk.DISABLED) # Feste Werte
            self.mistake_chance_var.set("20") # Fester Wert für Anfänger
            self.mistake_cluster_chance_var.set("50") # Fester Wert für Anfänger
        else: # Fortgeschritten (oder Standard)
            self.mistake_checkbox.config(state=tk.NORMAL)
            self.mistake_chance_entry.config(state=tk.NORMAL)
            self.mistake_cluster_chance_entry.config(state=tk.NORMAL)
            # Werte bleiben erhalten oder werden aus den Einstellungen geladen

    def _validate_inputs(self):
        """
        Validiert Benutzereingaben, bevor der Bot gestartet wird.
        Zeigt Fehlermeldungen über messagebox an.
        """
        username = self.username_var.get()
        password = self.password_var.get()
        mode = self.mode_var.get()
        url = self.url_var.get()
        typing_style = self.typing_style_var.get()

        if not username:
            messagebox.showerror("Fehler", "Bitte Benutzernamen eingeben.")
            return False
        if not password and mode == "login":
             messagebox.showerror("Fehler", "Bitte Passwort eingeben.")
             return False

        try:
            speed = int(self.speed_var.get())
            if not (50 <= speed <= 1000):
                messagebox.showerror("Fehler", "Tippgeschwindigkeit muss zwischen 50 und 1000 liegen.")
                return False
        except ValueError:
            messagebox.showerror("Fehler", "Tippgeschwindigkeit muss eine gültige Zahl sein.")
            return False

        # Fehlerquoten-Validierung nur, wenn sie vom Benutzer beeinflusst werden können
        if typing_style not in ["Perfekt", "Anfänger"]:
            try:
                mistake_chance = float(self.mistake_chance_var.get())
                if not (0 <= mistake_chance <= 100):
                    messagebox.showerror("Fehler", "Basis-Fehlerquote muss zwischen 0 und 100 liegen.")
                    return False
            except ValueError:
                messagebox.showerror("Fehler", "Basis-Fehlerquote muss eine gültige Zahl sein.")
                return False

            try:
                mistake_cluster_chance = float(self.mistake_cluster_chance_var.get())
                if not (0 <= mistake_cluster_chance <= 100):
                    messagebox.showerror("Fehler", "Chance für zusätzlichen Fehler muss zwischen 0 und 100 liegen.")
                    return False
            except ValueError:
                messagebox.showerror("Fehler", "Chance für zusätzlichen Fehler muss eine gültige Zahl sein.")
                return False

        if mode == "login":
            try:
                count = int(self.count_var.get())
                if count <= 0:
                    messagebox.showerror("Fehler", "Anzahl Übungen muss größer als 0 sein.")
                    return False
            except ValueError:
                messagebox.showerror("Fehler", "Anzahl Übungen muss eine gültige Zahl sein.")
                return False
        elif mode == "exercise":
            if not url:
                messagebox.showerror("Fehler", "Bitte die Übungs-URL eingeben im Modus 'exercise'.")
                return False

        return True

    def _on_start_button_click(self):
        """
        Behandelt das Klicken des 'Start'-Buttons.
        Validiert Eingaben und startet die Bot-Logik in einem separaten Thread.
        """
        if not self._validate_inputs():
            return

        # Speichert die Anmeldedaten und Einstellungen beim Start
        self._save_credentials()
        self._save_settings()

        # Deaktiviert den Start-Button, aktiviert den Stop-Button und setzt den Status
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True
        self.status_label.config(text="Bot wird gestartet...", foreground="blue")

        # Startet die Bot-Logik in einem neuen Thread, um die GUI reaktionsfähig zu halten
        self.bot_thread = threading.Thread(target=self._run_bot_logic)
        self.bot_thread.daemon = True # Erlaubt dem Thread, mit dem Hauptprogramm zu beenden
        self.bot_thread.start()

    def _stop_bot(self):
        """
        Behandelt das Klicken des 'Stop'-Buttons.
        Setzt das is_running-Flag, um die Bot-Logik zu beenden.
        """
        if self.is_running:
            self.is_running = False # Setzt das Flag, um die Schleife des Bots zu stoppen
            self.status_label.config(text="Bot wird gestoppt...", foreground="orange")
            # Der Finally-Block von _run_bot_logic wird driver.quit() und die Button-Zustände behandeln

    def _run_bot_logic(self):
        """
        Enthält die Hauptautomatisierungslogik des Bots, die in einem separaten Thread ausgeführt wird.
        Umfasst umfassende Fehlerbehandlung und Statusaktualisierungen.
        """
        try:
            # Sammelt Daten aus der GUI
            data = {
                "username": self.username_var.get(),
                "password": self.password_var.get(),
                "browser": self.browser_var.get(),
                "mode": self.mode_var.get(),
                "speed": self.speed_var.get(),
                "mistake": self.mistake_var.get(),
                "mistake_chance": float(self.mistake_chance_var.get()),
                "mistake_cluster_chance": float(self.mistake_cluster_chance_var.get()),
                "count": int(self.count_var.get()),
                "url": self.url_var.get(),
                "typing_style": self.typing_style_var.get() # NEU: Tippstil übergeben
            }

            # Startet den Browser
            self.master.after(0, lambda: self.status_label.config(text="Browser wird gestartet...", foreground="blue"))
            self.driver = start_browser(data["browser"])

            if data["mode"] == "login":
                self.master.after(0, lambda: self.status_label.config(text="Anmeldung läuft...", foreground="blue"))
                Login(self.driver, data)
                for i in range(data["count"]):
                    if not self.is_running:
                        break
                    self.master.after(0, lambda: self.status_label.config(text=f"Starte Übung {i + 1} von {data['count']}...", foreground="blue"))
                    NextLesson(self.driver)
                    if not self.is_running:
                        break
                    self.master.after(0, lambda: self.status_label.config(text=f"Führe Übung {i + 1} aus (Stil: {data['typing_style']})...", foreground="blue"))
                    DoExercise(self.driver, data["speed"], data["mistake"], data["mistake_chance"], data["mistake_cluster_chance"], data["typing_style"], lambda: self.is_running)
                    if not self.is_running:
                        break
                    self.master.after(0, lambda: self.status_label.config(text=f"Gehe zur Startseite...", foreground="blue"))
                    GotoHomeScreen(self.driver)
            else: # exercise-Modus
                self.master.after(0, lambda: self.status_label.config(text="Öffne Übungs-URL...", foreground="blue"))
                try:
                    self.driver.get(data["url"])
                    self.driver.maximize_window()
                    time.sleep(2)
                except Exception as e:
                    raise Exception(f"Fehler beim Öffnen der URL: {e}")
                if self.is_running:
                    self.master.after(0, lambda: self.status_label.config(text=f"Führe Übung aus (Stil: {data['typing_style']})...", foreground="blue"))
                    DoExercise(self.driver, data["speed"], data["mistake"], data["mistake_chance"], data["mistake_cluster_chance"], data["typing_style"], lambda: self.is_running)

            # Abschließende Statusaktualisierung
            if self.is_running:
                self.master.after(0, lambda: self.status_label.config(text="Bot-Ausführung abgeschlossen!", foreground="green"))
            else:
                self.master.after(0, lambda: self.status_label.config(text="Bot gestoppt durch Benutzer.", foreground="orange"))

        except Exception as e:
            # Aktualisiert den Status und zeigt eine Fehlermeldung in der GUI an
            self.master.after(0, lambda: self.status_label.config(text=f"FEHLER: {e}", foreground="red"))
            self.master.after(0, lambda: messagebox.showerror("Fehler", str(e)))
        finally:
            # Stellt sicher, dass der Browser geschlossen und die GUI-Buttons zurückgesetzt werden
            if self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    print(f"Fehler beim Schließen des Browsers: {e}")
                self.driver = None
            self.is_running = False
            # Aktualisiert die GUI-Elemente im Haupt-Thread mit after()
            self.master.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            # Setzt den Status nur auf 'Bereit' zurück, wenn keine Fehlermeldung angezeigt wird
            if not self.status_label["text"].startswith("FEHLER:"):
                self.master.after(0, lambda: self.status_label.config(text="Bereit", foreground="white"))


# --- Hauptausführung ---
if __name__ == "__main__":
    print("TypeWriterBot GUI wird gestartet...")
    root = tk.Tk()
    app = TypeWriterBotApp(root)
    root.mainloop()