# -*- coding: utf-8 -*-
import platform
import psutil
import socket
import json
import requests # Potrzebne do wysyłania danych HTTP
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading # Do uruchamiania operacji sieciowych w tle, aby GUI nie zamarzało

# Spróbuj zaimportować pynvml dla informacji o GPU NVIDIA
try:
    from pynvml import *
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    # print("Ostrzeżenie: Biblioteka 'pynvml' nie jest zainstalowana lub nie wykryto karty NVIDIA. Informacje o GPU mogą być ograniczone.")
except NVMLError as error:
    NVML_AVAILABLE = False
    # print(f"Ostrzeżenie: Błąd inicjalizacji NVML: {error}. Informacje o GPU mogą być ograniczone.")


def get_system_info():
    """
    Zbiera szczegółowe informacje techniczne o systemie operacyjnym i sprzęcie.
    Zwraca słownik z zebranymi informacjami.
    """
    info = {}

    # Informacje o systemie operacyjnym
    info['System Operacyjny'] = platform.system()
    info['Wersja OS'] = platform.version()
    info['Architektura'] = platform.machine()
    info['Nazwa Komputera'] = platform.node()
    info['Procesor'] = platform.processor()

    # Informacje o pamięci RAM
    svmem = psutil.virtual_memory()
    info['Całkowita Pamięć RAM (GB)'] = round(svmem.total / (1024**3), 2)
    info['Dostępna Pamięć RAM (GB)'] = round(svmem.available / (1024**3), 2)
    info['Używana Pamięć RAM (GB)'] = round(svmem.used / (1024**3), 2)
    info['Procent Użycia RAM'] = svmem.percent

    # Informacje o procesorze (rozszerzone)
    info['Liczba Rdzeni Fizycznych CPU'] = psutil.cpu_count(logical=False)
    info['Liczba Rdzeni Logicznych CPU'] = psutil.cpu_count(logical=True)
    info['Procent Użycia CPU (chwila)'] = psutil.cpu_percent(interval=1) # Procent użycia CPU w ciągu 1 sekundy

    # Średnie obciążenie systemu (Load Average) - typowe dla Linux/macOS
    load_avg = psutil.getloadavg()
    if platform.system() != "Windows":
        info['Średnie Obciążenie CPU (1, 5, 15 min)'] = [round(x, 2) for x in load_avg]
    else:
        info['Średnie Obciążenie CPU'] = 'Niedostępne na Windows (użyj Menedżera Zadań)'


    # Częstotliwość CPU (jeśli dostępna)
    cpu_freq = psutil.cpu_freq()
    if cpu_freq:
        info['Aktualna Częstotliwość CPU (MHz)'] = round(cpu_freq.current, 2)
        info['Minimalna Częstotliwość CPU (MHz)'] = round(cpu_freq.min, 2)
        info['Maksymalna Częstotliwość CPU (MHz)'] = round(cpu_freq.max, 2)
    else:
        info['Częstotliwość CPU'] = 'Niedostępne'

    # Informacje o dyskach
    disk_partitions = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_partitions.append({
                'Dysk': partition.device,
                'Punkt Montowania': partition.mountpoint,
                'System Plików': partition.fstype,
                'Całkowity Rozmiar (GB)': round(usage.total / (1024**3), 2),
                'Użyty Rozmiar (GB)': round(usage.used / (1024**3), 2),
                'Wolny Rozmiar (GB)': round(usage.free / (1024**3), 2),
                'Procent Użycia Dysku': usage.percent
            })
        except PermissionError:
            # Niektóre partycje mogą wymagać uprawnień administratora
            continue
    info['Informacje o Dyskach'] = disk_partitions

    # Informacje o sieci
    net_if_addrs = {}
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET': # IPv4
                net_if_addrs[interface_name] = {
                    'Adres IP': address.address,
                    'Maska Sieci': address.netmask,
                    'Adres Broadcast': address.broadcast
                }
    info['Informacje o Sieci'] = net_if_addrs

    # Informacje o GPU (NVIDIA za pomocą pynvml)
    gpu_info = []
    if NVML_AVAILABLE:
        try:
            nvmlInit()
            device_count = nvmlDeviceGetCount()
            for i in range(device_count):
                handle = nvmlDeviceGetHandleByIndex(i)
                name = nvmlDeviceGetName(handle)
                utilization = nvmlDeviceGetUtilizationRates(handle)
                memory_info = nvmlDeviceGetMemoryInfo(handle)
                gpu_info.append({
                    'Nazwa GPU': name.decode('utf-8'),
                    'Użycie GPU (%)': utilization.gpu,
                    'Użycie Pamięci GPU (%)': utilization.memory,
                    'Całkowita Pamięć GPU (MB)': round(memory_info.total / (1024**2), 2),
                    'Użyta Pamięć GPU (MB)': round(memory_info.used / (1024**2), 2),
                    'Wolna Pamięć GPU (MB)': round(memory_info.free / (1024**2), 2),
                })
            nvmlShutdown()
        except NVMLError as error:
            gpu_info.append(f"Błąd podczas pobierania danych GPU (NVIDIA): {error}")
    else:
        gpu_info.append("Informacje o GPU: Niedostępne. Wymagana biblioteka 'pynvml' dla kart NVIDIA lub inne narzędzia dla kart AMD/Intel.")

    info['Informacje o GPU'] = gpu_info

    # Informacje o zainstalowanych grach (placeholder)
    info['Zainstalowane Gry'] = "Wykrywanie gier wymaga specyficznych metod dla każdej platformy (np. Steam, Epic Games) i jest poza zakresem tego prostego skryptu."

    return info

def send_data_to_website(data, url, status_callback=None):
    """
    Wysyła zebrane dane na podany adres URL za pomocą żądania HTTP POST.
    Wywołuje status_callback z wiadomościami o postępie.
    """
    try:
        if status_callback:
            status_callback("Wysyłanie danych...")
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers, timeout=30) # Dodano timeout
        response.raise_for_status() # Wyrzuci błąd dla statusów 4xx/5xx
        message = f"Dane wysłane pomyślnie. Status: {response.status_code}"
        if status_callback:
            status_callback(message)
        return True, message
    except requests.exceptions.Timeout:
        message = f"Błąd: Przekroczono czas oczekiwania na odpowiedź serwera ({url})."
        if status_callback:
            status_callback(message)
        return False, message
    except requests.exceptions.RequestException as e:
        message = f"Błąd podczas wysyłania danych na stronę: {e}"
        if status_callback:
            status_callback(message)
        return False, message

class App:
    def __init__(self, master):
        self.master = master
        master.title("Informacje o Komputerze")
        master.geometry("800x600") # Ustawienie rozmiaru okna
        master.resizable(True, True) # Pozwól na zmianę rozmiaru okna

        # Stylizacja (opcjonalnie, ale poprawia wygląd)
        style = ttk.Style()
        style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
        style.configure('TButton', font=('Arial', 12), padding=10)
        style.configure('TLabel', font=('Arial', 10), padding=5)

        # Ramka na przyciski
        button_frame = ttk.Frame(master, padding="10 10 10 10")
        button_frame.pack(side=tk.TOP, fill=tk.X)

        # Przycisk "Zbierz i Wyślij Informacje"
        self.send_button = ttk.Button(button_frame, text="Zbierz i Wyślij Informacje", command=self.start_collection_and_send)
        self.send_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Etykieta statusu
        self.status_label = ttk.Label(button_frame, text="Gotowy.", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Pole tekstowe do wyświetlania informacji
        self.info_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=100, height=30, font=('Consolas', 10), bg="#f0f0f0", fg="#333333")
        self.info_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Ustawienie URL PHP
        self.php_url = "https://pcmod.pl/pcinfo.php"

        # Wyświetl początkowe informacje
        self.update_info_display("Kliknij 'Zbierz i Wyślij Informacje', aby rozpocząć...")

    def update_info_display(self, text):
        """Aktualizuje pole tekstowe z informacjami."""
        self.info_text.config(state=tk.NORMAL) # Włącz edycję
        self.info_text.delete(1.0, tk.END) # Wyczyść poprzednią zawartość
        self.info_text.insert(tk.END, text) # Wstaw nowy tekst
        self.info_text.config(state=tk.DISABLED) # Wyłącz edycję

    def update_status_label(self, message, color="blue"):
        """Aktualizuje etykietę statusu."""
        self.status_label.config(text=message, foreground=color)

    def start_collection_and_send(self):
        """Rozpoczyna zbieranie i wysyłanie danych w osobnym wątku."""
        self.send_button.config(state=tk.DISABLED) # Wyłącz przycisk podczas operacji
        self.update_status_label("Zbieranie informacji... Proszę czekać.", "orange")
        # Uruchom operację w osobnym wątku, aby GUI nie zamarzało
        threading.Thread(target=self._collect_and_send_data_thread).start()

    def _collect_and_send_data_thread(self):
        """Funkcja zbierająca i wysyłająca dane, uruchamiana w wątku."""
        try:
            system_info = get_system_info()
            formatted_info = json.dumps(system_info, indent=4, ensure_ascii=False)

            # Aktualizuj GUI z zebranymi danymi (musi być w głównym wątku Tkinter)
            self.master.after(0, self.update_info_display, formatted_info)
            self.master.after(0, self.update_status_label, "Informacje zebrane. Wysyłanie...", "orange")

            success, message = send_data_to_website(system_info, self.php_url, self.update_status_label)

            if success:
                self.master.after(0, self.update_status_label, message, "green")
                self.master.after(0, lambda: messagebox.showinfo("Sukces", message))
            else:
                self.master.after(0, self.update_status_label, message, "red")
                self.master.after(0, lambda: messagebox.showerror("Błąd", message))

        except Exception as e:
            error_message = f"Wystąpił nieoczekiwany błąd: {e}"
            self.master.after(0, self.update_status_label, error_message, "red")
            self.master.after(0, lambda: messagebox.showerror("Błąd", error_message))
        finally:
            self.master.after(0, lambda: self.send_button.config(state=tk.NORMAL)) # Włącz przycisk z powrotem


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
