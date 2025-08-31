import os
import subprocess
import time

# --- CONFIG ---
BLOCKED_PROCESSES = ["CapCutUpdate.exe", "CapCutService.exe"]
BLOCKED_SERVICES = ["CapCutUpdate", "CapCutService"]
BLOCKED_DOMAINS = [
    "update.capcut.com",
    "service.capcut.com",
    "download.capcut.com"
]
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT = "127.0.0.1"


def banner(): 
    title=rf"""

    ██████╗░░░░░░░░█████╗░░█████╗░██████╗░
    ██╔══██╗░░░░░░██╔══██╗██╔══██╗██╔══██╗
    ██████╦╝█████╗██║░░╚═╝███████║██████╔╝
    ██╔══██╗╚════╝██║░░██╗██╔══██║██╔═══╝░
    ██████╦╝░░░░░░╚█████╔╝██║░░██║██║░░░░░
    ╚═════╝░░░░░░░░╚════╝░╚═╝░░╚═╝╚═╝░░░░░

     B-CAP tool | Author: Chamnan dev | (c) 2025
    """

    print(title)


def disable_services():
    print("[*] Disabling CapCut services...")
    for s in BLOCKED_SERVICES:
        try:
            subprocess.run(["sc", "stop", s], shell=True)
            subprocess.run(["sc", "config", s, "start=", "disabled"], shell=True)
            print(f"[+] Disabled service: {s}")
        except Exception as e:
            print(f"[-] Failed to disable {s}: {e}")


def block_domains():
    print("[*] Blocking update domains in HOSTS file...")
    try:
        with open(HOSTS_PATH, "r+", encoding="utf-8") as file:
            content = file.read()
            for domain in BLOCKED_DOMAINS:
                entry = f"{REDIRECT} {domain}"
                if entry not in content:
                    file.write("\n" + entry)
                    print(f"[+] Blocked domain: {domain}")
    except PermissionError:
        print("[-] Permission denied! Run this script as Administrator.")
    except Exception as e:
        print(f"[-] Error editing hosts file: {e}")


def kill_updater_loop():
    print("[*] Starting updater killer loop...")
    while True:
        for proc in BLOCKED_PROCESSES:
            try:
                subprocess.call(f"taskkill /F /IM {proc}", shell=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        time.sleep(10)


if __name__ == "__main__":
    banner()
    disable_services()
    block_domains()
    kill_updater_loop()
    print("Tool running completed")

