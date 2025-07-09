

import ntplib
import subprocess
import platform
from datetime import datetime

def get_ntp_time(server):
    """Query time from an NTP server."""
    try:
        client = ntplib.NTPClient()
        response = client.request(server, version=3, timeout=5)
        return datetime.fromtimestamp(response.tx_time)
    except Exception as e:
        print(f"  [!] Could not reach {server}: {e}")
        return None

def set_windows_time(ntp_time):
    """Set Windows system time using the time received from NTP."""
    try:
        date_str = ntp_time.strftime('%m-%d-%Y')
        time_str = ntp_time.strftime('%H:%M:%S')

        subprocess.run(f'date {date_str}', shell=True, check=True)
        subprocess.run(f'time {time_str}', shell=True, check=True)
        print("\n[✔] System time updated successfully.")
    except Exception as e:
        print(f"[!] Failed to update system time: {e}")

def main():
    if platform.system() != "Windows":
        print("✘ This script is designed for Windows only.")
        return

    print("=== MOBATIME NTP Client (Windows Time Sync) ===\n")
    
    # Get user input for up to 3 NTP servers
    servers = []
    for i in range(3):
        server = input(f"Enter NTP Server {i+1} (or press Enter to skip): ").strip()
        if server:
            servers.append(server)

    if not servers:
        print("✘ No servers provided. Exiting.")
        return

    # Try each server until one responds
    for server in servers:
        print(f"\n[•] Contacting NTP server: {server}")
        ntp_time = get_ntp_time(server)
        if ntp_time:
            print(f"  [✓] Time from {server}: {ntp_time}")
            set_windows_time(ntp_time)
            break
    else:
        print("\n✘ Could not get time from any of the provided NTP servers.")

if __name__ == "__main__":
    main()
