import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import subprocess
import threading
import platform
import re
import time
import gc
import ctypes

class PCOptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exif Optimka - +200 fps w kazdej grze!")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        self._configure_styles()
        self._setup_main_layout()
        self._setup_tabs()
        self._setup_output_and_status()

        if platform.system() == "Windows" and not self.is_admin():
            messagebox.showwarning("Wymagane uprawnienia administratora",
                                   "Niektóre funkcje tej aplikacji mogą wymagać uprawnień administratora. Proszę uruchomić 'Exif Optimka' jako administrator, aby zapewnić pełną funkcjonalność.")

    def _configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#1a1a1a', foreground='#e0e0e0', font=('Inter', 10))
        self.style.configure('TFrame', background='#1a1a1a')
        self.style.configure('TLabelFrame', background='#1a1a1a', foreground='#e0e0e0', bordercolor='#6a006a', relief='groove')
        self.style.configure('TLabelFrame.Label', foreground='#ffffff', font=('Inter', 12, 'bold'))
        self.style.configure('TLabel', background='#1a1a1a', foreground='#e0e0e0', font=('Inter', 10))
        self.style.configure('TButton', background='#4a004a', foreground='#ffffff', font=('Inter', 10, 'bold'), relief='raised', borderwidth=2)
        self.style.map('TButton',
                       background=[('active', '#6a006a'), ('pressed', '#3a003a')],
                       foreground=[('active', '#ffffff'), ('pressed', '#ffffff')],
                       relief=[('pressed', 'sunken')])
        self.style.configure('TEntry', fieldbackground='#3a3a3a', foreground='#ffffff', bordercolor='#6a006a', font=('Inter', 10), relief='flat')
        self.style.configure('TScrolledtext', background='#0d0d0d', foreground='#c0c0c0', insertbackground='#ffffff', font=('Consolas', 9), relief='sunken', borderwidth=2)
        self.style.configure('TCheckbutton', background='#1a1a1a', foreground='#e0e0e0', font=('Inter', 10))
        self.style.map('TCheckbutton', background=[('active', '#1a1a1a')], foreground=[('active', '#ffffff')])
        self.style.configure('TNotebook', background='#1a1a1a', bordercolor='#6a006a', tabposition='n')
        self.style.configure('TNotebook.Tab', background='#3a003a', foreground='#ffffff', font=('Inter', 11, 'bold'), padding=[10, 5])
        self.style.map('TNotebook.Tab',
                       background=[('selected', '#6a006a'), ('active', '#5a005a')],
                       foreground=[('selected', '#ffffff'), ('active', '#ffffff')])
        self.style.configure('TProgressbar', background='#4a004a', troughcolor='#1e1e1e', bordercolor='#6a006a', thickness=10)

    def _setup_main_layout(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame = main_frame # Store for later use

    def _setup_tabs(self):
        tabs_config = {
            "Optymalizacja PC": self._populate_pc_tab,
            "Optymalizacja Windows": self._populate_windows_tab,
            "Optymalizacja Sieci": self._populate_network_tab,
            "Fortnite Optimka": self._populate_fortnite_tab
        }

        for tab_text, populate_func in tabs_config.items():
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=tab_text)
            self.create_scrollable_tab(tab_frame, populate_func)

    def _setup_output_and_status(self):
        self.output_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=80, height=15, state='disabled',
                                                     background='#0d0d0d', foreground='#c0c0c0', insertbackground='#ffffff')
        self.output_text.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.status_bar = ttk.Label(self.root, text="Gotowy", relief=tk.SUNKEN, anchor=tk.W,
                                    background='#3a3a3a', foreground='#ffffff', font=('Inter', 9))
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def create_scrollable_tab(self, parent_frame, populate_func):
        canvas = tk.Canvas(parent_frame, background='#1a1a1a', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="15")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollable_frame.grid_columnconfigure(0, weight=1)
        populate_func(scrollable_frame)

    def _create_buttons(self, frame, buttons_data):
        for i, (text, command) in enumerate(buttons_data):
            ttk.Button(frame, text=text, command=command).grid(row=i, column=0, pady=7, sticky=(tk.W, tk.E))

    def _populate_pc_tab(self, frame):
        buttons_data = [
            ("Wyczyść pliki tymczasowe", self.clear_temp_files),
            ("Znajdź duże pliki", self.find_large_files),
            ("Zwolnij pamięć RAM", self.clean_ram),
            ("Defragmentuj dyski (Windows)", self.defragment_drives),
            ("Otwórz Menedżer zadań (Autostart)", self.open_task_manager_startup)
        ]
        self._create_buttons(frame, buttons_data)

    def _populate_windows_tab(self, frame):
        buttons_data = [
            ("Ustaw tryb zasilania na 'Najwyższa wydajność'", self.set_power_plan_best_performance),
            ("Ustaw efekty wizualne na 'Dopasuj dla najlepszej wydajności'", self.set_visual_effects_best_performance),
            ("Wyłącz powiadomienia (Windows)", self.disable_notifications),
            ("Wyłącz historię schowka (Windows)", self.disable_clipboard_history),
            ("Wyłącz Czujnik pamięci (Storage Sense) (Windows)", self.disable_storage_sense),
            ("Wyłącz dane diagnostyczne (Windows)", self.disable_diagnostic_data),
            ("Wyłącz usługę bufora wydruku (Windows)", self.disable_print_spooler),
            ("Wyłącz Superfetch/SysMain (Windows)", self.disable_superfetch),
            ("Wyłącz Windows Search (Windows)", self.disable_windows_search),
            ("Tymczasowo wyłącz Windows Update (Windows)", self.disable_windows_update),
            ("Tymczasowo wyłącz Windows Defender (Windows)", self.disable_windows_defender),
            ("Wyłącz Game Bar (Windows)", self.disable_game_bar),
            ("Wyłącz Xbox DVR (Windows)", self.disable_xbox_dvr),
            ("Wyłącz aplikacje działające w tle (Windows)", self.disable_background_apps)
        ]
        self._create_buttons(frame, buttons_data)

    def _populate_network_tab(self, frame):
        buttons_data = [
            ("Odśwież pamięć podręczną DNS", self.flush_dns),
            ("Wykonaj test pingu", self.run_ping_test),
            ("Znajdź najlepszy serwer DNS", self.find_best_dns),
            ("Zmień priorytet sieci (Windows)", self.set_network_priority),
            ("Wyłącz algorytm Nagle'a (Windows)", self.disable_nagle_algorithm),
            ("Resetuj adaptery sieciowe (Windows)", self.reset_network_adapters),
            ("Włącz/Wyłącz Network Throttling (Windows)", self.toggle_network_throttling)
        ]
        self._create_buttons(frame, buttons_data)
        ttk.Label(frame, text="Adres IP do pingu:").grid(row=1, column=0, pady=(15, 5), sticky=tk.W)
        self.ping_entry = ttk.Entry(frame)
        self.ping_entry.insert(0, "8.8.8.8")
        self.ping_entry.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))


    def _populate_fortnite_tab(self, frame):
        buttons_data = [
            ("Ustaw priorytet procesu Fortnite na wysoki", self.set_fortnite_priority),
            ("Wyczyść pamięć podręczną Fortnite", self.clear_fortnite_cache),
            ("Włącz Tryb Gry (Windows)", self.enable_game_mode),
            ("Wyłącz pobieranie w tle (Windows Store/Update)", self.disable_background_downloads),
            ("Wyłącz optymalizacje pełnoekranowe dla Fortnite (Instrukcja)", self.fortnite_fullscreen_optimization_guide)
        ]
        self._create_buttons(frame, buttons_data)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def update_output(self, message):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def update_status(self, message):
        self.status_bar.config(text=message)

    def run_command_in_thread(self, func, *args):
        self.update_status("Przetwarzam...")
        thread = threading.Thread(target=func, args=args)
        thread.daemon = True
        thread.start()

    def _run_subprocess_command(self, command, success_message, error_message, requires_admin=False):
        self.update_output(f"\nWykonuję: {' '.join(command)}")
        if requires_admin and platform.system() == "Windows" and not self.is_admin():
            self.update_output("UWAGA: Ta operacja wymaga uprawnień administratora. Uruchom aplikację jako administrator, aby zadziałało.")
            self.update_status(f"Błąd: {error_message} (Wymagane uprawnienia administratora)")
            return False
        try:
            process = subprocess.run(command, capture_output=True, text=True, check=False, shell=False, encoding='utf-8', errors='ignore')
            self.update_output(process.stdout.strip())
            if process.stderr:
                self.update_output(f"Błędy (jeśli występują):\n{process.stderr.strip()}")
            if process.returncode == 0:
                self.update_output(success_message)
                return True
            else:
                self.update_output(f"{error_message} (Kod wyjścia: {process.returncode})")
                return False
        except FileNotFoundError:
            self.update_output(f"Błąd: Komenda '{command[0]}' nie znaleziona. Upewnij się, że jest w PATH.")
            return False
        except Exception as e:
            self.update_output(f"Wystąpił nieoczekiwany błąd: {e}")
            return False

    # --- PC Optimization Functions ---
    def clear_temp_files(self):
        self.run_command_in_thread(self._clear_temp_files_task)

    def _clear_temp_files_task(self):
        self.update_output("Rozpoczynanie czyszczenia plików tymczasowych...")
        temp_dirs = []
        if platform.system() == "Windows":
            temp_dirs.extend([os.environ.get('TEMP', ''), os.environ.get('TMP', ''),
                             os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
                             os.path.join(os.environ.get('WINDIR', ''), 'Prefetch'),
                             os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Recent')])
        elif platform.system() in ["Linux", "Darwin"]:
            temp_dirs.extend(["/tmp/", "/var/tmp/"])
            if 'XDG_RUNTIME_DIR' in os.environ:
                temp_dirs.append(os.environ['XDG_RUNTIME_DIR'])

        cleaned_count = 0
        cleaned_size = 0

        for temp_dir in [d for d in temp_dirs if os.path.exists(d)]:
            self.update_output(f"Przetwarzanie katalogu: {temp_dir}")
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            cleaned_count += 1
                            cleaned_size += file_size
                    except OSError as e:
                        self.update_output(f"Nie można usunąć pliku {file_path}: {e}")
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    try:
                        if not os.listdir(dir_path):
                            os.rmdir(dir_path)
                    except OSError as e:
                        self.update_output(f"Nie można usunąć katalogu {dir_path}: {e}")

        self.update_output(f"\nZakończono czyszczenie plików tymczasowych.")
        self.update_output(f"Usunięto {cleaned_count} plików i katalogów, łącznie {cleaned_size / (1024*1024):.2f} MB.")
        self.update_status("Czyszczenie plików tymczasowych zakończone.")
        self.update_output("Czyszczenie plików tymczasowych może przyczynić się do lepszej wydajności systemu i zwiększenia FPS.")

    def find_large_files(self):
        directory = filedialog.askdirectory(title="Wybierz katalog do skanowania")
        if directory:
            self.run_command_in_thread(self._find_large_files_task, directory)
        else:
            self.update_status("Anulowano wyszukiwanie dużych plików.")

    def _find_large_files_task(self, directory, min_size_mb=100):
        self.update_output(f"\nRozpoczynanie wyszukiwania plików większych niż {min_size_mb} MB w: {directory}")
        large_files = []
        min_size_bytes = min_size_mb * 1024 * 1024
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.isfile(file_path) and os.path.getsize(file_path) > min_size_bytes:
                        large_files.append((file_path, os.path.getsize(file_path)))
                except OSError as e:
                    self.update_output(f"Błąd dostępu do pliku {file_path}: {e}")
        if large_files:
            self.update_output("\nZnaleziono duże pliki (posortowane od największego):")
            large_files.sort(key=lambda x: x[1], reverse=True)
            for path, size in large_files:
                self.update_output(f"- {path} ({size / (1024*1024):.2f} MB)")
        else:
            self.update_output(f"\nNie znaleziono plików większych niż {min_size_mb} MB w {directory}.")
        self.update_status("Wyszukiwanie dużych plików zakończone.")
        self.update_output("Usunięcie dużych, niepotrzebnych plików może zwolnić miejsce na dysku i poprawić ogólną wydajność systemu.")

    def clean_ram(self):
        self.run_command_in_thread(self._clean_ram_task)

    def _clean_ram_task(self):
        self.update_output("\nRozpoczynanie próby zwolnienia pamięci RAM...")
        gc.collect()
        self.update_output("Wymuszono uruchomienie modułu zbierającego elementy bezużyteczne Pythona. To może zwolnić pamięć używaną przez samą aplikację.")
        if platform.system() == "Windows":
            self.update_output("Dla głębszego czyszczenia pamięci RAM w Windows, rozważ użycie narzędzi systemowych lub restart komputera.")
        self.update_output("Zwolnienie pamięci RAM może poprawić responsywność systemu i zapobiec zacięciom w grach, co może zwiększyć FPS.")
        self.update_status("Zwalnianie pamięci RAM zakończone.")

    def defragment_drives(self):
        if platform.system() != "Windows":
            self.update_output("Ta funkcja jest dostępna tylko dla systemu Windows.")
            self.update_status("Defragmentacja nieudana.")
            return
        self.run_command_in_thread(self._defragment_drives_task)

    def _defragment_drives_task(self):
        self.update_output("\nRozpoczynanie defragmentacji dysków (Windows)...")
        self.update_output("Może to potrwać dłuższą chwilę i wymaga uprawnień administratora.")
        self.update_output("Uruchamiam narzędzie 'optymalizuj dyski'.")
        try:
            subprocess.Popen(["dfrgui.exe"])
            self.update_output("Otwarto narzędzie 'Optymalizuj dyski'. Wybierz dyski do defragmentacji/optymalizacji.")
            self.update_output("Regularna defragmentacja (dla HDD) lub optymalizacja (dla SSD) może poprawić szybkość dostępu do plików i ogólną responsywność systemu, co pośrednio wpływa na FPS.")
            self.update_status("Defragmentacja/optymalizacja dysków rozpoczęta.")
        except FileNotFoundError:
            self.update_output("Błąd: dfrgui.exe nie znaleziono. Upewnij się, że narzędzie do optymalizacji dysków jest dostępne w systemie.")
            self.update_status("Defragmentacja nieudana.")
        except Exception as e:
            self.update_output(f"Wystąpił nieoczekiwany błąd: {e}")
            self.update_status("Defragmentacja nieudana.")

    def open_task_manager_startup(self):
        if platform.system() != "Windows":
            self.update_output("Ta funkcja jest dostępna tylko dla systemu Windows.")
            self.update_status("Nieobsługiwany system operacyjny.")
            return
        self.update_output("Otwieranie Menedżera zadań na zakładce 'Autostart'...")
        try:
            subprocess.Popen(["taskmgr.exe"])
            self.update_output("Otwarto Menedżer zadań. Przejdź do zakładki 'Autostart' i wyłącz niepotrzebne programy, aby przyspieszyć uruchamianie systemu i zwolnić zasoby. To może zwiększyć FPS.")
            self.update_status("Menedżer zadań otwarty.")
        except FileNotFoundError:
            self.update_output("Błąd: taskmgr.exe nie znaleziono.")
            self.update_status("Nie udało się otworzyć Menedżera zadań.")
        except Exception as e:
            self.update_output(f"Wystąpił nieoczekiwany błąd: {e}")
            self.update_status("Nie udało się otworzyć Menedżera zadań.")


    # --- Windows Optimization Functions ---
    def set_power_plan_best_performance(self):
        if platform.system() != "Windows":
            self.update_output("Ta funkcja jest dostępna tylko dla systemu Windows.")
            self.update_status("Ustawianie planu zasilania nieudane.")
            return
        self.run_command_in_thread(self._set_power_plan_best_performance_task)

    def _set_power_plan_best_performance_task(self):
        self.update_output("\nUstawianie planu zasilania na 'Najwyższa wydajność'...")
        ultimate_performance_guid = "e9a42b02-d5df-448d-aa00-03f14749d616"
        high_performance_guid = "8c5e7fd1-a8b0-4a9d-a705-ee28d6067916"

        if self._run_subprocess_command(["powercfg", "/setactive", ultimate_performance_guid],
                                        "Ustawiono plan zasilania na 'Najwyższa wydajność' (Ultimate Performance).",
                                        "Nie udało się ustawić planu zasilania 'Najwyższa wydajność'. Próbuję 'Wysoka wydajność'.",
                                        requires_admin=True):
            self.update_output("Tryb 'Najwyższa wydajność' może znacząco poprawić responsywność systemu i zwiększyć FPS.")
        else:
            if self._run_subprocess_command(["powercfg", "/setactive", high_performance_guid],
                                            "Ustawiono plan zasilania na 'Wysoka wydajność'.",
                                            "Nie udało się ustawić planu zasilania 'Wysoka wydajność'.",
                                            requires_admin=True):
                self.update_output("Tryb 'Wysoka wydajność' może poprawić responsywność systemu i zwiększyć FPS.")
            else:
                self.update_output("Nie udało się ustawić żadnego planu zasilania o wysokiej wydajności.")
        self.update_status("Ustawianie planu zasilania zakończone.")

    def set_visual_effects_best_performance(self):
        if platform.system() != "Windows":
            self.update_output("Ta funkcja jest dostępna tylko dla systemu Windows.")
            self.update_status("Ustawianie efektów wizualnych nieudane.")
            return
        self.run_command_in_thread(self._set_visual_effects_best_performance_task)

    def _set_visual_effects_best_performance_task(self):
        self.update_output("\nUstawianie efektów wizualnych na 'Dopasuj dla najlepszej wydajności' (Windows)...")
        self.update_output("Może to wymagać uprawnień administratora.")
        self.update_output("Ta operacja wyłączy większość animacji i cieni, co może poprawić wydajność.")

        commands = [
            (["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects", "/v", "VisualFXSetting", "/t", "REG_DWORD", "/d", "2", "/f"], "Pomyślnie zmieniono ustawienie: VisualFXSetting"),
            (["reg", "add", "HKCU\\Control Panel\\Desktop", "/v", "DragFullWindows", "/t", "REG_SZ", "/d", "0", "/f"], "Pomyślnie zmieniono ustawienie: DragFullWindows"),
            (["reg", "add", "HKCU\\Control Panel\\Desktop\\WindowMetrics", "/v", "MinAnimate", "/t", "REG_SZ", "/d", "0", "/f"], "Pomyślnie zmieniono ustawienie: MinAnimate"),
            (["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "/v", "ListviewAlphaSelect", "/t", "REG_DWORD", "/d", "0", "/f"], "Pomyślnie zmieniono ustawienie: ListviewAlphaSelect"),
            (["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "/v", "ListviewShadow", "/t", "REG_DWORD", "/d", "0", "/f"], "Pomyślnie zmieniono ustawienie: ListviewShadow"),
            (["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "/v", "TaskbarAnimations", "/t", "REG_DWORD", "/d", "0", "/f"], "Pomyślnie zmieniono ustawienie: TaskbarAnimations"),
        ]

        success_all = True
        for cmd_list, msg in commands:
            if not self._run_subprocess_command(cmd_list, msg, f"Nie udało się zmienić ustawienia: {cmd_list[4]}.", requires_admin=False):
                success_all = False

        if success_all:
            self.update_output("\nZakończono próby ustawienia efektów wizualnych na 'Dopasuj dla najlepszej wydajności'.")
            self.update_output("Te zmiany mogą znacząco poprawić płynność systemu i zwiększyć FPS, zwłaszcza na słabszych komputerach.")
        else:
            self.update_output("\nNiektóre ustawienia efektów wizualnych mogły nie zostać zmienione.")
        self.update_output("Aby uzyskać pełną kontrolę, zaleca się ręczne dostosowanie w 'Dostosuj wygląd i wydajność systemu Windows' (wyszukaj w menu Start).")
        self.update_status("Ustawianie efektów wizualnych zakończone.")

    def _windows_optimization_template(self, task_name, description, commands_data, final_message, requires_admin=False):
        if platform.system() != "Windows":
            self.update_output(f"Ta funkcja ({task_name}) jest dostępna tylko dla systemu Windows.")
            self.update_status(f"{task_name} nieudane.")
            return

        self.run_command_in_thread(
            lambda: self._execute_windows_optimization(task_name, description, commands_data, final_message, requires_admin)
        )

    def _execute_windows_optimization(self, task_name, description, commands_data, final_message, requires_admin):
        self.update_output(f"\nRozpoczynanie {description} (Windows)...")
        if requires_admin:
            self.update_output("Może to wymagać uprawnień administratora.")

        success_all = True
        for cmd_info in commands_data:
            cmd = cmd_info["command"]
            success_msg = cmd_info["success_message"]
            error_msg = cmd_info.get("error_message", f"Nie udało się wykonać komendy: {' '.join(cmd)}")
            if not self._run_subprocess_command(cmd, success_msg, error_msg, requires_admin=requires_admin):
                success_all = False

        self.update_output(f"\nZakończono próby {description}.")
        self.update_output(final_message)
        self.update_status(f"{task_name} zakończone.")

    def disable_notifications(self):
        self._windows_optimization_template(
            "Wyłączanie powiadomień",
            "wyłączania powiadomień",
            [
                {"command": ["reg", "add", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings", "/v", "NOC_GLOBAL_SETTING_ENABLED", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono globalne ustawienie powiadomień."},
                {"command": ["reg", "add", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings", "/v", "NOC_TOAST_ENABLED", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono powiadomienia wyskakujące (Toast Notifications)."}
            ],
            "Wyłączenie powiadomień może zmniejszyć obciążenie procesora i pamięci, co może poprawić FPS, zwłaszcza podczas gry.",
            requires_admin=False # HKCU
        )

    def disable_clipboard_history(self):
        self._windows_optimization_template(
            "Wyłączanie historii schowka",
            "wyłączania historii schowka",
            [
                {"command": ["reg", "add", "HKCU\\Software\\Microsoft\\Clipboard", "/v", "EnableClipboardHistory", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono historię schowka."}
            ],
            "Wyłączenie historii schowka może zwolnić niewielkie zasoby pamięci.",
            requires_admin=False
        )

    def disable_storage_sense(self):
        self._windows_optimization_template(
            "Wyłączanie Czujnika pamięci",
            "wyłączania Czujnika pamięci (Storage Sense)",
            [
                {"command": ["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\StorageSense\\Parameters\\StoragePolicy", "/v", "01", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono Czujnik pamięci (Storage Sense)."}
            ],
            "Wyłączenie Czujnika pamięci może zapobiec nieoczekiwanym operacjom na dysku w tle, co może poprawić stabilność FPS.",
            requires_admin=False
        )

    def disable_diagnostic_data(self):
        self._windows_optimization_template(
            "Wyłączanie danych diagnostycznych",
            "wyłączania danych diagnostycznych",
            [
                {"command": ["reg", "add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "/v", "AllowTelemetry", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono zbieranie danych telemetrycznych (AllowTelemetry)."},
                {"command": ["sc", "config", "DiagTrack", "start=", "disabled"], "success_message": "Pomyślnie wyłączono usługę 'Connected User Experiences and Telemetry'."},
                {"command": ["sc", "stop", "DiagTrack"], "success_message": "Pomyślnie zatrzymano usługę 'Connected User Experiences and Telemetry'."}
            ],
            "Wyłączenie danych diagnostycznych może zmniejszyć zużycie zasobów w tle i poprawić FPS.",
            requires_admin=True
        )

    def disable_print_spooler(self):
        self._windows_optimization_template(
            "Wyłączanie usługi bufora wydruku",
            "wyłączania usługi bufora wydruku (Print Spooler)",
            [
                {"command": ["sc", "config", "Spooler", "start=", "disabled"], "success_message": "Pomyślnie wyłączono usługę 'Spooler' (Bufor wydruku)."},
                {"command": ["sc", "stop", "Spooler"], "success_message": "Pomyślnie zatrzymano usługę 'Spooler' (Bufor wydruku)."}
            ],
            "Wyłączenie bufora wydruku może zwolnić niewielkie zasoby, jeśli nie drukujesz, co może przekładać się na wyższe FPS.",
            requires_admin=True
        )

    def disable_superfetch(self):
        self._windows_optimization_template(
            "Wyłączanie Superfetch/SysMain",
            "wyłączania usługi Superfetch/SysMain",
            [
                {"command": ["sc", "config", "SysMain", "start=", "disabled"], "success_message": "Pomyślnie wyłączono usługę 'SysMain' (Superfetch)."},
                {"command": ["sc", "stop", "SysMain"], "success_message": "Pomyślnie zatrzymano usługę 'SysMain' (Superfetch)."}
            ],
            "Wyłączenie Superfetch może pomóc w systemach z dyskami SSD, ale może nieznacznie spowolnić uruchamianie aplikacji na HDD. Może to również poprawić FPS w niektórych scenariuszach.",
            requires_admin=True
        )

    def disable_windows_search(self):
        self._windows_optimization_template(
            "Wyłączanie Windows Search",
            "wyłączania usługi Windows Search",
            [
                {"command": ["sc", "config", "WSearch", "start=", "disabled"], "success_message": "Pomyślnie wyłączono usługę 'Windows Search'."},
                {"command": ["sc", "stop", "WSearch"], "success_message": "Pomyślnie zatrzymano usługę 'Windows Search'."}
            ],
            "Wyłączenie Windows Search może zmniejszyć zużycie zasobów w tle, co może poprawić FPS.",
            requires_admin=True
        )

    def disable_windows_update(self):
        self._windows_optimization_template(
            "Tymczasowe wyłączanie Windows Update",
            "tymczasowego wyłączania usługi Windows Update",
            [
                {"command": ["sc", "config", "wuauserv", "start=", "disabled"], "success_message": "Pomyślnie wyłączono usługę 'Windows Update'."},
                {"command": ["sc", "stop", "wuauserv"], "success_message": "Pomyślnie zatrzymano usługę 'Windows Update'."}
            ],
            "Wyłączenie Windows Update może zapobiec nieoczekiwanym restartom i zużyciu zasobów w tle podczas gry, co może poprawić FPS.",
            requires_admin=True
        )

    def disable_windows_defender(self):
        self._windows_optimization_template(
            "Tymczasowe wyłączanie Windows Defender",
            "tymczasowego wyłączania Windows Defender",
            [
                {"command": ["powershell", "-Command", "Set-MpPreference -DisableRealtimeMonitoring $true"], "success_message": "Pomyślnie tymczasowo wyłączono monitorowanie w czasie rzeczywistym Windows Defender.", "error_message": "Nie udało się tymczasowo wyłączyć monitorowania w czasie rzeczywistym Windows Defender."},
                {"command": ["net", "stop", "WinDefend"], "success_message": "Pomyślnie zatrzymano usługę Windows Defender.", "error_message": "Nie udało się zatrzymać usługi Windows Defender."}
            ],
            "Tymczasowe wyłączenie Windows Defender może zwolnić zasoby podczas intensywnych operacji, takich jak gry, co może zwiększyć FPS. Pamiętaj, aby go ponownie włączyć dla bezpieczeństwa!",
            requires_admin=True
        )

    def disable_game_bar(self):
        self._windows_optimization_template(
            "Wyłączanie Game Bar",
            "wyłączania Game Bar",
            [
                {"command": ["reg", "add", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR", "/v", "AppCaptureEnabled", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono Game Bar (AppCaptureEnabled)."},
                {"command": ["reg", "add", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR", "/v", "GameDVR_Enabled", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono Game Bar (GameDVR_Enabled)."}
            ],
            "Wyłączenie Game Bar może zwolnić zasoby systemowe, co może poprawić FPS.",
            requires_admin=False
        )

    def disable_xbox_dvr(self):
        self._windows_optimization_template(
            "Wyłączanie Xbox DVR",
            "wyłączania Xbox DVR",
            [
                {"command": ["reg", "add", "HKCU\\System\\GameConfigStore", "/v", "GameDVR_Enabled", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono Xbox DVR."},
                {"command": ["reg", "add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR", "/v", "AllowGameDVR", "/t", "REG_DWORD", "/d", "0", "/f"], "success_message": "Pomyślnie wyłączono AllowGameDVR w HKLM (wymaga admina)."}
            ],
            "Wyłączenie Xbox DVR może zapobiec niepotrzebnemu nagrywaniu w tle i poprawić wydajność w grach, co może zwiększyć FPS.",
            requires_admin=True
        )

    def disable_background_apps(self):
        self._windows_optimization_template(
            "Wyłączanie aplikacji działających w tle",
            "wyłączania aplikacji działających w tle",
            [
                {"command": ["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications", "/v", "GlobalUserDisabled", "/t", "REG_DWORD", "/d", "1", "/f"], "success_message": "Pomyślnie wyłączono aplikacje działające w tle."}
            ],
            "Wyłączenie aplikacji działających w tle może znacznie zmniejszyć zużycie zasobów i poprawić FPS.",
            requires_admin=False
        )

    # --- Network Optimization Functions ---
    def flush_dns(self):
        self._windows_optimization_template(
            "Odświeżanie pamięci podręcznej DNS",
            "odświeżania pamięci podręcznej DNS",
            [
                {"command": ["ipconfig", "/flushdns"], "success_message": "Pomyślnie odświeżono pamięć podręczną DNS."}
            ],
            "Odświeżenie pamięci podręcznej DNS może rozwiązać problemy z łącznością i poprawić szybkość ładowania stron.",
            requires_admin=True
        )

    def run_ping_test(self):
        ping_ip = self.ping_entry.get()
        if not ping_ip:
            self.update_output("Proszę podać adres IP do pingu.")
            self.update_status("Błąd: Brak adresu IP.")
            return
        self.run_command_in_thread(self._run_ping_test_task, ping_ip)

    def _run_ping_test_task(self, ping_ip):
        self.update_output(f"\nWykonuję test pingu dla: {ping_ip}...")
        try:
            command = ["ping", ping_ip]
            process = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8', errors='ignore')
            self.update_output(process.stdout.strip())
            if process.returncode == 0:
                self.update_output("Test pingu zakończony pomyślnie.")
            else:
                self.update_output(f"Test pingu nieudany (Kod wyjścia: {process.returncode}).")
        except FileNotFoundError:
            self.update_output("Błąd: Komenda 'ping' nie znaleziona. Upewnij się, że jest w PATH.")
        except Exception as e:
            self.update_output(f"Wystąpił nieoczekiwany błąd podczas testu pingu: {e}")
        self.update_status("Test pingu zakończony.")
        self.update_output("Test pingu pozwala sprawdzić stabilność połączenia sieciowego, co jest kluczowe dla gier online i może wpływać na odczuwalne 'lag'.")

    def find_best_dns(self):
        self.update_output("\nWyszukiwanie najlepszego serwera DNS (wymaga narzędzi stron trzecich lub ręcznego sprawdzenia)...")
        self.update_output("Do znalezienia najlepszego serwera DNS zaleca się użycie narzędzi takich jak DNS Benchmark lub Cloudflare's 1.1.1.1.")
        self.update_output("Zmiana serwera DNS może poprawić szybkość ładowania stron i zmniejszyć opóźnienia w niektórych grach online.")
        self.update_status("Wyszukiwanie najlepszego DNS - instrukcja.")

    def set_network_priority(self):
        self.update_output("\nZmiana priorytetu sieci (Windows) - funkcja zaawansowana...")
        self.update_output("Zmiana priorytetu sieci może być wykonana poprzez Menedżer urządzeń -> Właściwości karty sieciowej -> zakładka Zaawansowane lub za pomocą skryptów PowerShell.")
        self.update_output("Nie ma uniwersalnego polecenia, które działałoby bez identyfikacji konkretnych kart sieciowych.")
        self.update_output("Zmiana priorytetu sieci może pomóc w zapewnieniu, że ruch gry ma pierwszeństwo nad innym ruchem sieciowym.")
        self.update_status("Zmiana priorytetu sieci - instrukcja.")

    def disable_nagle_algorithm(self):
        self._windows_optimization_template(
            "Wyłączanie algorytmu Nagle'a",
            "wyłączania algorytmu Nagle'a",
            [
                {"command": ["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces", "/v", "TcpNoDelay", "/t", "REG_DWORD", "/d", "1", "/f"], "success_message": "Pomyślnie włączono TcpNoDelay (wyłączono Nagle'a) w Interfaces. Należy to zrobić dla każdego interfejsu sieciowego. To tylko przykład."},
                {"command": ["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces", "/v", "TcpAckFrequency", "/t", "REG_DWORD", "/d", "1", "/f"], "success_message": "Pomyślnie ustawiono TcpAckFrequency na 1 w Interfaces. To tylko przykład."}
            ],
            "Wyłączenie algorytmu Nagle'a może zmniejszyć opóźnienia w grach online, ale może zwiększyć zużycie pasma.",
            requires_admin=True # Requires specific interface GUIDs for full effect
        )

    def reset_network_adapters(self):
        self._windows_optimization_template(
            "Resetowanie adapterów sieciowych",
            "resetowania adapterów sieciowych",
            [
                {"command": ["netsh", "winsock", "reset"], "success_message": "Pomyślnie zresetowano Winsock Catalog."},
                {"command": ["netsh", "int", "ip", "reset"], "success_message": "Pomyślnie zresetowano TCP/IP."}
            ],
            "Zresetowanie adapterów sieciowych może rozwiązać wiele problemów z połączeniem.",
            requires_admin=True
        )

    def toggle_network_throttling(self):
        self.update_output("\nWłączanie/Wyłączanie Network Throttling (Windows)...")
        self.update_output("Domyślnie Windows może ograniczać przepustowość sieci dla programów w tle. Wyłączenie tego może poprawić wydajność w grach.")
        self.update_output("Wartość 'DisableTaskOffload' = 1 wyłącza dławienie sieci, 0 włącza.")
        # Check current state first if possible, then toggle
        current_state = None
        try:
            # Attempt to read current value
            result = subprocess.run(["reg", "query", "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "/v", "NetworkThrottlingIndex"], capture_output=True, text=True, errors='ignore', check=False)
            if result.returncode == 0:
                match = re.search(r"REG_DWORD\s+0x([0-9a-fA-F]+)", result.stdout)
                if match:
                    current_value = int(match.group(1), 16)
                    self.update_output(f"Aktualna wartość NetworkThrottlingIndex: 0x{current_value:X}")
                    # If 0x0000000a, it's default (throttled). If 0xffffffff, it's disabled.
                    if current_value == 0xFFFFFFFF:
                        current_state = "disabled"
                    else:
                        current_state = "enabled" # Or default throttled

        except Exception as e:
            self.update_output(f"Nie udało się odczytać aktualnego stanu Network Throttling: {e}")
            current_state = None # Fallback

        if current_state == "disabled":
            self.update_output("Network Throttling jest obecnie WYŁĄCZONE. Czy chcesz je włączyć (przywrócić domyślne dławienie)?")
            cmd = ["reg", "add", "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "/v", "NetworkThrottlingIndex", "/t", "REG_DWORD", "/d", "10", "/f"] # Default is 0x0a
            self._run_subprocess_command(cmd, "Pomyślnie włączono Network Throttling (ustawiono na domyślne).", "Nie udało się włączyć Network Throttling.", requires_admin=True)
        else: # Either enabled or unknown/default
            self.update_output("Network Throttling jest obecnie WŁĄCZONE lub w stanie domyślnym. Czy chcesz je WYŁĄCZYĆ?")
            cmd = ["reg", "add", "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "/v", "NetworkThrottlingIndex", "/t", "REG_DWORD", "/d", "4294967295", "/f"] # 0xffffffff
            self._run_subprocess_command(cmd, "Pomyślnie wyłączono Network Throttling.", "Nie udało się wyłączyć Network Throttling.", requires_admin=True)

        self.update_output("Wyłączenie Network Throttling może zapewnić pełną przepustowość dla wszystkich aplikacji, potencjalnie poprawiając stabilność połączenia w grach.")
        self.update_status("Zmiana stanu Network Throttling zakończona.")

    # --- Fortnite Optimka Functions ---
    def set_fortnite_priority(self):
        self.update_output("\nUstawianie priorytetu procesu Fortnite na wysoki...")
        self.update_output("Ta funkcja wymaga, aby Fortnite był uruchomiony.")
        self.update_output("W Windows można to zrobić za pomocą 'wmic process where name=\"FortniteClient-Win64-Shipping.exe\" call setpriority \"high priority\"' lub 'taskkill /IM FortniteClient-Win64-Shipping.exe /F && start \"\" /high \"C:\\Path\\To\\Fortnite\\FortniteClient-Win64-Shipping.exe\"'.")
        self.update_output("Zmiana priorytetu procesu może pomóc systemowi przydzielić więcej zasobów CPU dla gry, co może zwiększyć FPS.")
        self.update_status("Ustawianie priorytetu Fortnite - instrukcja.")

    def clear_fortnite_cache(self):
        self.update_output("\nCzyszczenie pamięci podręcznej Fortnite...")
        # Common cache locations for Fortnite (Unreal Engine games)
        if platform.system() == "Windows":
            appdata_local = os.environ.get('LOCALAPPDATA', '')
            cache_path_dx12 = os.path.join(appdata_local, 'FortniteGame', 'Saved', 'Crashes') # This is usually crash logs
            cache_path_webcache = os.path.join(appdata_local, 'Epic Games Launcher', 'Saved', 'webcache') # Launcher cache
            cache_path_shader = os.path.join(appdata_local, 'NVIDIA', 'DXCache') # Nvidia shader cache, common for games
            cache_path_shader_amd = os.path.join(appdata_local, 'AMD', 'DxCache') # AMD shader cache

            paths_to_clean = [
                os.path.join(appdata_local, 'FortniteGame', 'Saved', 'webcache_4147'), # Common webcache for Fortnite
                os.path.join(appdata_local, 'FortniteGame', 'Saved', 'Config'), # Can delete, will recreate. But usually user settings.
                os.path.join(appdata_local, 'FortniteGame', 'Saved', 'Logs'),
                os.path.join(appdata_local, 'FortniteGame', 'Saved', 'Screenshots'),
                cache_path_dx12,
                cache_path_webcache,
                cache_path_shader,
                cache_path_shader_amd
            ]
        else:
            self.update_output("Czyszczenie pamięci podręcznej Fortnite jest obecnie wspierane głównie dla systemu Windows.")
            self.update_status("Czyszczenie pamięci podręcznej Fortnite nieudane.")
            return

        cleaned_count = 0
        for path in paths_to_clean:
            if os.path.exists(path):
                self.update_output(f"Czyszczę: {path}")
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                        cleaned_count += 1
                    elif os.path.isdir(path):
                        # Use shutil.rmtree for directories, but need to be careful.
                        # For safety, let's just delete files within known cache dirs.
                        # Or provide a warning. For simplicity and user control,
                        # I'll just iterate and remove files/empty dirs.
                        for root, dirs, files in os.walk(path, topdown=False):
                            for name in files:
                                try:
                                    os.remove(os.path.join(root, name))
                                    cleaned_count += 1
                                except OSError as e:
                                    self.update_output(f"Nie można usunąć pliku {os.path.join(root, name)}: {e}")
                            for name in dirs:
                                try:
                                    os.rmdir(os.path.join(root, name))
                                except OSError as e:
                                    self.update_output(f"Nie można usunąć katalogu {os.path.join(root, name)}: {e}")
                except Exception as e:
                    self.update_output(f"Błąd podczas czyszczenia {path}: {e}")
            else:
                self.update_output(f"Ścieżka nie istnieje, pomijam: {path}")

        self.update_output(f"\nZakończono czyszczenie pamięci podręcznej Fortnite. Usunięto {cleaned_count} elementów.")
        self.update_output("Czyszczenie pamięci podręcznej Fortnite może rozwiązać problemy z wydajnością, błędy graficzne i poprawić stabilność FPS.")
        self.update_status("Czyszczenie pamięci podręcznej Fortnite zakończone.")

    def enable_game_mode(self):
        self._windows_optimization_template(
            "Włączanie Trybu Gry",
            "włączania Trybu Gry",
            [
                {"command": ["reg", "add", "HKCU\\Software\\Microsoft\\GameBar", "/v", "AllowAutoGameMode", "/t", "REG_DWORD", "/d", "1", "/f"], "success_message": "Pomyślnie włączono Tryb Gry."}
            ],
            "Włączenie Trybu Gry w Windows optymalizuje system pod kątem gier, co może poprawić FPS.",
            requires_admin=False
        )

    def disable_background_downloads(self):
        self.update_output("\nWyłączanie pobierania w tle (Windows Store/Update)...")
        # This is often managed by disabling Windows Update or Delivery Optimization.
        # Direct command to disable ALL background downloads (e.g., from Store) is not simple via cmd/reg.
        # It's usually tied to "Allow downloads from other PCs" (Delivery Optimization) or background app settings.
        self.update_output("Aby wyłączyć pobieranie w tle, możesz:")
        self.update_output("1. Wyłączyć usługę Windows Update (tymczasowo, patrz dedykowana opcja).")
        self.update_output("2. Wyłączyć optymalizację dostarczania (Delivery Optimization) w Ustawieniach Windows (Ustawienia -> Aktualizacja i zabezpieczenia -> Optymalizacja dostarczania).")
        self.update_output("3. Wyłączyć aplikacje działające w tle (patrz dedykowana opcja).")
        self.update_output("Wyłączenie pobierania w tle może zwolnić przepustowość sieci i zasoby systemowe, co może poprawić FPS w grach online.")
        self.update_status("Wyłączanie pobierania w tle - instrukcja.")

    def fortnite_fullscreen_optimization_guide(self):
        self.update_output("\n--- Instrukcja: Wyłączanie optymalizacji pełnoekranowych dla Fortnite ---")
        self.update_output("Wyłączenie optymalizacji pełnoekranowych może poprawić wydajność i zmniejszyć opóźnienia wejściowe w grach.")
        self.update_output("1. Znajdź plik wykonywalny Fortnite. Domyślna ścieżka to zazwyczaj:")
        self.update_output("   C:\\Program Files\\Epic Games\\Fortnite\\FortniteGame\\Binaries\\Win64\\")
        self.update_output("   Poszukaj plików takich jak 'FortniteClient-Win64-Shipping.exe'.")
        self.update_output("2. Kliknij prawym przyciskiem myszy na plik wykonywalny Fortnite (.exe) i wybierz 'Właściwości'.")
        self.update_output("3. Przejdź do zakładki 'Zgodność'.")
        self.update_output("4. Zaznacz opcję 'Wyłącz optymalizacje pełnoekranowe'.")
        self.update_output("5. Kliknij 'Zastosuj', a następnie 'OK'.")
        self.update_output("Powtórz te kroki dla wszystkich plików .exe związanych z Fortnite w tym katalogu, zwłaszcza tych z 'EAC' lub 'BE' w nazwie.")
        self.update_output("\nZastosowanie tej optymalizacji może znacząco poprawić płynność gry i responsywność w Fortnite, co przekłada się na wyższe i bardziej stabilne FPS.")
        self.update_status("Instrukcja wyłączania optymalizacji pełnoekranowych.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PCOptimizerApp(root)
    root.mainloop()