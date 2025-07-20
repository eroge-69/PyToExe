import customtkinter as ctk
import os
import subprocess
import threading
import time
import urllib.request
from datetime import datetime
import sys
import ctypes
from tkinter import messagebox


# --- FUNKTIONEN FÜR ADMIN-RECHTE ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
    params = f'"{os.path.abspath(__file__)}"'
    ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)


# --- BENUTZERDEFINIERTE WIDGETS ---
class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_fg_color = self.cget("fg_color");
        self._pressed_fg_color = self._darken_color(self._original_fg_color)
        self.bind("<Button-1>", self._on_press);
        self.bind("<ButtonRelease-1>", self._on_release)

    def _darken_color(self, color_tuple):
        if isinstance(color_tuple, tuple) and len(color_tuple) == 2:
            dark_colors = []
            for color in color_tuple:
                if color.startswith("#"):
                    r, g, b = tuple(int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4));
                    r, g, b = max(0, r - 25), max(0, g - 25), max(0, b - 25)
                    dark_colors.append(f"#{r:02x}{g:02x}{b:02x}")
                else:
                    dark_colors.append(color)
            return tuple(dark_colors)
        return color_tuple

    def _on_press(self, event):
        if self.cget("state") == "normal": self.configure(fg_color=self._pressed_fg_color)

    def _on_release(self, event):
        if self.cget("state") == "normal": self.configure(fg_color=self._original_fg_color)


class AnimatedCheckBox(ctk.CTkFrame):
    def __init__(self, master, text, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.checked = False
        self.accent_color = "#3478F6";
        self.border_color_unchecked = "#555555";
        self.border_color_checked = self.accent_color
        self.canvas = ctk.CTkCanvas(self, width=22, height=22, bg="#242424", highlightthickness=2,
                                    highlightbackground=self.border_color_unchecked)
        self.canvas.pack(side="left")
        self.label = ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=13))
        self.label.pack(side="left", padx=12)
        self.bind("<Button-1>", self.toggle);
        self.label.bind("<Button-1>", self.toggle);
        self.canvas.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        self.checked = not self.checked;
        self.animate()

    def select(self):
        if not self.checked: self.toggle()

    def deselect(self):
        if self.checked: self.toggle()

    def get(self):
        return self.checked

    def animate(self):
        self.canvas.delete("all")
        if self.checked:
            self.canvas.configure(highlightbackground=self.border_color_checked); self.canvas.create_line(
                [(4, 11), (9, 16), (18, 7)], fill=self.accent_color, width=2.5)
        else:
            self.canvas.configure(highlightbackground=self.border_color_unchecked)


# --- HAUPTANWENDUNGSKLASSE ---
class HybridInstallerApp(ctk.CTk):
    def __init__(self, winget_path, choco_path):
        super().__init__()
        self.winget_path = winget_path
        self.choco_path = choco_path
        self.install_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Install")
        self.log_file = os.path.join(self.install_dir, "install.log")
        self.programs = [
            {'name': 'Google Chrome', 'winget_id': 'Google.Chrome', 'choco_id': 'googlechrome'},
            {'name': 'Mozilla Firefox', 'winget_id': 'Mozilla.Firefox', 'choco_id': 'firefox'},
            {'name': '7-Zip', 'winget_id': '7zip.7zip', 'choco_id': '7zip.install'},
            {'name': 'VLC Media Player', 'winget_id': 'VideoLAN.VLC', 'choco_id': 'vlc'},
            {'name': 'PDF24 Creator', 'winget_id': 'pdfforge.PDF24', 'choco_id': 'pdf24'},
            {'name': 'Adobe Acrobat Reader', 'winget_id': 'Adobe.Acrobat.ReaderDC', 'choco_id': 'adobereader'},
            {'name': 'Stetzberger Fernwartung', 'type': 'download',
             'url': 'https://edv-stetzberger.de/fileadmin/stetzberger_computer/user_uploads/Stetzberger_Fernwartung.exe',
             'filename': 'Stetzberger_Fernwartung.exe'}
        ]
        self.checkboxes = [];
        self.accent_color = "#3478F6";
        self.is_checking = False
        self.cancel_flag = threading.Event()
        self.title("Software Installer v21.0 (Hybrid FINAL)");
        self.geometry("480x700");
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark");
        self.configure(fg_color="#1a1a1a")
        if not os.path.exists(self.install_dir): os.makedirs(self.install_dir)
        self.create_widgets()
        threading.Thread(target=self.check_installed_programs, daemon=True).start()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent");
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        title_label = ctk.CTkLabel(main_frame, text="Software auswählen", font=ctk.CTkFont(size=24, weight="bold"));
        title_label.pack(pady=(10, 20))
        checkbox_frame = ctk.CTkScrollableFrame(main_frame, fg_color="#242424", border_color="#333333", border_width=2)
        checkbox_frame.pack(fill="both", expand=True)
        for program in self.programs:
            checkbox = AnimatedCheckBox(checkbox_frame, text=program['name']);
            checkbox.pack(fill="x", padx=15, pady=12)
            self.checkboxes.append({'widget': checkbox, 'program': program})

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        button_frame.grid_columnconfigure((0, 1), weight=1)

        self.select_all_button = AnimatedButton(button_frame, text="Alle auswählen", command=self.select_all,
                                                fg_color="#333333", hover_color="#444444")
        self.select_all_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.deselect_all_button = AnimatedButton(button_frame, text="Auswahl entfernen", command=self.deselect_all,
                                                  fg_color="#333333", hover_color="#444444")
        self.deselect_all_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent");
        status_frame.pack(fill="x", pady=10)
        self.status_label = ctk.CTkLabel(status_frame, text="Initialisiere...", font=ctk.CTkFont(size=12),
                                         text_color="#999999");
        self.status_label.pack()
        self.progress_bar = ctk.CTkProgressBar(status_frame, progress_color=self.accent_color);
        self.progress_bar.set(0);
        self.progress_bar.pack(fill="x", pady=(10, 5))

        action_button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_button_frame.pack(fill="x", pady=(10, 0))
        action_button_frame.grid_columnconfigure(0, weight=3)
        action_button_frame.grid_columnconfigure(1, weight=1)

        self.install_button = AnimatedButton(action_button_frame, text="Installation starten",
                                             command=self.start_installation_thread, height=50,
                                             font=ctk.CTkFont(size=16, weight="bold"),
                                             fg_color=(self.accent_color, self.accent_color),
                                             hover_color=("#3069d1", "#3069d1"))
        self.install_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.cancel_button = AnimatedButton(action_button_frame, text="Abbrechen", command=self.cancel_installation,
                                            height=50, fg_color="#555555", hover_color="#666666", state="disabled")
        self.cancel_button.grid(row=0, column=1, sticky="ew")

    def check_installed_programs(self):
        self.after(0, self.start_checking_animation)
        if self.winget_path:
            for item in self.checkboxes:
                program = item['program']
                if program.get('winget_id'):
                    try:
                        command = [self.winget_path, 'list', '--id', program['winget_id'], '-e',
                                   '--accept-source-agreements']
                        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                                                 creationflags=subprocess.CREATE_NO_WINDOW)
                        if process.returncode == 0 and program['winget_id'].lower() in process.stdout.lower():
                            version = "unbekannt";
                            for line in process.stdout.splitlines():
                                if program['winget_id'].lower() in line.lower():
                                    parts = line.split();
                                    if len(parts) > 1: version = parts[1]
                                    break
                            new_text = f"{program['name']} ({version} installiert)"
                            self.after(0,
                                       lambda widget=item['widget'], text=new_text: widget.label.configure(text=text))
                    except Exception as e:
                        self.write_log(f"Fehler bei der Prüfung von '{program['name']}': {e}")
        self.is_checking = False

    def start_checking_animation(self):
        self.is_checking = True
        self.install_button.configure(state="disabled");
        self.select_all_button.configure(state="disabled");
        self.deselect_all_button.configure(state="disabled")
        self._animate_checking_button()

    def _animate_checking_button(self, dot_count=1):
        if not self.is_checking:
            self.install_button.configure(text="Installation starten", state="normal")
            self.select_all_button.configure(state="normal");
            self.deselect_all_button.configure(state="normal")
            self.status_label.configure(text="Bereit zur Installation (Admin-Modus).")
            return
        new_text = "Überprüfe" + "." * dot_count
        self.install_button.configure(text=new_text)
        self.status_label.configure(text="Prüfe installierte Software...")
        next_dot_count = (dot_count % 3) + 1
        self.after(400, lambda: self._animate_checking_button(next_dot_count))

    def select_all(self):
        for cb in self.checkboxes: cb['widget'].select()

    def deselect_all(self):
        for cb in self.checkboxes: cb['widget'].deselect()

    def write_log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S");
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Konnte nicht in Log-Datei schreiben: {e}")

    def start_installation_thread(self):
        self.cancel_flag.clear()
        self.install_button.configure(state="disabled", text="Arbeite...")
        self.cancel_button.configure(state="normal")
        threading.Thread(target=self.run_installation, daemon=True).start()

    def cancel_installation(self):
        self.status_label.configure(text="Abbruch wird angefordert...", text_color="orange")
        self.cancel_flag.set()
        self.cancel_button.configure(state="disabled")

    def run_installation(self):
        self.write_log("==================== AKTION GESTARTET ====================")
        selected_items = [cb['program'] for cb in self.checkboxes if cb['widget'].get()]
        total = len(selected_items)
        if total == 0: self.status_label.configure(text="Status: Nichts ausgewählt."); self.install_button.configure(
            state="normal"); self.cancel_button.configure(state="disabled"); return

        failed_items = []
        for i, program in enumerate(selected_items):
            if self.cancel_flag.is_set(): self.write_log("Aktion vom Benutzer abgebrochen."); break

            self.progress_bar.set((i + 1) / total)
            program_type = program.get('type')
            success = False

            try:
                if program_type == 'download':
                    self.status_label.configure(text=f"Lade {program['name']} herunter...")
                    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop');
                    save_path = os.path.join(desktop_path, program['filename'])
                    urllib.request.urlretrieve(program['url'], save_path)
                    success = True
                else:  # Hybrid-Installation
                    if self.winget_path:
                        self.status_label.configure(text=f"Versuch 1/2 (winget): {program['name']}")
                        command = [self.winget_path, 'install', '--id', program['winget_id'], '-e', '--silent',
                                   '--accept-source-agreements', '--accept-package-agreements']
                        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                                                 creationflags=subprocess.CREATE_NO_WINDOW)
                        success_codes = [0, 3010, 1641, 2316632107]
                        if process.returncode in success_codes:
                            success = True
                        else:
                            self.write_log(
                                f"WINGET-FEHLER bei '{program['name']}': Code {process.returncode}\n{process.stderr}")

                    if not success and self.choco_path:
                        self.status_label.configure(text=f"Versuch 2/2 (choco): {program['name']}")
                        command = [self.choco_path, 'install', program['choco_id'], '-y']
                        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                                                 creationflags=subprocess.CREATE_NO_WINDOW)
                        if process.returncode == 0:
                            success = True
                        else:
                            self.write_log(
                                f"CHOCO-FEHLER bei '{program['name']}': Code {process.returncode}\n{process.stderr}")

                if not success: raise RuntimeError("Beide Installationsmethoden sind fehlgeschlagen.")

            except Exception as e:
                self.write_log(f"FINALER FEHLER bei '{program['name']}': {e}")
                failed_items.append(program['name'])

        # Finale Statusmeldung
        if self.cancel_flag.is_set():
            self.status_label.configure(text="Aktion erfolgreich abgebrochen.", text_color="orange")
        elif not failed_items:
            self.status_label.configure(text="Status: Alle Aktionen erfolgreich abgeschlossen!",
                                        text_color=self.accent_color)
        else:
            self.status_label.configure(text=f"Status: Abgeschlossen mit {len(failed_items)} Fehlern.",
                                        text_color="orange")
            error_summary = "\n- ".join(failed_items)
            messagebox.showwarning("Installation unvollständig",
                                   f"Folgende Programme konnten nicht verarbeitet werden:\n\n- {error_summary}")

        self.write_log("==================== AKTION BEENDET ====================")
        self.install_button.configure(state="normal", text="Installation starten")
        self.cancel_button.configure(state="disabled")


# --- HAUPTEINSTIEGSPUNKT MIT PRÜFUNG ---
def main():
    if not is_admin():
        run_as_admin()
        return

    winget_path, choco_path = None, None
    try:
        winget_path = subprocess.check_output(['where', 'winget'], text=True,
                                              creationflags=subprocess.CREATE_NO_WINDOW).strip().split('\n')[0]
    except Exception:
        pass
    try:
        choco_path = \
        subprocess.check_output(['where', 'choco'], text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip().split(
            '\n')[0]
    except Exception:
        pass

    if not winget_path and not choco_path:
        messagebox.showerror("Voraussetzung fehlt",
                             "Kein unterstützter Paketmanager (winget oder Chocolatey) wurde gefunden.")
        return

    app = HybridInstallerApp(winget_path=winget_path, choco_path=choco_path)
    app.mainloop()


if __name__ == "__main__":
    main()