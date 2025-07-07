import platform
import subprocess
import requests
import getpass
import threading
import time

def ping_host(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=subprocess.DEVNULL) == 0

def login(server_url, username, password):
    try:
        response = requests.post(f"{server_url}/auth.php", data={
            "username": username,
            "password": password
        })
        return response.text.strip() == "success"
    except Exception as e:
        print("❌ Error contacting server:", e)
        return False

def send_heartbeat(server_url, username):
    def loop():
        while True:
            try:
                requests.post(f"{server_url}/heartbeat.php", json={"username": username})
            except Exception as e:
                print("⚠️ Heartbeat failed:", e)
            time.sleep(30)
    threading.Thread(target=loop, daemon=True).start()

def main():
    print("🔐 Server Login")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    server_host = input("Server address (without http://): ").strip()
    server_url = f"http://{server_host}"

    print("📡 Pinging server...")
    if ping_host(server_host):
        print("✅ Server is online.")
        if login(server_url, username, password):
            print(f"🔓 Login successful as '{username}'")
            send_heartbeat(server_url, username)
            print("💓 Heartbeat active. Press Ctrl+C to quit.")
            while True:
                time.sleep(60)
        else:
            print("❌ Login failed. Please check your credentials.")
    else:
        print("🚫 Server appears to be offline.")

if __name__ == "__main__":
    main()
