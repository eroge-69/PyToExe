import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import time
import threading
import math
import random
import tkinter as tk
import re
import sys
import os
import json
import hashlib

# --- GLOBALNE USTALENIA LOADERA ---
LOADER_VERSION_NAME = "NORMAL"
CURRENT_VERSION_LEVEL = 1 # 1 = Normal, 2 = VIP, 3 = ELITE
# --- KONIEC GLOBALNYCH USTALEŃ LOADERA ---

# --- FUNKCJE OBSŁUGI DANYCH UŻYTKOWNIKA ---
def get_appdata_path():
    """Zwraca ścieżkę do folderu %appdata%/Wycinator."""
    appdata_dir = os.path.join(os.environ['APPDATA'], 'Wycinator')
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir)
    return appdata_dir

def get_users_file_path():
    """Zwraca pełną ścieżkę do pliku users.json."""
    return os.path.join(get_appdata_path(), 'users.json')

def load_users():
    """Wczytuje dane użytkowników z pliku users.json."""
    file_path = get_users_file_path()
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Zwróć pusty słownik, jeśli plik jest pusty/uszkodzony
    return {}

def save_users(users_data):
    """Zapisuje dane użytkowników do pliku users.json."""
    file_path = get_users_file_path()
    with open(file_path, 'w') as f:
        json.dump(users_data, f, indent=4)

def hash_password(password):
    """Haszuje hasło używając SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# --- KLASA LOGOWANIA/REJESTRACJI ---
class LoginRegisterApp(ctk.CTk):
    def __init__(self, launcher_callback):
        super().__init__()
        self.launcher_callback = launcher_callback
        
        self.title("Wycinator - Logowanie / Rejestracja")
        self.geometry("400x350")
        self.resizable(False, False)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.create_widgets()

    def create_widgets(self):
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.frame, text="Logowanie / Rejestracja", font=("Arial", 20, "bold")).pack(pady=10)

        ctk.CTkLabel(self.frame, text="Nazwa użytkownika:").pack(pady=5)
        self.username_entry = ctk.CTkEntry(self.frame, width=250)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.frame, text="Hasło:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.frame, width=250, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self.frame, text="Zaloguj", command=self.login)
        self.login_button.pack(pady=10)

        self.register_button = ctk.CTkButton(self.frame, text="Zarejestruj", command=self.register)
        self.register_button.pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_password = hash_password(password)

        users = load_users()

        if username in users and users[username]['password'] == hashed_password:
            messagebox.showinfo("Sukces", "Zalogowano pomyślnie!")
            self.withdraw() # Ukryj okno logowania
            self.launcher_callback() # Wywołaj callback do uruchomienia launchera
        else:
            messagebox.showerror("Błąd", "Nieprawidłowa nazwa użytkownika lub hasło.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Błąd", "Nazwa użytkownika i hasło nie mogą być puste!")
            return

        users = load_users()

        if username in users:
            messagebox.showerror("Błąd", "Nazwa użytkownika już istnieje.")
        else:
            users[username] = {'password': hash_password(password)}
            save_users(users)
            messagebox.showinfo("Sukces", "Konto zarejestrowane pomyślnie! Możesz się teraz zalogować.")
            # Opcjonalnie: automatyczne logowanie po rejestracji
            # self.username_entry.delete(0, tk.END)
            # self.password_entry.delete(0, tk.END)

# ----------------------------------------------------------------------
#                         KOD WYCINATORA NORMAL
# ----------------------------------------------------------------------

class WycinatorToolNormal(ctk.CTk):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window 
        self.parent_window.withdraw() 

        self.title("Wycinator Tool v1.0 - NORMAL EDITION")
        self.geometry("700x600")
        self.resizable(False, False)

        self.method_var = ctk.StringVar(self)
        self.min_packets_entry_value = 10 
        self.fixed_botnets = 50
        self.min_internet_down_threshold = 1000 
        self.max_internet_down_threshold = 3000
        self.max_pps_limit = 50 

        self.create_main_gui()

    def create_main_gui(self):
        main_frame = ctk.CTkFrame(self, fg_color="#202020")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.control_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B", width=300)
        self.control_frame.pack(side="left", fill="both", padx=(0, 10), pady=0)
        self.control_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(self.control_frame, text="Wycinator Tool - Normal OPS",
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=20)

        ctk.CTkLabel(self.control_frame, text="Wybierz metodę ataku:").pack(pady=5)
        methods = ["SYN Flood", "UDP Flood", "HTTP Flood"]
        self.method_var.set(methods[0])
        self.method_menu = ctk.CTkOptionMenu(self.control_frame, variable=self.method_var, values=methods)
        self.method_menu.pack(pady=5, fill="x", padx=15)

        ctk.CTkLabel(self.control_frame, text="Adres IP celu:").pack(pady=5)
        self.ip_entry = ctk.CTkEntry(self.control_frame, width=250, placeholder_text="np. 192.168.1.1")
        self.ip_entry.pack(pady=5, fill="x", padx=15)

        ctk.CTkLabel(self.control_frame, text=f"Liczba pakietów: {self.min_packets_entry_value}").pack(pady=5)
        self.packets_entry = ctk.CTkEntry(self.control_frame, width=250)
        self.packets_entry.insert(0, str(self.min_packets_entry_value))
        self.packets_entry.pack(pady=5, fill="x", padx=15)
        
        self.start_button = ctk.CTkButton(self.control_frame, text="ROZPOCZNIJ ATAK",
                                         command=self.start_attack_thread,
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         height=50)
        self.start_button.pack(pady=20, padx=15, fill="x")

        self.operation_progress_bar = ctk.CTkProgressBar(self.control_frame, orientation="horizontal",
                                                        width=250, mode="determinate")
        self.operation_progress_bar.pack(pady=10)
        self.operation_progress_bar.set(0)

        console_frame = ctk.CTkFrame(main_frame, fg_color="#1C1C1C")
        console_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=0)

        ctk.CTkLabel(console_frame, text="Konsola Systemowa", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        self.console_output = scrolledtext.ScrolledText(console_frame, wrap="word",
                                                     bg="#000000", fg="#00FF00",
                                                     font=("Consolas", 10),
                                                     insertbackground="#00FF00")
        self.console_output.pack(expand=True, fill="both", padx=10, pady=5)
        self.console_output.config(state="disabled")

        stats_frame = ctk.CTkFrame(console_frame, fg_color="#2B2B2B")
        stats_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.packets_per_sec_label = ctk.CTkLabel(stats_frame, text="Pakiety/s: 0", font=ctk.CTkFont(size=12))
        self.packets_per_sec_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.power_label = ctk.CTkLabel(stats_frame, text="Moc (Mbps): 0.00", font=ctk.CTkFont(size=12))
        self.power_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.botnets_label = ctk.CTkLabel(stats_frame, text=f"Botnety: {self.fixed_botnets}", font=ctk.CTkFont(size=12))
        self.botnets_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        self.status_label = ctk.CTkLabel(self.control_frame, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)

    def is_valid_ip(self, ip_address):
        pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return re.match(pattern, ip_address)

    def update_console(self, message):
        self.console_output.config(state="normal")
        self.console_output.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.console_output.see(tk.END)
        self.console_output.config(state="disabled")

    def run_attack_simulation(self, method, target_ip, total_packets_to_send):
        self.status_label.configure(text=f"Przygotowuję atak: {method} na {target_ip}...")
        self.update_console(f"Inicjowanie ataku {method} na cel: {target_ip}...")
        self.operation_progress_bar.set(0)
        
        sent_packets_in_frame = 0
        current_pps = 0
        current_power = 0.00
        start_time_frame = time.time()
        
        internet_down_trigger = random.randint(self.min_internet_down_threshold, self.max_internet_down_threshold)
        
        effective_packets_target = total_packets_to_send

        if effective_packets_target > internet_down_trigger:
             effective_packets_target_for_progress = internet_down_trigger
        else:
            effective_packets_target_for_progress = effective_packets_target

        internet_down = False

        for i in range(1, total_packets_to_send + 1):
            if internet_down: 
                break

            if i >= internet_down_trigger and not internet_down:
                internet_down = True
                self.update_console(f"!!! CEL {target_ip} ZNACZNIE ZWOLNIŁ LUB ODŁĄCZYŁ SIĘ OD SIECI !!!")
                self.status_label.configure(text=f"CEL {target_ip} OFFLINE! (Atak zakończony)")
                self.operation_progress_bar.set(1.0)
                self.packets_per_sec_label.configure(text="Pakiety/s: 0")
                self.power_label.configure(text="Moc (Mbps): 0.00")
                messagebox.showinfo("Atak zakończony sukcesem!", f"Cel {target_ip} stracił połączenie z internetem po {i} pakietach!")
                break 
            
            if self.max_pps_limit > 0:
                target_delay_per_packet = 1.0 / self.max_pps_limit
                current_delay = target_delay_per_packet + random.uniform(-0.002, 0.005) 
                if current_delay < 0.0001: current_delay = 0.0001 
                time.sleep(current_delay)
            else: 
                 time.sleep(0.01 + random.random() * 0.05)


            sent_packets_in_frame += 1
            
            progress_val = i / effective_packets_target_for_progress
            self.operation_progress_bar.set(progress_val)
            self.status_label.configure(text=f"Wysyłam pakiet {i}/{effective_packets_target_for_progress} ({method}) do {target_ip}...")

            if time.time() - start_time_frame > 0.5: 
                elapsed_frame = time.time() - start_time_frame
                
                current_pps = int(sent_packets_in_frame / elapsed_frame) if elapsed_frame > 0 else 0
                if current_pps > self.max_pps_limit:
                    current_pps = self.max_pps_limit - random.randint(0, 5) 
                    if current_pps < 0: current_pps = 0

                power_ratio = min(1.0, i / internet_down_trigger) 
                max_power_achieved = random.uniform(5.0, 15.0) 
                current_power = 1.0 + (max_power_achieved - 1.0) * power_ratio + random.uniform(-0.5, 0.5)
                if current_power < 0: current_power = 0
                current_power = round(current_power, 2)

                self.packets_per_sec_label.configure(text=f"Pakiety/s: {current_pps}")
                self.power_label.configure(text=f"Moc (Mbps): {current_power:.2f}")
                
                self.update_console(f"[+] {current_pps} pps | {current_power:.2f} Mbps | {self.fixed_botnets} botnets | Packet {i}/{internet_down_trigger}")
                
                start_time_frame = time.time()
                sent_packets_in_frame = 0

            self.update_idletasks()
            

        if not internet_down:
            self.packets_per_sec_label.configure(text="Pakiety/s: 0")
            self.power_label.configure(text="Moc (Mbps): 0.00")
            self.botnets_label.configure(text=f"Botnety: {self.fixed_botnets}")

            self.status_label.configure(text=f"Atak {method} na {target_ip} zakończony. Przetworzono {effective_packets_target_for_progress} pakietów.")
            self.update_console(f"--- Atak zakończony: {method} na {target_ip} ---")
            messagebox.showinfo("Atak zakończony", f"Akcja zakończona sukcesem.\nMetoda: {method}\nCel: {target_ip}\nPakiety: {effective_packets_target_for_progress}\nBotnety: {self.fixed_botnets}")

        self.set_controls_state("normal")
        self.parent_window.deiconify() 
        self.destroy() 

    def start_attack_thread(self):
        method = self.method_var.get()
        target_ip = self.ip_entry.get()
        packets_str = self.packets_entry.get()

        if not self.is_valid_ip(target_ip):
            messagebox.showerror("Błąd", "Wprowadź prawidłowy adres IP (np. 192.168.1.1)!")
            return
        
        if not packets_str.isdigit():
            messagebox.showerror("Błąd", "Wprowadź prawidłową liczbę pakietów!")
            return
        
        packets = int(packets_str)

        if packets < self.min_packets_entry_value:
            messagebox.showerror("Błąd", f"Wprowadź co najmniej {self.min_packets_entry_value} pakietów!")
            return
        
        MAX_PACKETS_ENTRY_LIMIT = 10000 

        if packets > MAX_PACKETS_ENTRY_LIMIT:
            messagebox.showerror("Błąd", f"Nie możesz tyle wysłać! Ta wersja ma limit {MAX_PACKETS_ENTRY_LIMIT} pakietów!")
            return

        self.set_controls_state("disabled")
        self.console_output.config(state="normal")
        self.console_output.delete(1.0, tk.END)
        self.console_output.config(state="disabled")
        
        threading.Thread(target=self.run_attack_simulation, args=(method, target_ip, packets)).start()
    
    def set_controls_state(self, state):
        self.method_menu.configure(state=state)
        self.ip_entry.configure(state=state)
        self.packets_entry.configure(state=state)
        self.start_button.configure(state=state)

# ----------------------------------------------------------------------
#                         KONIEC KODU WYCINATORA NORMAL
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
#                         KOD GŁÓWNEGO LOADERA
# ----------------------------------------------------------------------

class WycinatorLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"Wycinator Launcher - {LOADER_VERSION_NAME} Edition [PREMIUM]") 
        self.geometry("450x450")
        self.resizable(False, False)

        # --- Ustawienia wyglądu loadera ELITE ---
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue") 
        # --- Koniec ustawień wyglądu loadera ELITE ---

        main_frame = ctk.CTkFrame(self, fg_color="#12121F") 
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        title_label = ctk.CTkLabel(main_frame, text=f"Wycinator System ({LOADER_VERSION_NAME})",
                                  font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"), 
                                  text_color="#FFD700") 
        title_label.pack(pady=25)

        ctk.CTkLabel(main_frame, text="Wybierz wersję do uruchomienia:", font=ctk.CTkFont(family="Segoe UI", size=16), text_color="#E0E0E0").pack(pady=10)

        # --- Przyciski wyboru wersji ---
        self.create_version_button(main_frame, "Normal", 1)
        self.create_version_button(main_frame, "VIP", 2)
        self.create_version_button(main_frame, "ELITE", 3)
        # --- Koniec przycisków ---

        self.status_label = ctk.CTkLabel(main_frame, text="",
                                        font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                                        text_color="#00FFFF")
        self.status_label.pack(pady=20)

    def create_version_button(self, parent_frame, version_name, version_level):
        button_text = f"Uruchom Wycinator {version_name}"
        
        # NOTE: Aby odblokować wersje, zmieniamy CURRENT_VERSION_LEVEL w pliku konkretnej wersji.
        # np. dla normal.py zmieniamy LOADER_VERSION_NAME = "NORMAL" i CURRENT_VERSION_LEVEL = 1
        # dla vip.py zmieniamy LOADER_VERSION_NAME = "VIP" i CURRENT_VERSION_LEVEL = 2
        # dla elite.py zmieniamy LOADER_VERSION_NAME = "ELITE" i CURRENT_VERSION_LEVEL = 3

        if version_level <= CURRENT_VERSION_LEVEL:
            btn = ctk.CTkButton(parent_frame, text=button_text,
                                command=lambda: self.launch_wycinator_version(version_name),
                                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                fg_color="#0056B3", hover_color="#004080", corner_radius=12, height=45, border_width=2, border_color="#00FFFF") 
        else:
            btn = ctk.CTkButton(parent_frame, text=f"{button_text} (Zablokowane)",
                                command=lambda: self.show_upgrade_message(version_name),
                                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                fg_color="#3A3A5A", hover_color="#4A4A6A", state="normal", corner_radius=12, height=45, border_width=1, border_color="#555555") 

        btn.pack(pady=7, fill="x", padx=40)

    def show_upgrade_message(self, target_version_name):
        # NOTE: Ten komunikat jest teraz bardziej dynamiczny w zależności od wersji loadera.
        if LOADER_VERSION_NAME == "NORMAL":
            messagebox.showinfo("Wymagana Aktualizacja", 
                                f"To jest wersja NORMAL. Aby użyć Wycinatora {target_version_name}, potrzebujesz wersji VIP lub ELITE.")
        elif LOADER_VERSION_NAME == "VIP":
            messagebox.showinfo("Wymagana Aktualizacja", 
                                f"To jest wersja VIP. Aby użyć Wycinatora {target_version_name}, potrzebujesz wersji ELITE.")
        elif LOADER_VERSION_NAME == "ELITE":
             messagebox.showinfo("Wymagana Aktualizacja", 
                                f"To jest już wersja ELITE. Wycinator {target_version_name} jest już odblokowany. Jeśli to widzisz, to jest to błąd w kodzie odblokowania wersji.")


    def launch_wycinator_version(self, version_to_launch):
        if version_to_launch == "Normal":
            wycinator_app = WycinatorToolNormal(self)
        elif version_to_launch == "VIP":
            # Ta linia będzie powodować błąd importu, jeśli VIP nie jest zaimportowany.
            # Ważne: W każdym pliku powinna być tylko odpowiednia klasa narzędziowa.
            # Zostawiamy tu WycinatorToolVIP i WycinatorToolELITE dla spójności,
            # ale w praktyce w każdym pliku będzie tylko jedna z nich, a pozostałe będą "importowane"
            # (lub de facto uruchamiane jako osobne programy/pliki).
            try:
                wycinator_app = WycinatorToolVIP(self)
            except NameError:
                messagebox.showerror("Błąd", "Wersja VIP nie jest dostępna w tym wydaniu.")
                return
        elif version_to_launch == "ELITE":
            try:
                wycinator_app = WycinatorToolELITE(self)
            except NameError:
                messagebox.showerror("Błąd", "Wersja ELITE nie jest dostępna w tym wydaniu.")
                return
        else:
            messagebox.showerror("Błąd", "Nieznana wersja Wycinatora.")
            return
        
        wycinator_app.mainloop() 
        # Po zakończeniu działania Wycinatora, wracamy do okna launchera
        self.deiconify() 

def start_application():
    """Funkcja uruchamiająca proces logowania, a następnie launchera."""
    def run_launcher():
        app = WycinatorLauncher()
        app.mainloop()

    login_app = LoginRegisterApp(run_launcher)
    login_app.mainloop()

if __name__ == "__main__":
    start_application()