import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import threading
import os
import re

class HashcatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LazyCat V1.0 GUI")
        self.root.geometry("900x550")

        # Variablen
        self.handshake_file = tk.StringVar()
        self.wordlist_file = tk.StringVar()
        self.attack_mode = tk.StringVar(value="0")
        self.custom_charset = tk.StringVar()
        self.status_text = tk.StringVar(value="Bereit")
        self.cracked_result = tk.StringVar()

        # GUI aufbauen
        self.build_gui()

    def build_gui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Linke Spalte
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        font_style = ("Courier New", 10)

        tk.Label(left_frame, text="Handshake Datei:").pack(anchor="w")
        tk.Entry(left_frame, textvariable=self.handshake_file, width=80, font=font_style).pack(anchor="w")
        tk.Button(left_frame, text="Datei wählen", command=self.select_handshake).pack(anchor="w", pady=(0, 10))

        tk.Label(left_frame, text="Wörterbuch Datei:").pack(anchor="w")
        tk.Entry(left_frame, textvariable=self.wordlist_file, width=80, font=font_style).pack(anchor="w")
        tk.Button(left_frame, text="Datei wählen", command=self.select_wordlist).pack(anchor="w", pady=(0, 10))

        tk.Label(left_frame, text="Angriffsmodus (0=Wörterbuch, 3=Bruteforce):").pack(anchor="w")
        tk.Entry(left_frame, textvariable=self.attack_mode, width=5, font=font_style).pack(anchor="w")

        tk.Label(left_frame, text="Bruteforce-Muster (z. B. ?l?l?l?l?l?d):").pack(anchor="w")
        tk.Entry(left_frame, textvariable=self.custom_charset, width=30, font=font_style).pack(anchor="w")
        tk.Label(left_frame, text="Hilfestellung: ?l=Klein, ?u=Groß, ?d=Ziffer, ?s=Sonderz.").pack(anchor="w")
        tk.Label(left_frame, text="Beispiele:").pack(anchor="w")
        tk.Label(left_frame, text="  ?d?d?d?d         → 4-stellige PIN\n  ?u?l?l?l?l?d     → Passwort wie Aabcd3\n  ?l?l?l?l?l?s     → mit Sonderzeichen", justify="left").pack(anchor="w")

        tk.Button(left_frame, text="Hashcat starten", bg="green", fg="white", command=self.start_hashcat).pack(pady=10)

        self.progress = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(left_frame, variable=self.progress, maximum=100)
        self.progressbar.pack(fill="x", pady=5)
        tk.Label(left_frame, textvariable=self.status_text).pack(anchor="w")

        tk.Label(left_frame, text="Status / Log:").pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(left_frame, height=10, font=("Courier New", 9), state='disabled')
        self.log_area.pack(fill="both", expand=True, pady=(5, 0))

        tk.Label(left_frame, text="Ergebnis (falls geknackt):").pack(anchor="w", pady=(10, 0))
        self.result_area = tk.Entry(left_frame, textvariable=self.cracked_result, font=("Courier New", 10), width=80, state='readonly')
        self.result_area.pack(anchor="w", pady=(0, 10))

        # Rechte Spalte
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="y", padx=10)

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "lazycat.png")
            image = Image.open(image_path)
            image = image.resize((180, 180), Image.LANCZOS)
            self.cat_photo = ImageTk.PhotoImage(image)
            tk.Label(right_frame, image=self.cat_photo).pack()
            tk.Label(right_frame, text="LazyCat wacht... manchmal.", font=("Arial", 10, "italic")).pack()
        except Exception as e:
            tk.Label(right_frame, text="(Keine Grafik gefunden)", fg="gray").pack()
            print(f"Fehler beim Laden des Bildes: {e}")

    def select_handshake(self):
        file = filedialog.askopenfilename(title="Wähle Handshake Datei", filetypes=[("HCCAPX / PCAP", "*.hccapx *.pcap *.cap"), ("Alle Dateien", "*.*")])
        if file:
            self.handshake_file.set(file)

    def select_wordlist(self):
        file = filedialog.askopenfilename(title="Wähle Wörterbuch", filetypes=[("Text Dateien", "*.txt"), ("Alle Dateien", "*.*")])
        if file:
            self.wordlist_file.set(file)

    def start_hashcat(self):
        if not os.path.exists(self.handshake_file.get()):
            messagebox.showerror("Fehler", "Handshake Datei nicht gefunden.")
            return

        if self.attack_mode.get() == "0" and not os.path.exists(self.wordlist_file.get()):
            messagebox.showerror("Fehler", "Wörterbuch Datei nicht gefunden.")
            return

        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        self.progress.set(0)
        self.status_text.set("Hashcat wird gestartet...")
        self.cracked_result.set("")

        threading.Thread(target=self.run_hashcat, daemon=True).start()

    def run_hashcat(self):
        mode = self.attack_mode.get()
        cmd = [
            "hashcat",
            "-m", "2500",
            "-a", mode,
            self.handshake_file.get()
        ]

        if mode == "0":
            cmd.append(self.wordlist_file.get())
        elif mode == "3":
            pattern = self.custom_charset.get()
            if not pattern:
                self.append_log("Kein Bruteforce-Muster angegeben.")
                self.status_text.set("Fehler: Kein Bruteforce-Muster")
                return
            cmd.append(pattern)
        else:
            self.append_log("Ungültiger Angriffsmodus.")
            self.status_text.set("Fehler: Ungültiger Modus")
            return

        cmd += ["--status", "--status-timer=5", "--machine-readable"]

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

            for line in process.stdout:
                self.append_log(line.strip())
                progress_match = re.search(r"PROGRESS=(\d+)/(\d+)", line)
                if progress_match:
                    current = int(progress_match.group(1))
                    total = int(progress_match.group(2))
                    percent = (current / total) * 100 if total else 0
                    self.progress.set(percent)

                cracked_match = re.search(r"Recovered\s+\d+\/\d+\s+hashes", line)
                if cracked_match:
                    potfile_path = os.path.expanduser("~/.hashcat/hashcat.potfile")
                    if os.path.exists(potfile_path):
                        with open(potfile_path, "r", encoding="utf-8", errors="ignore") as f:
                            last_line = f.readlines()[-1].strip()
                            if last_line:
                                self.cracked_result.set(last_line)

            process.wait()
            self.append_log(f"Hashcat beendet mit Code {process.returncode}")
            self.status_text.set("Fertig")
        except Exception as e:
            self.append_log(f"Fehler beim Starten von Hashcat: {str(e)}")
            self.status_text.set("Fehler beim Ausführen")

    def append_log(self, text):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = HashcatGUI(root)
    root.mainloop()
