import subprocess
from datetime import datetime
LOG_FILE = "dhcp_log.txt"

def log_action(message):
    """Записывает сообщение в лог с отметкой времени."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} — {message}\n")

def get_active_adapters():
    """Возвращает список только активных (подключённых) сетевых адаптеров."""
    result = subprocess.run(
        ["netsh", "interface", "show", "interface"],
        capture_output=True, text=True, encoding="cp866"
    )
    adapters = []
    for line in result.stdout.splitlines():
        # Пример строки: "Подключено    Выкл.     Ethernet        Ethernet 1"
        if "Подключено" in line and not "Отключено" in line:
            parts = line.split()
            adapter_name = " ".join(parts[3:])
            adapters.append(adapter_name)
    return adapters

def check_dhcp(adapter_name):
    """Проверяет, включен ли DHCP для адаптера."""
    result = subprocess.run(
        ["netsh", "interface", "ipv4", "show", "config", f"name={adapter_name}"],
        capture_output=True, text=True, encoding="cp866"
    )
    return "DHCP включен" in result.stdout

def enable_dhcp(adapter_name):
    """Включает автоматическое получение IP и DNS."""
    subprocess.run(
        ["netsh", "interface", "ipv4", "set", "address", f"name={adapter_name}", "source=dhcp"],
        capture_output=True, text=True, encoding="cp866"
    )
    subprocess.run(
        ["netsh", "interface", "ipv4", "set", "dnsservers", f"name={adapter_name}", "source=dhcp"],
        capture_output=True, text=True, encoding="cp866"
    )
    log_action(f"DHCP включен для адаптера: {adapter_name}")
    print(f"[+] DHCP включен для адаптера: {adapter_name}")

if __name__ == "__main__":
    adapters = get_active_adapters()
    if not adapters:
        print("Нет активных сетевых адаптеров.")
        log_action("Нет активных сетевых адаптеров.")
    else:
        for adapter in adapters:
            if check_dhcp(adapter):
                print(f"[OK] {adapter}: DHCP уже включен")
                log_action(f"{adapter}: DHCP уже включен")
            else:
                print(f"[!] {adapter}: DHCP выключен — включаем...")
                log_action(f"{adapter}: DHCP был выключен — включаем")
                enable_dhcp(adapter)
