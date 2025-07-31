import ipaddress
from ping3 import ping
import concurrent.futures

# Список филиалов и их IP-диапазоны
branches = {
    "1": {"name": "Филиал 1", "range": "10.105.45.1-255"},
    "2": {"name": "Филиал 2", "range": "10.105.50.1-255"},
    "3": {"name": "Филиал 3", "range": "10.103.154.1-255"},
    "4": {"name": "Филиал 4", "range": "10.106.23.1-255"},
    "5": {"name": "Филиал 5", "range": "10.109.218.1-255"},
    "6": {"name": "Филиал 6", "range": "10.105.21.1-255"},
    "7": {"name": "Филиал 7", "range": "10.105.77.1-255"},
}


def generate_ips(ip_range):
    base = ".".join(ip_range.split(".")[:3])
    return [f"{base}.{i}" for i in range(1, 256)]


def ping_ip(ip):
    if ping(ip, timeout=1):
        return f"[+] {ip} - доступен"
    else:
        return f"[-] {ip} - недоступен"


def scan_range(ip_range):
    ip_list = generate_ips(ip_range)
    print(f"\nСканирование сети {ip_range}...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(ping_ip, ip_list)

    for result in results:
        print(result)


def main():
    print("Выберите филиал:\n")
    for key, info in branches.items():
        print(f"{key}. {info['name']}")

    choice = input("\nВведите номер филиала: ").strip()

    if choice in branches:
        ip_range = branches[choice]['range']
        scan_range(ip_range)
    else:
        print("Неверный выбор. Завершение.")


if __name__ == "__main__":
    main()
