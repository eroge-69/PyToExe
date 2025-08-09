import win32gui
import win32con
import random
import time
import sys
import os

# Sicherheitsabfrage beim Start
antwort = win32gui.MessageBox(
    0,
    "Möchten Sie dieses Programm wirklich ausführen?",
    "Sicherheitsabfrage",
    win32con.MB_YESNO | win32con.MB_ICONQUESTION
)

if antwort != win32con.IDYES:
    sys.exit()  # Programm beenden, wenn der Nutzer "Nein" klickt

# Bildschirmgröße
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Icon-Typen
icons = [
    win32gui.LoadIcon(0, win32con.IDI_ERROR),
    win32gui.LoadIcon(0, win32con.IDI_WARNING),
    win32gui.LoadIcon(0, win32con.IDI_INFORMATION),
    win32gui.LoadIcon(0, win32con.IDI_QUESTION)
]


# Ordner & Fake-EXE-Dateien erstellen (auf dem Desktop)
def create_folders_with_exes():
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "PingVirus")
    try:
        os.makedirs(desktop_path, exist_ok=True)
        for i in range(5):
            folder_path = os.path.join(desktop_path, f"Ordner_{i+1}")
            os.makedirs(folder_path, exist_ok=True)
            exe_path = os.path.join(folder_path, f"fake{i+1}.exe")
            with open(exe_path, "w") as f:
                f.write("Dies ist keine echte .exe Datei.\n")
    except Exception as e:
        win32gui.MessageBox(0, str(e), "Fehler beim Erstellen der Dateien", win32con.MB_ICONERROR)



def draw_random_icon():
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)

    for _ in range(10):  # 10 Icons pro Durchlauf
        x = random.randint(0, SCREEN_WIDTH - 32)
        y = random.randint(0, SCREEN_HEIGHT - 32)
        icon = random.choice(icons)
        win32gui.DrawIcon(hdc, x, y, icon)

    win32gui.ReleaseDC(hwnd, hdc)

def show_random_error_window():
    messages = [
        ("Fehler", "Ein unerwarteter Fehler ist aufgetreten.", win32con.MB_ICONERROR),
        ("Warnung", "Achtung! Systemressourcen sind niedrig.", win32con.MB_ICONWARNING),
        ("Information", "Update erfolgreich abgeschlossen.", win32con.MB_ICONINFORMATION),
        ("Frage", "Möchten Sie die Aktion wirklich ausführen?", win32con.MB_ICONQUESTION),
        ("Systemfehler", "Kritischer Systemfehler. Neustart empfohlen.", win32con.MB_ICONERROR),
        ("Netzwerk", "Verbindung verloren. Versuchen Sie es erneut.", win32con.MB_ICONWARNING)
    ]

    title, text, icon = random.choice(messages)
    win32gui.MessageBox(0, text, title, icon | win32con.MB_OK)

# === Start ===
create_folders_with_exes()

# Hauptschleife
while True:
    draw_random_icon()

    if random.random() < 0.1:
        show_random_error_window()

    time.sleep(0.1)
