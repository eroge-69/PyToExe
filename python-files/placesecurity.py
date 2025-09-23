import os
import time
from rich.console import Console
from rich.panel import Panel
from rich import print
import requests
import json
import platform
import psutil
import wmi
import geocoder
import subprocess
import sys
import webbrowser
import getpass
import datetime

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Instalowanie brakującego pakietu: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Lista wymaganych pakietów
required = [
    "rich",
    "requests",
    "psutil",
    "wmi",
    "geocoder"
]

for pkg in required:
    install_and_import(pkg)

console = Console()
panel = Panel.fit('\n             PlaceRP Security - Hounds                \n    ', title='', border_style='cyan', padding=(2, 3), style='bold white', width=110)
console.print(panel)
webhook_url = 'https://discord.com/api/webhooks/1419762908438466680/dsSE1F7YqU21JMr8qgjZP8xnFhvyHEXZAEMaAJuBybCy-Pep0FE7XEmaQbXP49UT8bgD'
print('--------------------------------------------------')
print('[green]Wybierz opcję:[/green]')
print('[bright_blue]1. Wszystkie opcje[/bright_blue]')
print('[blue]2.[/blue] Sprawdź Detection')
print('[blue]3.[/blue] Sprawdź katalog kosza')
print('[blue]4.[/blue] Otwórz katalogi mods, citizen, historie i cache')
print('[blue]5.[/blue] Sprawdź ostatnio zmodyfikowane pliki na pulpicie')
print('[blue]6.[/blue] Sprawdź informacje o systemie')
print('[blue]7.[/blue] Sprawdź ostatnie pendrive [BETA]')
print('[blue]8.[/blue] Zakończ program')
print('--------------------------------------------------')

def wyslij_na_webhook_embed(tytul, tresc, kolor):
    try:
        payload = {'embeds': [{'title': tytul, 'description': tresc, 'color': kolor}]}
        response = requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"Błąd przy wysyłaniu webhook: {e}")

def open_discord():
    url = 'https://discord.gg/placerp'
    webbrowser.open(url)
    tytul = 'PlacerRP - Hounds'
    tresc = f'{platform.node()} odpalił **PlaceRP Security**!'
    kolor = 255
    wyslij_na_webhook_embed(tytul, tresc, kolor)

open_discord()

def loading_animation(duration):
    for i in range(50):
        sys.stdout.write('\r')
        sys.stdout.write('[0;32m[%-50s][0m [0;33m%d%%[0m' % ('=' * i, 2 * i))
        sys.stdout.flush()
        time.sleep(duration)

def sprawdz_imgui(sciezka):
    imgui_path = os.path.join(sciezka, 'imgui.ini')
    if os.path.exists(imgui_path):
        try:
            os.startfile(sciezka)
            if os.path.exists(imgui_path):
                os.system(f'start notepad "{imgui_path}"')
            with open(imgui_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read().lower()
                if 'redengine' in file_content or 'pegasus' in file_content or 'vip' in file_content:
                    tytul = 'Wykryto cheaty!'
                    tresc = f'Wykryto cheaty na komputerze {platform.node()}! **Detekcja Menu**'
                    kolor = 16711680
                    wyslij_na_webhook_embed(tytul, tresc, kolor)
                    print('[red]WYKRYTO CHEATY!!!!!!![/red]')
                    zapisz_do_cache('Wykryto cheaty')
                else:
                    tytul = 'Gracz jest czysty!'
                    tresc = f'Nie wykryto cheatów na komputerze {platform.node()}! **Nie wykryto detekcji**'
                    kolor = 65280
                    wyslij_na_webhook_embed(tytul, tresc, kolor)
                    print('[green]Gracz jest czysty![/green]')
                    zapisz_do_cache('Gracz jest czysty')
        except Exception as e:
            print(f"Błąd przy sprawdzaniu imgui: {e}")
    else:
        tytul = 'Gracz jest czysty!'
        tresc = f'Nie wykryto cheatów na komputerze {platform.node()}! **Nie wykryto detekcji**'
        kolor = 65280
        wyslij_na_webhook_embed(tytul, tresc, kolor)
        print('[green]Gracz jest czysty![/green]')
        zapisz_do_cache('Gracz jest czysty')
        try:
            os.startfile(sciezka)
        except Exception as e:
            print(f"Błąd przy otwieraniu ścieżki: {e}")

def wyslij_plik_na_webhook(plik, webhook_url):
    try:
        with open(plik, 'rb') as f:
            files = {'file': f}
            response = requests.post(webhook_url, files=files)
    except Exception as e:
        print(f"Błąd przy wysyłaniu pliku: {e}")

def generuj_plik_zawartosc(plik, zawartosc):
    try:
        with open(plik, 'w', encoding='utf-8') as f:
            f.write(zawartosc)
    except Exception as e:
        print(f"Błąd przy generowaniu pliku: {e}")

def otworz_katalogi_i_wyslij_na_webhook(webhook_url):
    mods_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'FiveM', 'FiveM.app', 'mods')
    if os.path.exists(mods_path):
        pliki = []
        try:
            for plik in os.listdir(mods_path):
                sciezka_pliku = os.path.join(mods_path, plik)
                if os.path.isfile(sciezka_pliku):
                    rozmiar = os.path.getsize(sciezka_pliku)
                    pliki.append((plik, rozmiar))
            zawartosc_pliku = ''
            for nazwa, rozmiar in pliki:
                zawartosc_pliku += f'{nazwa}: {rozmiar} bytes\n'
            nazwa_pliku = 'pliki_mods.txt'
            generuj_plik_zawartosc(nazwa_pliku, zawartosc_pliku)
            wyslij_plik_na_webhook(nazwa_pliku, webhook_url)
            print('Zapisano info o modsach!')
        except Exception as e:
            print(f"Błąd przy przetwarzaniu mods: {e}")
    else:
        print('Katalog mods nie istnieje.')

def zapisz_do_cache(info):
    try:
        documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')
        cache_folder = os.path.join(documents_folder, 'mOnteySecurity')
        cache_file_path = os.path.join(cache_folder, 'mOnteySecurity-wynik.txt')
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
        header = 'mOntey Security - Hounds\n\n'
        with open(cache_file_path, 'a', encoding='utf-8') as cache_file:
            cache_file.write(header)
            cache_file.write(f'{info}\n')
    except Exception as e:
        print(f'Błąd podczas zapisywania do pliku cache: {e}')

def sprawdz_kosz():
    kosz_path = 'C:\\$Recycle.Bin'
    if os.path.exists(kosz_path):
        try:
            files_in_bin = os.listdir(kosz_path)
            latest_modification_time = 0
            for file_name in files_in_bin:
                file_path = os.path.join(kosz_path, file_name)
                if os.path.exists(file_path):
                    modification_time = os.path.getmtime(file_path)
                    latest_modification_time = max(latest_modification_time, modification_time)
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest_modification_time))
            print(f'Kosz był ostatnio modyfikowany: {formatted_time}')
        except Exception as e:
            print(f"Błąd przy sprawdzaniu kosza: {e}")
    else:
        print('Kosz nie istnieje.')

def otworz_katalogi():
    paths_to_open = [
        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'FiveM', 'FiveM.app', 'mods'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'FiveM', 'FiveM.app', 'citizen', 'common', 'data'),
        'C:\\Windows\\Prefetch',
        'C:\\Windows\\System32\\drivers\\etc',
        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Microsoft', 'Windows', 'History'),
        'C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive',
        os.path.join(os.path.expanduser('~'), 'Recent')
    ]
    
    for path in paths_to_open:
        if os.path.exists(path):
            try:
                os.startfile(path)
                print(f'Pomyślnie otwarto katalog: {path}')
            except Exception as e:
                print(f'Błąd podczas otwierania katalogu {path}: {e}')
        else:
            print(f'Katalog {path} nie istnieje.')

def ostatnio_modyfikowane(sciezka, limit=10):
    """Funkcja zwracająca listę ostatnio zmodyfikowanych plików w danej ścieżce."""
    lista_modyfikowanych = []
    try:
        for root, dirs, files in os.walk(sciezka):
            for plik in files:
                sciezka_pliku = os.path.join(root, plik)
                if os.path.isfile(sciezka_pliku):
                    mtime = os.path.getmtime(sciezka_pliku)
                    lista_modyfikowanych.append((plik, datetime.datetime.fromtimestamp(mtime)))
                if len(lista_modyfikowanych) >= limit:
                    break
            if len(lista_modyfikowanych) >= limit:
                break
        # Sortuj od najnowszych
        lista_modyfikowanych.sort(key=lambda x: x[1], reverse=True)
        return lista_modyfikowanych[:limit]
    except Exception as e:
        print(f'Błąd: {e}')
        return []

def ostatnio_modyfikowane_pulpit():
    sciezka_katalogu = os.path.join(os.path.expanduser('~'), 'Desktop')
    print('Ostatnio zmodyfikowane pliki na pulpicie:')
    try:
        pliki = ostatnio_modyfikowane(sciezka_katalogu, 10)
        for plik, data in pliki:
            print(f'    {plik} - {data}')
    except Exception as e:
        print(f"Błąd przy sprawdzaniu pulpitu: {e}")

def monitoruj_usb():
    try:
        c = wmi.WMI()
        urzadzenia_usb = c.Win32_PnPEntity(ConfigManagerErrorCode=0, Description='USB Mass Storage Device')
        identyfikatory_usb = {device.DeviceID: device.Description for device in urzadzenia_usb}
        print('Wszystkie podłączone urządzenia USB:')
        for id, opis in identyfikatory_usb.items():
            print(f'ID: {id}, Opis: {opis}')
        print("Funkcja monitorowania USB (BETA) - wyświetlono aktualne urządzenia")
    except Exception as e:
        print(f"Błąd przy monitorowaniu USB: {e}")

def check_vpn():
    try:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.status == 'ESTABLISHED':
                # Sprawdź typowe porty VPN
                if conn.laddr.port in [1194, 1723, 1701, 500, 4500]:
                    return '[red]Tak[/red]'
        return '[green]Nie[/green]'
    except Exception as e:
        return f'Błąd: {e}'

def get_location():
    try:
        g = geocoder.ip('me')
        if g.ok:
            return f'Kraj: {g.country}, Miasto: {g.city}'
        return 'Nie udało się uzyskać lokalizacji.'
    except Exception as e:
        return f'Błąd lokalizacji: {e}'

def get_ping():
    try:
        if platform.system().lower() == "windows":
            command = ['ping', '-n', '4', 'google.com']
        else:
            command = ['ping', '-c', '4', 'google.com']
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f'Błąd podczas sprawdzania ping: {e}'

def get_current_user():
    try:
        return getpass.getuser()
    except:
        return "Nieznany użytkownik"

def get_all_users():
    try:
        return [user.name for user in psutil.users()]
    except:
        return ["Błąd pobierania użytkowników"]

def get_boot_time():
    try:
        boot_time_timestamp = psutil.boot_time()
        boot_time = datetime.datetime.fromtimestamp(boot_time_timestamp)
        return boot_time.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "Błąd pobierania czasu rozruchu"

def get_system_uptime():
    try:
        czas_rozruchu = psutil.boot_time()
        teraz = datetime.datetime.now().timestamp()
        czas_dzialania_sekundy = teraz - czas_rozruchu
        czas_dzialania = datetime.timedelta(seconds=czas_dzialania_sekundy)
        return str(czas_dzialania)
    except:
        return "Błąd pobierania czasu działania"

def sprawdz_info():
    try:
        windows_version = platform.platform()
        current_user = get_current_user()
        all_users = get_all_users()
        boot_time = get_boot_time()
        czas_dzialania_systemu = get_system_uptime()
        vpn_status = check_vpn()
        location_info = get_location()
        ping_info = get_ping()
        
        print('VPN:', vpn_status)
        print(location_info)
        print('Aktualna wersja systemu Windows:', windows_version)
        print('Aktualnie zalogowany użytkownik:', current_user)
        print('Lista wszystkich użytkowników:', all_users)
        print('Czas uruchomienia komputera:', boot_time)
        print('Czas działania systemu:', czas_dzialania_systemu)
        print('Ping do google.com:')
        print(ping_info)
    except Exception as e:
        print(f"Błąd przy pobieraniu informacji systemowych: {e}")

def find_d3d10_dll():
    plugins_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'FiveM', 'FiveM.app', 'plugins')
    if os.path.exists(plugins_path):
        try:
            for file in os.listdir(plugins_path):
                if file.lower() == 'd3d10.dll':
                    return True
        except Exception as e:
            print(f"Błąd przy sprawdzaniu pluginów: {e}")
    return False

def find_gtav_files():
    typical_locations = [
        'C:\Program Files\\Rockstar Games\\Grand Theft Auto V',
        'C:\Program Files (x86)\\Rockstar Games\\Grand Theft Auto V', 
        'C:\Program Files\Epic Games\GTAV',
        'C:\Program Files (x86)\\Steam\\steamapps\\common\\Grand Theft Auto V',
        'D:\Steam\\steamapps\\common\\Grand Theft Auto V',
        'E:\Games\\Grand Theft Auto V'
    ]
    for location in typical_locations:
        if os.path.exists(location):
            return location
    return None

# Główna pętla programu
while True:
    try:
        wybor = input('Twój wybór: ')
        
        if wybor == '1':
            sciezka = find_gtav_files()
            if sciezka is None:
                sciezka = input('Nie znaleziono instalacji GTAV w typowych lokalizacjach. Podaj ścieżkę do folderu gry: ')
                if not os.path.exists(sciezka):
                    print('Podana ścieżka do GTA V jest nieprawidłowa. Spróbuj ponownie.')
                    continue
            loading_animation(0.4)
            print('\nSprawdzanie pliku imgui.ini...')
            sprawdz_imgui(sciezka)
            print('\nSprawdzanie katalogu kosza...')
            sprawdz_kosz()
            print('\nOtwieranie katalogów mods, citizen, historie i cache...')
            otworz_katalogi()
            print('\nSprawdzanie ostatnio zmodyfikowanych plików na pulpicie...')
            ostatnio_modyfikowane_pulpit()
            print('\nSprawdzanie informacji o systemie...')
            sprawdz_info()
            otworz_katalogi_i_wyslij_na_webhook(webhook_url)
            print('\nSprawdzanie pluginów...')
            if find_d3d10_dll():
                tytul = 'Wykryto cheaty!'
                tresc = f'Wykryto cheaty na komputerze {platform.node()}! Plik: **d3d10.dll**'
                kolor = 16711680
                wyslij_na_webhook_embed(tytul, tresc, kolor)
                print('[red]Wykryto plik d3d10.dll w lokalizacji plugins w FiveM. Obecność Cheatów![/red]')
                zapisz_do_cache('Wykryto cheaty')
            else:
                tytul = 'Nie wykryto cheatow!'
                tresc = f'Nie wykryto cheatow na komputerze {platform.node()}! **d3d10.dll checker**'
                kolor = 65280
                wyslij_na_webhook_embed(tytul, tresc, kolor)
                print('[green]Nie wykryto pliku d3d10.dll.[/green]')
                zapisz_do_cache('Gracz nie ma dll!')
                
        elif wybor == '2':
            sciezka = find_gtav_files()
            if sciezka is None:
                sciezka = input('Nie znaleziono instalacji GTAV w typowych lokalizacjach. Podaj ścieżkę do folderu gry: ')
                if not os.path.exists(sciezka):
                    print('Podana ścieżka do GTA V jest nieprawidłowa. Spróbuj ponownie.')
                    continue
            loading_animation(0.1)
            print('\nSprawdzanie pliku imgui.ini...')
            sprawdz_imgui(sciezka)
            print('\nSprawdzanie pluginów...')
            if find_d3d10_dll():
                tytul = 'Wykryto cheaty!'
                tresc = f'Wykryto cheaty na komputerze {platform.node()}! Plik: **d3d10.dll**'
                kolor = 16711680
                wyslij_na_webhook_embed(tytul, tresc, kolor)
                print('[red]Wykryto plik d3d10.dll w lokalizacji plugins w FiveM. Obecność Cheatów![/red]')
                zapisz_do_cache('Wykryto cheaty')
            else:
                tytul = 'Nie wykryto cheatow!'
                tresc = f'Nie wykryto cheatow na komputerze {platform.node()}! **d3d10.dll checker**'
                kolor = 65280
                wyslij_na_webhook_embed(tytul, tresc, kolor)
                print('[green]Nie wykryto pliku d3d10.dll.[/green]')
                zapisz_do_cache('Gracz nie ma dll!')
                
        elif wybor == '3':
            loading_animation(0.1)
            print('\nSprawdzanie katalogu kosza...')
            sprawdz_kosz()
            
        elif wybor == '4':
            loading_animation(0.1)
            print('\nOtwieranie katalogów mods, citizen, historie i cache...')
            otworz_katalogi()
            
        elif wybor == '5':
            loading_animation(0.1)
            print('\nSprawdzanie ostatnio zmodyfikowanych plików na pulpicie...')
            ostatnio_modyfikowane_pulpit()
            
        elif wybor == '6':
            loading_animation(0.1)
            print('\nSprawdzanie informacji o systemie...')
            sprawdz_info()
            
        elif wybor == '7':
            loading_animation(0.1)
            print('\nSprawdzanie pendrive...')
            monitoruj_usb()
            
        elif wybor == '8':
            print('Zamykanie programu...')
            break
            
        else:
            print('Nieprawidłowy wybór. Wybierz liczbę od 1 do 8.')
            
    except KeyboardInterrupt:
        print('\nProgram przerwany przez użytkownika.')
        break
    except Exception as e:
        print(f'Wystąpił nieoczekiwany błąd: {e}')