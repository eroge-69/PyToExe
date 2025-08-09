import secrets
import string
import webview
import threading
import time
import os
import subprocess
import sys
import ctypes
from colorama import Fore, Style, init

# Initialize colorama for colorful console
init(autoreset=True)

# --- CONFIGURATION ---
CONFIG = {
    "WIREGUARD_CONF_PATH": r"C:\\Users\\Admin\\Downloads\\wgcf\\wgcf-profile.conf",
    "VPN_STABILIZE_SECONDS": 1,
    "ACCOUNTS_PER_VPN_CYCLE": 3,
    "RANDOM_STRING_LENGTH": 9,
    "ALT_CREATION_TIMEOUT": 30,  # Max seconds to wait per alt
    "PAGE_LOAD_SETTLE_SECONDS": 1,
    "OUTPUT_FILENAME": "accounts.txt",
    "HEADLESS_MODE": True
}
# --- END CONFIGURATION ---

RESTART_SESSION = False
SESSION_SUCCESSFUL = False
SESSION_COUNT = 0


def require_admin():
    """Restart the script with admin rights if not already elevated."""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return
    except:
        pass
    print(Fore.YELLOW + "[!] Restarting script as administrator...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()


def run_wireguard_command(command):
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError:
        return False


def connect_vpn():
    run_wireguard_command("wireguard /uninstalltunnelservice wgcf-profile")
    time.sleep(1)

    conf_path = CONFIG["WIREGUARD_CONF_PATH"]
    if not os.path.exists(conf_path):
        print(Fore.RED + f"[FATAL] WireGuard config not found at {conf_path}")
        sys.exit(1)

    if run_wireguard_command(f'wireguard /installtunnelservice "{conf_path}"'):
        print(Fore.CYAN + "[VPN] Connected.")
        time.sleep(CONFIG['VPN_STABILIZE_SECONDS'])
    else:
        print(Fore.RED + "[VPN] Failed to connect.")
        sys.exit(1)


def disconnect_vpn():
    run_wireguard_command("wireguard /uninstalltunnelservice wgcf-profile")
    print(Fore.CYAN + "[VPN] Disconnected.")


def generate_two_strings():
    chars = string.ascii_letters + string.digits
    length = CONFIG["RANDOM_STRING_LENGTH"]
    return (
        ''.join(secrets.choice(chars) for _ in range(length)),
        ''.join(secrets.choice(chars) for _ in range(length))
    )


def get_total_accounts_in_file():
    if not os.path.exists(CONFIG["OUTPUT_FILENAME"]):
        return 0
    with open(CONFIG["OUTPUT_FILENAME"], 'r') as f:
        return sum(1 for _ in f)


def save_account_to_file(username, password):
    try:
        with open(CONFIG["OUTPUT_FILENAME"], 'a') as f:
            f.write(f"{username}:{password}\n")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Could not save account: {e}")


def run_automation_logic(window):
    global SESSION_SUCCESSFUL, SESSION_COUNT
    username, password = generate_two_strings()
    start_time = time.time()

    js_code = f"""
        (function() {{
            function waitForPageAndElement(callback) {{
                let attempts = 0;
                const interval = setInterval(() => {{
                    attempts++;
                    if (document.readyState === 'complete' && document.body) {{
                        const u = document.getElementById('signup-username');
                        const p = document.getElementById('signup-password');
                        const b = document.getElementById('signup-button');
                        if (u && p && b) {{
                            clearInterval(interval);
                            callback(u, p, b);
                        }}
                    }}
                }}, 200);
            }}

            waitForPageAndElement((usernameInput, passwordInput, signUpButton) => {{
                function setNativeValue(el, val) {{
                    const valueSetter = Object.getOwnPropertyDescriptor(el, 'value').set;
                    const prototype = Object.getPrototypeOf(el);
                    const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
                    if (valueSetter && valueSetter !== prototypeValueSetter) {{
                        prototypeValueSetter.call(el, val);
                    }} else {{
                        valueSetter.call(el, val);
                    }}
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}

                function setSelect(id, value) {{
                    const el = document.getElementById(id);
                    if (el) {{
                        el.value = value;
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}

                setSelect('MonthDropdown', 'Jan');
                setSelect('DayDropdown', '25');
                setSelect('YearDropdown', '2005');
                setNativeValue(usernameInput, '{username}');
                setNativeValue(passwordInput, '{password}');
                signUpButton.click();
            }});
        }})();
    """
    window.evaluate_js(js_code)

    while time.time() - start_time < CONFIG["ALT_CREATION_TIMEOUT"]:
        time.sleep(0.2)
        current_url = window.get_current_url()
        if current_url and 'roblox.com/home' in current_url:
            SESSION_SUCCESSFUL = True
            save_account_to_file(username, password)
            SESSION_COUNT += 1
            total_in_file = get_total_accounts_in_file()

            print(Fore.GREEN + f"[SUCCESS] Generated account: {username}")
            print(Fore.MAGENTA + f"          Total this session: {SESSION_COUNT}")
            print(Fore.MAGENTA + f"          Total in file: {total_in_file}\n")

            trigger_restart(window)
            return

    print(Fore.RED + "[TIMEOUT] Took longer than 30 seconds — restarting cycle.")
    trigger_restart(window)


def on_page_load(window):
    time.sleep(CONFIG["PAGE_LOAD_SETTLE_SECONDS"])
    threading.Thread(target=run_automation_logic, args=(window,), daemon=True).start()


def trigger_restart(window):
    global RESTART_SESSION
    if not RESTART_SESSION:
        RESTART_SESSION = True
        if window:
            window.destroy()


def run_single_session():
    global RESTART_SESSION, SESSION_SUCCESSFUL
    RESTART_SESSION = False
    SESSION_SUCCESSFUL = False

    window = webview.create_window(
        'Roblox',
        'https://www.roblox.com',
        width=400,
        height=600,
        hidden=CONFIG["HEADLESS_MODE"]
    )
    window.events.loaded += lambda: on_page_load(window)
    webview.start(storage_path=None)


if __name__ == '__main__':
    require_admin()
    try:
        while True:
            connect_vpn()
            successful_runs = 0
            while successful_runs < CONFIG["ACCOUNTS_PER_VPN_CYCLE"]:
                run_single_session()
                if SESSION_SUCCESSFUL:
                    successful_runs += 1
                if RESTART_SESSION:
                    time.sleep(1)
                else:
                    disconnect_vpn()
                    sys.exit(0)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[EXIT] Stopping script...")
    finally:
        disconnect_vpn()
