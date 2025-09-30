import http.client
import ssl
import json
import time
import os
import winreg
from urllib.parse import urlencode
from colorama import Fore, init

init(autoreset=True)

CONFIG_FILE = "config.json"

# Registry path for Rec Room login lock
REG_PATH = r"Software\Against Gravity\Rec Room"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            "delay": 5,              # seconds between gift requests
            "auth_data": "",         # /connect/token body
            "gift_context": "1",     # default GiftContext
            "gift_message": "",      # default Message
            "lobby_hop": True,       # toggle Dodgeball matchmaking
            "lobby_hop_delay": 5     # delay before hopping (seconds)
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return config
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_login_lock_from_registry() -> str:
    """Finds any LoginLockTokenV2_* REG_BINARY in registry and extracts LockToken."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
            i = 0
            while True:
                try:
                    name, raw, vtype = winreg.EnumValue(key, i)
                    if name.startswith("LoginLockTokenV2_") and vtype == winreg.REG_BINARY:
                        data_bytes = raw if isinstance(raw, (bytes, bytearray)) else bytes(raw)
                        text = data_bytes.decode("utf-8", errors="ignore").strip("\x00")
                        js = json.loads(text)
                        return js.get("LockToken")
                    i += 1
                except OSError:
                    break
    except Exception as e:
        print(Fore.RED + f"[ERROR] Registry read failed: {e}")
    return None

def make_request(host, method, path, headers=None, body=None):
    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection(host, context=context, timeout=20)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        resp = conn.getresponse()
        data = resp.read().decode("utf-8", errors="ignore")
        return resp.status, data
    finally:
        conn.close()

def get_access_token(auth_data: str) -> str:
    host = "auth.epicquest.live"
    path = "/connect/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    status, data = make_request(host, "POST", path, headers=headers, body=auth_data)
    if status != 200:
        print(Fore.RED + f"[ERROR] Token request failed: {status} {data}")
        return None
    try:
        return json.loads(data).get("access_token")
    except Exception:
        print(Fore.RED + f"[ERROR] Could not parse token response: {data}")
        return None

def send_gift(access_token: str, gift_context: str, gift_message: str) -> (bool, str):
    host = "api.epicquest.live"
    path = "/api/avatar/v2/gifts/generate"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = urlencode({
        "GiftContext": gift_context,
        "Message": gift_message
    })
    status, data = make_request(host, "POST", path, headers=headers, body=body)

    if status == 200:
        return True, None
    elif status == 400:
        if "Daily limit reached." in data:
            return False, "DAILY_LIMIT"
        try:
            js = json.loads(data)
            if js.get("title") == "Bad Request":
                return False, "NOT_IN_RRO"
        except Exception:
            if "Rate limit exceeded" in data:
                return False, "RATE_LIMIT"
        return False, "BAD_REQUEST"
    else:
        return False, f"HTTP {status}: {data}"

def goto_dodgeball(access_token: str, login_lock: str):
    if not login_lock:
        print(Fore.YELLOW + "[WARN] Could not locate loginLock, skipping room hop.")
        return False

    host = "match.epicquest.live"
    path = "/goto/room/Dodgeball"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = urlencode({"loginLock": login_lock})
    status, data = make_request(host, "POST", path, headers=headers, body=body)

    if status == 200:
        print(Fore.CYAN + "[ROOM] Joined Dodgeball (public).")
        return True
    else:
        print(Fore.RED + f"[ROOM FAIL] {status} {data}")
        return False

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + "=== radeon giftbox nigger ===")

    config = load_config()
    delay = config.get("delay", 5)
    auth_data = config.get("auth_data", "")
    gift_context = config.get("gift_context", "1")
    gift_message = config.get("gift_message", "")
    lobby_hop = config.get("lobby_hop", True)
    lobby_hop_delay = config.get("lobby_hop_delay", 5)

    print(Fore.YELLOW + f"[CONFIG] Delay: {delay}s | GiftContext: {gift_context} | Message: '{gift_message}' | LobbyHop: {lobby_hop} | LobbyHopDelay: {lobby_hop_delay}s")

    if not auth_data:
        print(Fore.CYAN + "\nPaste your auth data (from Postman Body for /connect/token):")
        auth_data = input("> ").strip()
        if not auth_data:
            print(Fore.RED + "No auth data provided. Exiting.")
            return
        config["auth_data"] = auth_data
        save_config(config)
        print(Fore.GREEN + "[OK] Auth data saved to config.json.")

    print(Fore.CYAN + "[*] Requesting access token...")
    token = get_access_token(auth_data)
    if not token:
        return
    print(Fore.GREEN + "[OK] Access token retrieved.")

    success_count = 0
    last_refresh = time.time()

    try:
        while True:
            # refresh token every 30 minutes
            if time.time() - last_refresh >= 1800:
                print(Fore.CYAN + "[*] Refreshing access token...")
                token = get_access_token(auth_data)
                if token:
                    print(Fore.GREEN + "[OK] Token refreshed.")
                else:
                    print(Fore.RED + "[ERROR] Token refresh failed. Exiting.")
                    break
                last_refresh = time.time()

            ok, error = send_gift(token, gift_context, gift_message)
            if ok:
                success_count += 1
                print(Fore.GREEN + f"[SUCCESS] Gift sent! Total: {success_count}")
            else:
                if error == "DAILY_LIMIT":
                    print(Fore.RED + "[LIMIT] Daily gift limit reached. Please wait until tomorrow.")
                    break
                elif error == "NOT_IN_RRO":
                    print(Fore.RED + "[FAIL] You are not currently in a Rec Room Online session (RRO). Gifts cannot be sent.")
                elif error == "RATE_LIMIT":
                    print(Fore.YELLOW + "[RATE LIMIT] Too many requests. Edit config.json and increase the delay.")
                elif error == "BAD_REQUEST":
                    print(Fore.RED + "[FAIL] 400 Bad Request (unknown cause).")
                else:
                    print(Fore.RED + f"[ERROR] {error}")

            # Lobby hop toggle
            if lobby_hop:
                time.sleep(lobby_hop_delay)
                goto_dodgeball(token, get_login_lock_from_registry())

            # Wait the configured delay before the next gift
            time.sleep(delay)
    except KeyboardInterrupt:
        print(Fore.CYAN + "\n[EXIT] Stopped by user.")

if __name__ == "__main__":
    main()
