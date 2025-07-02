import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import sys
import subprocess
import threading
import queue
import glob
import time

# Abhängigkeit: Pillow. Installieren mit: pip install Pillow
try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror(
        "Fehlende Bibliothek",
        "Die 'Pillow' Bibliothek wird benötigt, um das Logo anzuzeigen.\n\n"
        "Bitte installieren Sie sie mit dem Befehl:\n"
        "pip install Pillow"
    )
    sys.exit(1)


class ArgyllProfilerGUI:
    """
    Eine Tkinter-GUI zum Erstellen von Kamera-ICC-Profilen.
    Erkennt den Argyll-Pfad und Referenz-Sets automatisch und
    organisiert und bereinigt die Ausgabe.
    """
    def __init__(self, master):
        self.master = master
        master.title("Walter-Nagel ICC Premium")
        master.minsize(650, 580) # Höhe leicht angepasst

        master.columnconfigure(0, weight=1)
        master.rowconfigure(4, weight=1)

        # --- Initialisierung der Variablen ---
        self.photo_path = tk.StringVar()
        self.profile_name = tk.StringVar()
        self.selected_ref_set = tk.StringVar()
        self.available_ref_sets = {}

        self.is_argyll_path_valid = False
        self._setup_automatic_paths()
        self._create_widgets()

        if self.is_argyll_path_valid:
            self._find_reference_sets()

        self.log_queue = queue.Queue()
        self.master.after(100, self._process_log_queue)

    def _setup_automatic_paths(self):
        try:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
            self.bin_path = os.path.join(self.script_dir, "bin")
            self.is_argyll_path_valid = os.path.isdir(self.bin_path)
            if not self.is_argyll_path_valid:
                messagebox.showerror("Argyll nicht gefunden", f"Der 'bin'-Ordner wurde nicht unter '{self.bin_path}' gefunden.")
        except Exception as e:
            messagebox.showerror("Fehler bei Pfad-Erkennung", f"Ein unerwarteter Fehler ist aufgetreten: {e}")
            self.is_argyll_path_valid = False

    def _create_widgets(self):
        logo_frame = ttk.Frame(self.master)
        logo_frame.grid(row=0, column=0, pady=(10, 5))
        try:
            logo_path = os.path.join(self.script_dir, "Ressource", "Logo WalterNagel 2C.jpg")
            image = Image.open(logo_path)
            image.thumbnail((400, 100))
            self.logo_image = ImageTk.PhotoImage(image)
            ttk.Label(logo_frame, image=self.logo_image).pack()
        except Exception:
            pass

        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.grid(row=1, column=0, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        
        self.diag_button = ttk.Button(input_frame, text="Diagnose Datei erstellen", command=self._start_diagnostic_thread)
        self.diag_button.grid(row=0, column=2, sticky="e", pady=(0, 15))

        ttk.Label(input_frame, text="Scan (TIFF):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.photo_path, state="readonly").grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(input_frame, text="Datei auswählen", command=self._select_photo).grid(row=1, column=2, sticky="e")

        ttk.Label(input_frame, text="Referenzfile:").grid(row=2, column=0, sticky="w", pady=2)
        self.ref_set_combobox = ttk.Combobox(input_frame, textvariable=self.selected_ref_set, state="readonly")
        self.ref_set_combobox.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5)
        self.ref_set_combobox.set("Keine Referenz-Sets gefunden...")

        ttk.Label(input_frame, text="Name des ICC-Profils:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.profile_name).grid(row=3, column=1, columnspan=2, sticky="ew", padx=5)

        # Gamma-Checkbox wurde entfernt

        button_frame = ttk.Frame(self.master, padding="10")
        button_frame.grid(row=2, column=0, sticky="ew")

        self.create_button = ttk.Button(button_frame, text="ICC-Profil erstellen", command=self._start_profiling_thread)
        self.create_button.pack(fill='x')

        if not self.is_argyll_path_valid:
            self.create_button.config(state="disabled")
            self.diag_button.config(state="disabled")

        output_frame = ttk.Frame(self.master, padding="10")
        output_frame.grid(row=4, column=0, sticky="nsew") 
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state="disabled")
        self.output_text.grid(row=0, column=0, sticky="nsew")

    def _find_reference_sets(self):
        """Sucht nach Unterordnern im 'Referenzfiles'-Ordner."""
        self.available_ref_sets.clear()
        ref_sets_path = os.path.join(self.script_dir, "Referenzfiles")
        
        if not os.path.isdir(ref_sets_path):
            self.ref_set_combobox.set("Ordner 'Referenzfiles' nicht gefunden")
            return

        set_names = [d for d in os.listdir(ref_sets_path) if os.path.isdir(os.path.join(ref_sets_path, d))]
        
        if not set_names:
            self.ref_set_combobox.set("Keine Sets im 'Referenzfiles'-Ordner gefunden")
            return

        for name in sorted(set_names):
            self.available_ref_sets[name] = os.path.join(ref_sets_path, name)
        
        self.ref_set_combobox['values'] = sorted(set_names)
        self.ref_set_combobox.current(0)
        
    def _log(self, message): self.log_queue.put(message)

    def _process_log_queue(self):
        while not self.log_queue.empty():
            try:
                message = self.log_queue.get_nowait()
                self.output_text.config(state="normal")
                self.output_text.insert(tk.END, message)
                self.output_text.see(tk.END)
                self.output_text.config(state="disabled")
            except queue.Empty: pass
        self.master.after(100, self._process_log_queue)

    def _select_photo(self):
        path = filedialog.askopenfilename(title="Wählen Sie die Scan-Datei", filetypes=[("TIFF-Dateien", "*.tif *.tiff"), ("Alle Dateien", "*.*")])
        if path:
            self.photo_path.set(path)
            if not self.profile_name.get():
                self.profile_name.set(os.path.splitext(os.path.basename(path))[0])

    def _prepare_for_run(self):
        """Gemeinsame Vorbereitungs- und Validierungsfunktion."""
        selected_set_name = self.selected_ref_set.get()
        set_folder_path = self.available_ref_sets.get(selected_set_name)
        if not set_folder_path:
            messagebox.showerror("Fehler", "Bitte wählen Sie ein gültiges Referenzfile aus.")
            return None
        try:
            cht_file = glob.glob(os.path.join(set_folder_path, '*.cht'))[0]
            txt_file_list = glob.glob(os.path.join(set_folder_path, '*.txt')) + \
                            glob.glob(os.path.join(set_folder_path, '*.cie')) + \
                            glob.glob(os.path.join(set_folder_path, '*.it8'))
            txt_file = txt_file_list[0]
        except IndexError:
            messagebox.showerror("Fehler im Referenzfile-Ordner", f"Im Ordner '{selected_set_name}' wurde keine .cht- oder .txt-Datei gefunden.")
            return None
        if not self.photo_path.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Scan (TIFF) aus.")
            return None
        
        is_diag = threading.current_thread().name == "DiagnosticThread"
        if not is_diag and not self.profile_name.get():
            messagebox.showerror("Fehler", "Bitte geben Sie einen Namen für das ICC-Profil ein.")
            return None
        
        self.create_button.config(state="disabled")
        self.diag_button.config(state="disabled")
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")
        return cht_file, txt_file

    def _start_profiling_thread(self):
        prepared_files = self._prepare_for_run()
        if prepared_files:
            cht_file, txt_file = prepared_files
            thread = threading.Thread(target=self._run_profiling_process, args=(cht_file, txt_file), name="ProfilingThread", daemon=True)
            thread.start()

    def _start_diagnostic_thread(self):
        prepared_files = self._prepare_for_run()
        if prepared_files:
            cht_file, txt_file = prepared_files
            thread = threading.Thread(target=self._run_diagnostic_process, args=(cht_file, txt_file), name="DiagnosticThread", daemon=True)
            thread.start()

    def _run_command(self, cmd_list, expect_fail=False):
        self._log(f"\n--- Befehl wird ausgeführt ---\n{' '.join(cmd_list)}\n---------------------------\n\n")
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', startupinfo=startupinfo, cwd=self.script_dir)
        for line in iter(process.stdout.readline, ''): self._log(line)
        process.stdout.close()
        return_code = process.wait()
        if not expect_fail and return_code != 0: raise subprocess.CalledProcessError(return_code, cmd_list)
        
    def _open_folder(self, path):
        try:
            if sys.platform == "win32": os.startfile(os.path.normpath(path))
            elif sys.platform == "darwin": subprocess.run(["open", path])
            else: subprocess.run(["xdg-open", path])
            self._log(f"\nÖffne: {path}\n")
        except Exception as e: self._log(f"\nFehler beim Öffnen von {path}: {e}\n")

    def _run_profiling_process(self, cht_file, txt_file):
        """Führt den kompletten Prozess zur Profilerstellung aus."""
        try:
            photo_file, profile_name_base = self.photo_path.get(), self.profile_name.get()
            ti3_input_prefix = os.path.splitext(photo_file)[0]
            exe_suffix = ".exe" if sys.platform == "win32" else ""
            scanin_cmd = os.path.join(self.bin_path, "scanin" + exe_suffix)
            colprof_cmd = os.path.join(self.bin_path, "colprof" + exe_suffix)
            gamma = "2.2" # Gamma ist jetzt fest auf 2.2 gesetzt

            self._log(">>> Schritt 1: Starte 'scanin' zur Analyse des Scans...\n")
            scanin_args = [scanin_cmd, "-v", "-p", "-G", gamma, photo_file, cht_file, txt_file]
            self._run_command(scanin_args)
            self._log("\n>>> 'scanin' erfolgreich abgeschlossen.\n")

            self._log(">>> Schritt 2: Starte 'colprof' zur Erstellung des ICC-Profils...\n")
            colprof_args = [
                colprof_cmd, "-v",
                "-A", "Walter Nagel",
                "-D", profile_name_base,
                "-qh", "-al",
                ti3_input_prefix
            ]
            self._run_command(colprof_args)

            self._log("\n>>> Prüfe auf erstellte Profildatei...\n")
            time.sleep(1)

            generated_path = ti3_input_prefix + ".icc" if os.path.exists(ti3_input_prefix + ".icc") else ti3_input_prefix + ".icm"
            
            if os.path.exists(generated_path):
                main_output_dir = os.path.join(self.script_dir, "ICC_Profile")
                profile_specific_dir = os.path.join(main_output_dir, profile_name_base)
                os.makedirs(profile_specific_dir, exist_ok=True)
                final_icc_path = os.path.join(profile_specific_dir, profile_name_base + ".icc")
                
                if os.path.exists(final_icc_path): os.remove(final_icc_path)
                os.rename(generated_path, final_icc_path)

                self._log(f"\n>>> 'colprof' erfolgreich abgeschlossen.\n")
                self._log(f"\n======================================================\n")
                self._log(f" ERFOLG: ICC-Profil wurde erstellt und gespeichert in:\n {final_icc_path}\n")
                self._log(f"======================================================\n")
                
                ti3_file_path = ti3_input_prefix + ".ti3"
                if os.path.exists(ti3_file_path):
                    try:
                        os.remove(ti3_file_path)
                        self._log(f"\nTemporäre .ti3-Datei wurde gelöscht.\n")
                    except OSError as e: self._log(f"\nFehler beim Löschen der .ti3-Datei: {e}\n")
                self._open_folder(profile_specific_dir)
            else:
                raise FileNotFoundError("colprof hat keine .icc oder .icm Datei erstellt.")

        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            self._log(f"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            self._log(f" FEHLER: Der Prozess wurde abgebrochen.\n")
            self.log_queue.put(f" Grund: {str(e)}\n")
            self._log(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        finally:
            self.create_button.config(state="normal")
            self.diag_button.config(state="normal")
            
    def _run_diagnostic_process(self, cht_file, txt_file):
        """Führt nur scanin im Diagnose-Modus aus."""
        try:
            photo_file = self.photo_path.get()
            scanin_cmd = os.path.join(self.bin_path, "scanin.exe" if sys.platform == "win32" else "scanin")
            gamma = "2.2" # Gamma ist jetzt fest auf 2.2 gesetzt

            self._log(">>> Starte 'scanin' im Diagnose-Modus...\n")
            scanin_args = [scanin_cmd, "-v", "-dp", "-G", gamma, photo_file, cht_file, txt_file]
            
            self._run_command(scanin_args, expect_fail=True)
            self._log("\n>>> 'scanin' beendet. Prüfe auf Diagnose-Datei...\n")

            diag_file = os.path.join(self.script_dir, "diag.tif")
            if os.path.exists(diag_file):
                self._log(f"\n======================================================\n")
                self._log(f" ERFOLG: Diagnose-Datei wurde erstellt:\n {diag_file}\n")
                self._log(f"======================================================\n")
                self._open_folder(diag_file)
            else:
                self._log("\n>>> FEHLER: 'scanin' hat die Diagnose-Datei nicht erstellt.\n")

        except Exception as e:
            self._log(f"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            self._log(f" FEHLER: Der Prozess wurde abgebrochen.\n")
            self.log_queue.put(f" Grund: {str(e)}\n")
            self._log(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        finally:
            self.create_button.config(state="normal")
            self.diag_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArgyllProfilerGUI(root)
    root.mainloop()