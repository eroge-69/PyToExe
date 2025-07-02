# -*- coding: utf-8 -*-
import platform
import psutil
import socket
import json
import requests # Potrzebne do wysyłania danych HTTP

def get_system_info():
    """
    Zbiera szczegółowe informacje techniczne o systemie operacyjnym i sprzęcie.
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
    info['Procent Użycia CPU'] = psutil.cpu_percent(interval=1) # Procent użycia CPU w ciągu 1 sekundy

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

    # Informacje o zainstalowanych grach (placeholder)
    info['Zainstalowane Gry'] = "Wykrywanie gier wymaga specyficznych metod dla każdej platformy (np. Steam, Epic Games) i jest poza zakresem tego prostego skryptu."

    # Informacje o GPU (placeholder)
    info['Informacje o GPU'] = "Wykrywanie szczegółów GPU i jego wydajności wymaga specjalistycznych bibliotek (np. pynvml dla NVIDIA) lub narzędzi systemowych, co wykracza poza zakres psutil."

    return info

def send_data_to_website(data, url):
    """
    Wysyła zebrane dane na podany adres URL za pomocą żądania HTTP POST.
    """
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() # Wyrzuci błąd dla statusów 4xx/5xx
        print(f"Dane wysłane pomyślnie na {url}. Status: {response.status_code}")
        print(f"Odpowiedź serwera: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas wysyłania danych na stronę: {e}")

def main():
    """
    Główna funkcja programu, zbiera informacje i wysyła je.
    """
    print("Zbieranie informacji o komputerze...")
    system_info = get_system_info()

    print("
--- Szczegółowe Informacje Techniczne (do wysłania) ---")
    # Wyświetl dane w konsoli przed wysłaniem
    print(json.dumps(system_info, indent=4, ensure_ascii=False))

    # --- WAŻNE ---
    # Adres URL Twojej strony PHP, która będzie odbierać dane.
    # Ten URL jest dynamicznie wstawiany przez skrypt PHP.
    php_url = "https://pcmod.pl/pcinfo.php"

    print(f"
Próba wysłania danych na adres: {php_url}")
    send_data_to_website(system_info, php_url)

if __name__ == "__main__":
    main()