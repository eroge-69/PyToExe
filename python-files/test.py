import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time
from datetime import datetime

class FireTruckDiagnostic:
    def __init__(self, root):
        self.root = root
        self.root.title("System Diagnostyczny Pojazdu Ratowniczo-Gaśniczego")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        self.root.attributes('-fullscreen', True)
        
        # Zmienne stanu
        self.is_scanning = False
        self.current_system = 0
        
        # Systemy główne
        self.systems = [
            "Sterownik główny SERCA-1",
            "Sterownik pomocniczy SERCA-2", 
            "Moduł piany FOAM-CTRL-A",
            "Moduł piany FOAM-CTRL-B",
            "Moduł CAN Master",
            "Moduł CAN Slave-1", 
            "Moduł CAN Slave-2",
            "Czujniki temperatury i ciśnienia",
            "Barografy piany i wody",
            "Zawór dozownika (serwo)",
            "Moduły zbiorcze H2O/FOAM",
            "Czujniki słupa 4-20mA",
            "Wyświetlacze przód/tył",
            "Moduł lamp błyskowych",
            "Zwijadło szybkiego natarcia",
            "Maszt oświetleniowy",
            "Moduły PDU (przekaźniki)",
            "Magistrala CAN-BUS"
        ]
        
        # Komórki pamięci dla różnych modułów
        self.memory_modules = [
            "SERCA-1 EEPROM (512KB)",
            "SERCA-2 EEPROM (512KB)", 
            "FOAM-CTRL-A Flash (256KB)",
            "FOAM-CTRL-B Flash (256KB)",
            "CAN Master NVRAM (128KB)",
            "CAN Slave-1 EEPROM (64KB)",
            "CAN Slave-2 EEPROM (64KB)",
            "PDU-1 Config (32KB)",
            "PDU-2 Config (32KB)",
            "Wyświetlacz-P FRAM (16KB)",
            "Wyświetlacz-T FRAM (16KB)",
            "Moduł lamp Flash (64KB)",
            "Zwijadło EEPROM (32KB)",
            "Maszt Config (32KB)"
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Nagłówek
        header_frame = tk.Frame(self.root, bg='#cc0000', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🚒 SYSTEM DIAGNOSTYCZNY POJAZDU RATOWNICZO-GAŚNICZEGO", 
                              font=('Arial', 20, 'bold'), bg='#cc0000', fg='white')
        title_label.pack(pady=20)
        
        # Główna ramka
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Lewa strona - status systemu
        left_frame = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Status label
        self.status_label = tk.Label(left_frame, text="GOTOWY DO DIAGNOSTYKI", 
                                    font=('Arial', 16, 'bold'), bg='#2d2d2d', fg='#00ff00')
        self.status_label.pack(pady=15)
        
        # Progress bar główny
        progress_frame = tk.Frame(left_frame, bg='#2d2d2d')
        progress_frame.pack(pady=10)
        
        tk.Label(progress_frame, text="POSTĘP DIAGNOSTYKI GŁÓWNEJ:", 
                font=('Arial', 10, 'bold'), bg='#2d2d2d', fg='white').pack()
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate',
                                          variable=self.progress_var)
        self.progress_bar.pack(pady=5)
        
        # Progress bar pamięci
        memory_frame = tk.Frame(left_frame, bg='#2d2d2d')
        memory_frame.pack(pady=10)
        
        tk.Label(memory_frame, text="ANALIZA KOMÓREK PAMIĘCI:", 
                font=('Arial', 10, 'bold'), bg='#2d2d2d', fg='#00ffff').pack()
        
        self.memory_progress_var = tk.DoubleVar()
        self.memory_progress_bar = ttk.Progressbar(memory_frame, length=400, mode='determinate',
                                                 variable=self.memory_progress_var)
        self.memory_progress_bar.pack(pady=5)
        
        self.memory_status_label = tk.Label(memory_frame, text="Gotowy do skanowania pamięci", 
                                          font=('Arial', 10), bg='#2d2d2d', fg='#00ffff')
        self.memory_status_label.pack(pady=2)
        
        # Current system label
        self.current_system_label = tk.Label(left_frame, text="", 
                                           font=('Arial', 14), bg='#2d2d2d', fg='#ffff00')
        self.current_system_label.pack(pady=10)
        
        # Console output
        console_frame = tk.Frame(left_frame, bg='#2d2d2d')
        console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        console_label = tk.Label(console_frame, text="KONSOLA DIAGNOSTYCZNA", 
                               font=('Arial', 12, 'bold'), bg='#2d2d2d', fg='white')
        console_label.pack(anchor='w')
        
        # Scrolled text dla konsoli
        self.console_text = tk.Text(console_frame, height=15, width=60, 
                                  bg='#000000', fg='#00ff00', 
                                  font=('Courier', 10))
        scrollbar = tk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=scrollbar.set)
        
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Prawa strona - parametry
        right_frame = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Parametry systemów
        params_label = tk.Label(right_frame, text="PARAMETRY SYSTEMÓW", 
                              font=('Arial', 16, 'bold'), bg='#2d2d2d', fg='white')
        params_label.pack(pady=15)
        
        # Ramka na parametry
        self.params_frame = tk.Frame(right_frame, bg='#2d2d2d')
        self.params_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.setup_parameters()
        
        # Przyciski sterowania
        control_frame = tk.Frame(self.root, bg='#1a1a1a')
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_button = tk.Button(control_frame, text="ROZPOCZNIJ DIAGNOSTYKĘ", 
                                    command=self.start_diagnostic, bg='#00aa00', fg='white',
                                    font=('Arial', 14, 'bold'), width=20)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(control_frame, text="ZATRZYMAJ", 
                                   command=self.stop_diagnostic, bg='#aa0000', fg='white',
                                   font=('Arial', 14, 'bold'), width=15)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(control_frame, text="RESET", 
                                    command=self.reset_diagnostic, bg='#0066cc', fg='white',
                                    font=('Arial', 14, 'bold'), width=15)
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        # Przycisk wyjścia
        exit_button = tk.Button(control_frame, text="WYJŚCIE [ESC]", 
                              command=self.root.quit, bg='#666666', fg='white',
                              font=('Arial', 12, 'bold'), width=15)
        exit_button.pack(side=tk.RIGHT, padx=10)
        
        # Bind ESC key
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Dodaj wstępne komunikaty
        self.add_console_message("System gotowy do diagnostyki")
        self.add_console_message("Podłączenie do ECU... OK")
        self.add_console_message("Inicjalizacja modułów... OK")
        
    def setup_parameters(self):
        # Parametry do wyświetlenia - zabudowa strażacka
        self.param_labels = {}
        
        params = [
            ("Temperatura systemu", "24°C", "#00ff00"),
            ("Ciśnienie niskie", "8.2 bar", "#00ff00"),
            ("Ciśnienie wysokie", "38.5 bar", "#00ff00"),
            ("Podciśnienie", "-0.3 bar", "#00ff00"),
            ("Barograf H2O", "67%", "#00ff00"),
            ("Barograf FOAM", "42%", "#ffff00"),
            ("Dozownik (kąt)", "45°", "#00ff00"),
            ("Słup wody", "12.4 mA", "#00ff00"),
            ("Słup piany", "8.7 mA", "#00ff00"),
            ("Lampy błyskowe", "AKTYWNE", "#00ff00"),
            ("Zwijadło SN", "GOTOWE", "#00ff00"),
            ("Maszt oświetlen.", "ZŁOŻONY", "#ffff00"),
            ("PDU główny", "24.1 V", "#00ff00"),
            ("SERCA-1 status", "ON-LINE", "#00ff00"),
            ("SERCA-2 status", "ON-LINE", "#00ff00")
        ]
        
        for i, (name, value, color) in enumerate(params):
            frame = tk.Frame(self.params_frame, bg='#2d2d2d')
            frame.pack(fill=tk.X, pady=3)
            
            name_label = tk.Label(frame, text=name + ":", font=('Arial', 10), 
                                bg='#2d2d2d', fg='white', width=18, anchor='w')
            name_label.pack(side=tk.LEFT)
            
            value_label = tk.Label(frame, text=value, font=('Arial', 10, 'bold'), 
                                 bg='#2d2d2d', fg=color, width=12, anchor='w')
            value_label.pack(side=tk.RIGHT)
            
            self.param_labels[name] = value_label
    
    def add_console_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        self.console_text.insert(tk.END, full_message)
        self.console_text.see(tk.END)
        
    def start_diagnostic(self):
        if not self.is_scanning:
            self.is_scanning = True
            self.start_button.config(state='disabled')
            self.current_system = 0
            self.progress_var.set(0)
            self.memory_progress_var.set(0)
            self.status_label.config(text="DIAGNOSTYKA W TOKU...", fg='#ffff00')
            self.memory_status_label.config(text="Oczekiwanie na analizę pamięci...")
            
            # Uruchom diagnostykę w osobnym wątku
            threading.Thread(target=self.run_diagnostic, daemon=True).start()
    
    def stop_diagnostic(self):
        self.is_scanning = False
        self.start_button.config(state='normal')
        self.status_label.config(text="DIAGNOSTYKA ZATRZYMANA", fg='#ff6600')
        self.current_system_label.config(text="")
        self.memory_status_label.config(text="Analiza pamięci przerwana")
        
    def reset_diagnostic(self):
        self.stop_diagnostic()
        self.progress_var.set(0)
        self.memory_progress_var.set(0)
        self.console_text.delete(1.0, tk.END)
        self.status_label.config(text="GOTOWY DO DIAGNOSTYKI", fg='#00ff00')
        self.memory_status_label.config(text="Gotowy do skanowania pamięci")
        self.add_console_message("System zresetowany")
        self.add_console_message("Gotowy do ponownej diagnostyki")
    
    def run_diagnostic(self):
        messages = [
            "Inicjalizacja połączenia CAN-BUS...",
            "Odczyt komórek pamięci EEPROM...",
            "Test komunikacji ze sterownikami SERCA...",
            "Sprawdzanie kalibracji czujników...",
            "Analiza parametrów barografów...",
            "Diagnostyka modułów zbiorczych...",
            "Weryfikacja pętli prądowej 4-20mA...",
            "Test zaworów dozownika...",
            "Sprawdzanie modułów PDU...",
            "Kalibracja czujników ciśnienia...",
            "Diagnostyka lamp błyskowych...",
            "Test systemu zwijadła SN...",
            "Sprawdzanie masztu oświetleniowego...",
            "Analiza wyświetlaczy LCD...",
            "Weryfikacja integralności firmware...",
            "Sprawdzanie magistrali RS485...",
            "Test procedur bezpieczeństwa...",
            "Analiza historii błędów...",
            "Kalibracja przetworników A/D...",
            "Sprawdzanie watchdog timers..."
        ]
        
        detailed_messages = [
            "Odczyt sektora EEPROM 0x0000-0x00FF...",
            "Test komunikacji SERCA-1 @ 0x10...",
            "Test komunikacji SERCA-2 @ 0x11...",
            "Kalibracja czujnika temperatury TMP-01...",
            "Sprawdzanie czujnika ciśnienia P-LOW...",
            "Sprawdzanie czujnika ciśnienia P-HIGH...",
            "Test czujnika podciśnienia P-NEG...",
            "Analiza barografu H2O: sector 0x200...",
            "Analiza barografu FOAM: sector 0x201...",
            "Pozycjonowanie zaworu dozownika...",
            "Test pętli prądowej słupa wody...",
            "Test pętli prądowej słupa piany...",
            "Sprawdzanie wyświetlacza przód...",
            "Sprawdzanie wyświetlacza tył...",
            "Diagnostyka modułu lamp błyskowych...",
            "Test enkodera zwijadła SN...",
            "Sprawdzanie silnika masztu...",
            "Analiza modułu PDU-1...",
            "Analiza modułu PDU-2...",
            "Weryfikacja sum kontrolnych..."
        ]
        
        for i, system in enumerate(self.systems):
            if not self.is_scanning:
                break
                
            self.current_system_label.config(text=f"Diagnostyka: {system}")
            self.add_console_message(f">>> Rozpoczęcie testu: {system}")
            
            # Symulacja testów dla każdego systemu - więcej szczegółów
            test_count = random.randint(4, 8)  # Więcej testów na system
            for j in range(test_count):
                if not self.is_scanning:
                    break
                    
                # Wybierz odpowiedni typ komunikatu
                if random.random() < 0.7:
                    message = random.choice(detailed_messages)
                else:
                    message = random.choice(messages)
                    
                self.add_console_message(message)
                
                # Aktualizuj parametry losowo
                self.update_random_parameters()
                
                time.sleep(random.uniform(0.3, 1.5))
                
                # Czasami dodaj szczegółowe informacje
                if random.random() < 0.4:
                    detail_messages = [
                        "   → Odczyt rejestru: 0x" + format(random.randint(0, 255), '02X'),
                        "   → Wartość odczytana: " + str(random.randint(100, 999)),
                        "   → Suma kontrolna: OK",
                        "   → Timeout: " + str(random.randint(5, 50)) + "ms",
                        "   → Kalibracja: WYMAGANA",
                        "   → Status: OPERATIONAL",
                        "   → Firmware: v" + str(random.randint(1, 9)) + "." + str(random.randint(0, 9)),
                        "   → Temperatura pracy: " + str(random.randint(20, 45)) + "°C"
                    ]
                    self.add_console_message(random.choice(detail_messages))
                
                # Czasami dodaj ostrzeżenie specyficzne dla zabudowy
                if random.random() < 0.25:
                    warning_messages = [
                        "UWAGA: Barograf wymaga kalibracji",
                        "INFO: Czujnik ciśnienia - odchylenie 2%",
                        "STATUS: Zawór dozownika - zużycie uszczelki",
                        "OSTRZEŻENIE: Moduł PDU - przekroczenie temp.",
                        "ALERT: Pętla 4-20mA - szum na linii",
                        "INFO: SERCA-1 - czas odpowiedzi zwiększony",
                        "UWAGA: Zwijadło SN - wymagane smarowanie",
                        "STATUS: Lampy błyskowe - LED degradacja"
                    ]
                    self.add_console_message(random.choice(warning_messages))
            
            # Końcowy komunikat dla systemu
            status_messages = [
                "Test zakończony - STATUS: OPERATIONAL",
                "Diagnostyka ukończona - WYNIK: PASSED", 
                "Analiza zakończona - SYSTEM: READY",
                "Weryfikacja ukończona - STAN: GOOD",
                "Procedura ukończona - RESULT: OK",
                "Sprawdzenie zakończone - STATUS: NOMINAL"
            ]
            self.add_console_message(random.choice(status_messages))
            
            # Aktualizuj progress bar
            progress = ((i + 1) / len(self.systems)) * 100
            self.progress_var.set(progress)
            
            time.sleep(random.uniform(0.5, 2.0))
        
        if self.is_scanning:
            # Po głównej diagnostyce - rozpocznij analizę pamięci
            self.add_console_message("="*50)
            self.add_console_message("ROZPOCZĘCIE ANALIZY KOMÓREK PAMIĘCI")
            self.add_console_message("Łączny rozmiar: ~2MB w " + str(len(self.memory_modules)) + " modułach")
            self.memory_status_label.config(text="Skanowanie pamięci w toku...")
            
            # Analiza pamięci
            threading.Thread(target=self.run_memory_analysis, daemon=True).start()
            
    def run_memory_analysis(self):
        """Oddzielna analiza komórek pamięci z własnym postępem"""
        
        memory_messages = [
            "Mapowanie przestrzeni adresowej...",
            "Sprawdzanie sum kontrolnych CRC32...",
            "Analiza integralności danych...",
            "Weryfikacja bootloadera...",
            "Skanowanie bad blocks...",
            "Test read/write cycles...",
            "Sprawdzanie wear leveling...",
            "Analiza parametrów konfiguracyjnych...",
            "Weryfikacja firmware checksums...",
            "Test retention time..."
        ]
        
        for i, memory_module in enumerate(self.memory_modules):
            if not self.is_scanning:
                break
                
            self.memory_status_label.config(text=f"Analiza: {memory_module}")
            self.add_console_message(f">>> Skanowanie pamięci: {memory_module}")
            
            # Szczegółowa analiza każdego modułu pamięci
            sectors = random.randint(8, 32)  # Ilość sektorów do sprawdzenia
            
            for sector in range(sectors):
                if not self.is_scanning:
                    break
                    
                # Adres sektora
                sector_addr = sector * 1024
                self.add_console_message(f"   Sektor 0x{sector_addr:04X}: " + random.choice([
                    "CRC OK", "Odczyt OK", "Weryfikacja OK", "Suma kontrolna OK",
                    "Dane ważne", "Backup OK", "Konfiguracja OK"
                ]))
                
                # Czasami szczegółowe informacje
                if random.random() < 0.3:
                    detail = random.choice([
                        f"      → Size: {random.randint(512, 4096)} bytes",
                        f"      → Used: {random.randint(10, 90)}%", 
                        f"      → Cycles: {random.randint(100, 9999)}",
                        f"      → Last write: {random.randint(1, 365)} days ago",
                        f"      → Temperature: {random.randint(20, 45)}°C"
                    ])
                    self.add_console_message(detail)
                
                time.sleep(random.uniform(0.1, 0.4))
                
                # Aktualizuj postęp pamięci
                current_progress = ((i * 20 + sector + 1) / (len(self.memory_modules) * 20)) * 100
                self.memory_progress_var.set(min(current_progress, 100))
            
            # Czasami ostrzeżenia dotyczące pamięci
            if random.random() < 0.2:
                warnings = [
                    "Error in module memory",
                    "Error in CANmemory", 
                    "Error in Bootloader",
                    "Error processor high temp."
                ]
                self.add_console_message(random.choice(warnings))
            
            self.add_console_message(f"Moduł {memory_module}: COMPLETE")
            
            # Końcowy postęp pamięci
            memory_progress = ((i + 1) / len(self.memory_modules)) * 100
            self.memory_progress_var.set(memory_progress)
            
            time.sleep(random.uniform(0.5, 1.0))
        
        if self.is_scanning:
            self.add_console_message("="*50)
            self.add_console_message("ANALIZA PAMIĘCI ZAKOŃCZONA")
            self.add_console_message("Łącznie przeskanowano ~2MB danych")
            self.add_console_message("Wszystkie komórki pamięci sprawdzone")
            self.add_console_message("Int. Data not working")
            self.add_console_message("="*50)
            self.add_console_message("PEŁNA DIAGNOSTYKA ZAKOŃCZONA")
            self.add_console_message("Wszystkie moduły zabudowy przetestowane")
            self.add_console_message("Raport diagnostyczny zapisany")
            self.add_console_message("System gotowy do eksploatacji")
            self.status_label.config(text="PEŁNA DIAGNOSTYKA ZAKOŃCZONA", fg='#00ff00')
            self.memory_status_label.config(text="Analiza pamięci: COMPLETE")
            self.current_system_label.config(text="")
            self.start_button.config(state='normal')
            self.is_scanning = False
    
    def update_random_parameters(self):
        # Losowe aktualizacje parametrów - zabudowa strażacka
        updates = {
            "Temperatura systemu": (f"{random.randint(15, 55)}°C", "#00ff00" if random.randint(15, 55) < 45 else "#ffff00"),
            "Ciśnienie niskie": (f"{random.uniform(6.0, 20.0):.1f} bar", "#00ff00"),
            "Ciśnienie wysokie": (f"{random.uniform(30.0, 55.0):.1f} bar", "#00ff00"),
            "Podciśnienie": (f"{random.uniform(-0.8, -0.1):.1f} bar", "#00ff00"),
            "Barograf H2O": (f"{random.randint(0, 100)}%", "#00ff00"),
            "Barograf FOAM": (f"{random.randint(0, 100)}%", "#ffff00" if random.randint(0, 100) < 50 else "#00ff00"),
            "Dozownik (kąt)": (f"{random.randint(0, 180)}°", "#00ff00"),
            "Słup wody": (f"{random.uniform(4.0, 20.0):.1f} mA", "#00ff00"),
            "Słup piany": (f"{random.uniform(4.0, 20.0):.1f} mA", "#00ff00"),
            "Lampy błyskowe": (random.choice(["AKTYWNE", "STANDBY", "TEST"]), "#00ff00"),
            "Zwijadło SN": (random.choice(["GOTOWE", "ROZWINIĘTE", "ZWIJANIE"]), "#00ff00"),
            "Maszt oświetlen.": (random.choice(["ZŁOŻONY", "PODNOSZENIE", "ROZŁOŻONY"]), "#ffff00"),
            "PDU główny": (f"{random.uniform(22.0, 26.0):.1f} V", "#00ff00"),
            "SERCA-1 status": (random.choice(["ON-LINE", "BUSY", "IDLE"]), "#00ff00"),
            "SERCA-2 status": (random.choice(["ON-LINE", "BUSY", "IDLE"]), "#00ff00"),
        }
        
        # Aktualizuj 2-3 losowe parametry za jednym razem
        params_to_update = random.sample(list(updates.keys()), random.randint(2, 4))
        
        for param_name in params_to_update:
            if param_name in updates and param_name in self.param_labels:
                value, color = updates[param_name]
                self.param_labels[param_name].config(text=value, fg=color)

def main():
    root = tk.Tk()
    app = FireTruckDiagnostic(root)
    root.mainloop()

if __name__ == "__main__":
    main()
