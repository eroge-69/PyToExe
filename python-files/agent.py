import platform
import subprocess
import sys
import os
import logging
import time

# Try importing requests, install if not present
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import json

# ---------------------------
# CONFIG
# ---------------------------
BACKEND_API_URL = "https://snowagent.free.beeceptor.com"
LOG_FILE = "agent.log"
COLLECTION_INTERVAL = 300  # seconds (1 hour)

# ---------------------------
# LOGGING SETUP
# ---------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger()

# ---------------------------
# SYSTEM INFO COLLECTION
# ---------------------------
def get_installed_software_windows():
    import winreg
    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    software_list = []

    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for key_path in uninstall_keys:
            try:
                key = winreg.OpenKey(root, key_path)
            except FileNotFoundError:
                continue

            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)

                    try:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    except FileNotFoundError:
                        continue

                    try:
                        display_version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                    except FileNotFoundError:
                        display_version = "Unknown"

                    software_list.append({
                        "name": display_name,
                        "version": display_version
                    })

                except Exception as e:
                    logger.error(f"Error reading registry subkey: {e}")

    return software_list

def get_installed_software_mac():
    try:
        output = subprocess.check_output(
            ["system_profiler", "SPApplicationsDataType", "-json"],
            text=True
        )
        apps = json.loads(output)
        software_list = [
            {"name": app.get("name"), "version": app.get("version", "Unknown")}
            for app in apps.get("SPApplicationsDataType", [])
        ]
        return software_list
    except Exception as e:
        logger.error(f"Error getting installed software on macOS: {e}")
        return []

def get_installed_software_linux():
    software_list = []
    try:
        output = subprocess.check_output(
            ["dpkg-query", "-W", "-f=${binary:Package} ${Version}\n"],
            text=True
        )
        for line in output.strip().split("\n"):
            name, version = line.split(" ", 1)
            software_list.append({"name": name, "version": version})
    except Exception:
        try:
            output = subprocess.check_output(
                ["rpm", "-qa", "--queryformat", "%{NAME} %{VERSION}\n"],
                text=True
            )
            for line in output.strip().split("\n"):
                name, version = line.split(" ", 1)
                software_list.append({"name": name, "version": version})
        except Exception as e:
            logger.error(f"Error getting installed software on Linux: {e}")

    return software_list

def collect_system_info():
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "hostname": platform.node()
    }

# ---------------------------
# SEND DATA
# ---------------------------
def send_data_to_backend(data):
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(BACKEND_API_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            logger.info("Data sent successfully.")
        else:
            logger.warning(f"Failed to send  HTTP {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error sending data to backend: {e}")

# ---------------------------
# MAIN LOOP (Background Service)
# ---------------------------
def run_agent():
    logger.info("Agent started and running as background service.")

    while True:
        try:
            system_info = collect_system_info()
            platform_type = system_info["platform"]

            if platform_type == "Windows":
                software_list = get_installed_software_windows()
            elif platform_type == "Darwin":
                software_list = get_installed_software_mac()
            elif platform_type == "Linux":
                software_list = get_installed_software_linux()
            else:
                logger.error(f"Unsupported platform: {platform_type}")
                software_list = []

            data = {
                "system_info": system_info,
                "installed_software": software_list
            }

            logger.info(f"Collected {len(software_list)} software entries.")
            send_data_to_backend(data)

        except Exception as e:
            logger.error(f"Unhandled error in main loop: {e}")

        time.sleep(COLLECTION_INTERVAL)

if __name__ == "__main__":
    try:
        run_agent()
    except KeyboardInterrupt:
        logger.info("Agent stopped by user.")
    except Exception as e:
        logger.critical(f"Agent crashed: {e}")
