import itertools
import string
import subprocess

def scan_wifi_networks():
    """Scan and return a list of available Wi-Fi SSIDs on Windows."""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        ssids = []
        for line in lines:
            line = line.strip()
            if line.startswith("SSID ") and " :" in line:
                ssid = line.split(":", 1)[1].strip()
                if ssid and ssid not in ssids:
                    ssids.append(ssid)
        return ssids
    except subprocess.CalledProcessError as e:
        print(f"Error scanning Wi-Fi networks: {e}")
        return []

def password_finder(target_password, min_length=8, max_length=16, charset=None):
    """Brute-force attempt to find the target password."""
    if charset is None:
        charset = string.ascii_letters + string.digits + string.punctuation

    print(f"Starting password search for target: '{target_password}'")
    for length in range(min_length, max_length + 1):
        print(f"Trying passwords of length {length}...")
        for combo in itertools.product(charset, repeat=length):
            candidate = ''.join(combo)
            if candidate == target_password:
                print(f"Password found: {candidate}")
                return candidate
    print("Password not found in given range.")
    return None

def connect_to_network(ssid, password):
    """Create Wi-Fi profile and connect to the network using Windows netsh commands."""
    print(f"Attempting to connect to network '{ssid}' with password '{password}'")

    wifi_profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""

    profile_name = f"{ssid}.xml"
    with open(profile_name, 'w') as file:
        file.write(wifi_profile)

    try:
        subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={profile_name}'], check=True)
        subprocess.run(['netsh', 'wlan', 'connect', ssid], check=True)
        print(f"Connection command sent for SSID: {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect: {e}")

    # Optionally delete the profile file after use
    # import os
    # os.remove(profile_name)

def main():
    print("Scanning for available Wi-Fi networks...")
    networks = scan_wifi_networks()

    if not networks:
        print("No Wi-Fi networks found.")
        return

    print("\nAvailable Wi-Fi Networks:")
    for i, ssid in enumerate(networks, 1):
        print(f"{i}. {ssid}")

    # User selects a network by number
    while True:
        try:
            choice = int(input(f"\nChoose a network to attack (1-{len(networks)}): "))
            if 1 <= choice <= len(networks):
                selected_ssid = networks[choice - 1]
                break
            else:
                print("Invalid choice, try again.")
        except ValueError:
            print("Please enter a valid number.")

    print(f"\nYou selected: {selected_ssid}")

    # For demonstration, you must specify the target password here
    # In a real brute-force scenario, you don't know it beforehand
    target_password = input("Enter the target password to find (for demo): ")

    found_password = password_finder(target_password)
    if found_password:
        connect_to_network(selected_ssid, found_password)
    else:
        print("Failed to find the password.")

if __name__ == "__main__":
    main()
