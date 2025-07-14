import os
import time
import ctypes
import subprocess
import sys
import traceback
import logging

# === DEBUG-LOGGING EINRICHTEN ===
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launcher_debug.log")
logging.basicConfig(
    filename=log_path,
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Skript gestartet.")

# === ADMIN-RECHTE PRÜFEN ===
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        logging.info("Starte mit Administratorrechten neu...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, '"' + '" "'.join(sys.argv) + '"', None, 0)
    except Exception as e:
        logging.error("Fehler beim Neustart mit Adminrechten: %s", str(e))
    sys.exit()

if not is_admin():
    run_as_admin()

# === FENSTER VERSTECKEN ===
try:
    import win32gui
    import win32con
    window = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(window, win32con.SW_HIDE)
    logging.info("Konsole versteckt.")
except Exception as e:
    logging.warning("Konnte Fenster nicht verstecken: %s", str(e))

# === PROGRAMMPFADE ===
gimi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3DMigoto Loader.exe")
genshin_path = r"C:\Program Files\HoYoPlay\games\Genshin Impact game\GenshinImpact.exe"

# === STARTE GIMI ===
try:
    logging.info(f"Starte GIMI: {gimi_path}")
    subprocess.Popen([
        "powershell", "-Command",
        f"Start-Process -FilePath \"{gimi_path}\" -Verb RunAs"
    ])
except Exception as e:
    logging.error("Fehler beim Start von GIMI: %s", str(e))
    logging.error(traceback.format_exc())

# === WARTE 10 SEKUNDEN ===
logging.info("Warte 10 Sekunden...")
time.sleep(2)

# === STARTE GENSHIN IMPACT ===
try:
    logging.info(f"Starte Genshin: {genshin_path}")
    subprocess.Popen([
        "powershell", "-Command",
        f"Start-Process -FilePath \"{genshin_path}\" -Verb RunAs"
    ])
except Exception as e:
    logging.error("Fehler beim Start von Genshin Impact: %s", str(e))
    logging.error(traceback.format_exc())

# === ABSCHLUSS ===
logging.info("Skript abgeschlossen.")