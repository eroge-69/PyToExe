import os
import time

def clear_logs():
    print("[*] czyszczenie event logów...")
    os.system("wevtutil cl Application")
    os.system("wevtutil cl Security")
    os.system("wevtutil cl System")
    print("[*] logi wyczyszczone")

def block_ports():
    print("[*] blokowanie podstawowych portów...")
    ports = [80, 443, 21, 22, 3389, 135, 139, 445]
    for port in ports:
        cmd = f'netsh advfirewall firewall add rule name="Blokada portu {port}" dir=in action=block protocol=TCP localport={port}'
        os.system(cmd)
        print(f"[+] port {port} zablokowany")
    print("[*] porty zablokowane")

def unblock_ports():
    print("[*] odblokowywanie portów...")
    ports = [80, 443, 21, 22, 3389, 135, 139, 445]
    for port in ports:
        cmd = f'netsh advfirewall firewall delete rule name="Blokada portu {port}" protocol=TCP localport={port}'
        os.system(cmd)
        print(f"[+] port {port} odblokowany")
    print("[*] porty odblokowane")

def stop_services():
    print("[*] wyłączanie usług, które mogą zdradzić...")
    services = ["wuauserv", "SysMain", "DiagTrack"]
    for service in services:
        os.system(f'net stop {service}')
        print(f"[+] usługa {service} zatrzymana")
    print("[*] usługi wyłączone")

def start_services():
    print("[*] uruchamianie usług ponownie...")
    services = ["wuauserv", "SysMain", "DiagTrack"]
    for service in services:
        os.system(f'net start {service}')
        print(f"[+] usługa {service} uruchomiona")
    print("[*] usługi uruchomione")

def print_banner():
    banner = """
██╗ ██████╗  ██████╗  ██████╗  ███╗   ██╗ ██████╗ 
██║██╔═══██╗██╔═══██╗██╔═══██╗████╗  ██║██╔════╝ 
██║██║   ██║██║   ██║██║   ██║██╔██╗ ██║██║  ███╗
██║██║   ██║██║   ██║██║   ██║██║╚██╗██║██║   ██║
██║╚██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝
╚═╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ 
    """
    print(banner)

def menu():
    print("""
Incognito Tool - wybierz opcję:
1. Zamknij porty + wyłącz usługi + wyczyść logi
2. Odblokuj porty + uruchom usługi
3. Wyjdź
""")

def main():
    print_banner()
    while True:
        menu()
        choice = input("Wybierz opcję: ").strip()
        if choice == "1":
            block_ports()
            stop_services()
            clear_logs()
            print("\nTryb incognito włączony\n")
            input("Naciśnij Enter, aby kontynuować...")
        elif choice == "2":
            unblock_ports()
            start_services()
            print("\nTryb incognito wyłączony\n")
            input("Naciśnij Enter, aby kontynuować...")
        elif choice == "3":
            print("Do zobaczenia!")
            break
        else:
            print("Niepoprawna opcja, spróbuj jeszcze raz.")

if __name__ == "__main__":
    main()
