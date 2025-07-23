import http.server
import socketserver
import webbrowser
import os
import sys
import time
import subprocess # Neu: Für das Ausführen von Systembefehlen

# Den Arbeitsordner auf den Ordner des Skripts setzen
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

PORT = 8080 # Der gewünschte Port

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def release_port(port):
    """Versucht, den angegebenen Port freizugeben (unter Windows)."""
    if sys.platform == "win32":
        try:
            # Finde die PID des Prozesses, der den Port nutzt
            cmd = f'netstat -ano | findstr :{port}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='ignore')
            
            pid = None
            for line in result.stdout.splitlines():
                if "LISTEN" in line:
                    parts = line.strip().split()
                    if parts and len(parts) > 4:
                        # Die PID ist das letzte Element der Zeile
                        pid = parts[-1]
                        break
            
            if pid:
                print(f"Port {port} wird von PID {pid} belegt. Versuche, den Prozess zu beenden...")
                # Beende den Prozess
                kill_cmd = f'taskkill /PID {pid} /F'
                subprocess.run(kill_cmd, shell=True, capture_output=True)
                print(f"Prozess mit PID {pid} wurde beendet (falls vorhanden).")
                time.sleep(1) # Kurze Pause, um dem System Zeit zu geben
            else:
                print(f"Port {port} ist nicht belegt.")
        except Exception as e:
            print(f"Fehler beim Freigeben von Port {port}: {e}")
    else:
        print(f"Automatisches Freigeben von Ports wird auf {sys.platform} nicht unterstützt.")

try:
    # Versuche, den Port vor dem Start freizugeben
    release_port(PORT)

    httpd = socketserver.TCPServer(("", PORT), NoCacheHandler)
    print(f"Server läuft auf http://localhost:{PORT}")

    webbrowser.open_new_tab(f"http://localhost:{PORT}")

    httpd.serve_forever()

except OSError as e:
    print(f"Fehler: Port {PORT} ist möglicherweise belegt oder Berechtigung fehlt. {e}")
    # Wenn der Port immer noch belegt ist (z.B. von einem Dienst, der sich sofort neu startet)
    # oder Berechtigungsprobleme auftreten, gib dem Benutzer eine Fehlermeldung.
    input("Drücke Enter zum Beenden...")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nServer wird beendet.")
    httpd.shutdown()
    sys.exit(0)