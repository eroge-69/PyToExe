#!/usr/bin/env python3
import sys
import subprocess
import importlib
import os
import platform
import psutil
import requests
from datetime import datetime
from getpass import getpass

REQUIRED = ("psutil", "requests")

def ensure_packages(pkgs):
    missing = []
    for p in pkgs:
        try:
            importlib.import_module(p)
        except ImportError:
            missing.append(p)
    if not missing:
        return True
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install packages: {e}")
        return False
    for p in missing:
        try:
            importlib.import_module(p)
        except ImportError:
            return False
    return True

if not ensure_packages(REQUIRED):
    print("[!] Could not ensure required packages. Exiting.")
    sys.exit(1)

# CONFIG
WEBHOOK_URL = "https://discord.com/api/webhooks/1416318798365065246/ybs0sO-9xLMkUZQTk9to0GFt7YP2ZNlL5w_3HUugE4mvcCEXeeipV6KH1YLAwb5SAIwg"
DRY_RUN = True
ALLOW_MODIFICATIONS = False

SUSPECT_NAMES = [
    "solara", "bootstrapper", "boostrapper", "jjsp", "jjssploit",
    "xeno", "xen0", "injector", "synapse", "krnl", "fluxus"
]
SUSPECT_FILENAMES = [
    "solara.exe", "bootstrapper.exe", "bootstrappernew.exe", "injector.exe",
    "jjssploit.exe", "xeno.exe", "synapse.exe", "krnl.exe", "fluxus.exe"
]
SUSPECT_URLS = ["wearedevs", "wearedevs.net", "pluto", "solara", "jjssploit", "xeno"]
SEARCH_PATHS = [
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.join(os.path.expanduser("~"), "AppData", "Local"),
    os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
]
MAX_FILES_TO_SCAN = 1500
MAX_FILE_DEPTH = 4
MAX_MATCHES_PER_CATEGORY = 30
PREFETCH_DIR = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Prefetch")

def is_windows():
    return platform.system().lower().startswith("win")

def detect_active_executors(suspect_names):
    matches = []
    lowered = [s.lower() for s in suspect_names]
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            name = (proc.info.get('name') or "").lower()
            exe = (proc.info.get('exe') or "").lower()
            cmd = " ".join(proc.info.get('cmdline') or []).lower()
            combined = " ".join([name, exe, cmd])
            for cand in lowered:
                if cand in combined:
                    matches.append((proc.info.get('pid'), proc.info.get('name') or proc.info.get('exe') or "unknown"))
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if len(matches) >= MAX_MATCHES_PER_CATEGORY:
            break
    return matches[:MAX_MATCHES_PER_CATEGORY]

def search_files_for_names(paths, filenames, max_depth=MAX_FILE_DEPTH, max_files=MAX_FILES_TO_SCAN):
    matches = []
    filenames_lower = [f.lower() for f in filenames]
    files_scanned = 0
    def walk(path, depth):
        nonlocal files_scanned, matches
        if files_scanned >= max_files or len(matches) >= MAX_MATCHES_PER_CATEGORY:
            return
        if depth < 0:
            return
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if files_scanned >= max_files or len(matches) >= MAX_MATCHES_PER_CATEGORY:
                        break
                    try:
                        if entry.is_file(follow_symlinks=False):
                            files_scanned += 1
                            name = entry.name.lower()
                            for cand in filenames_lower:
                                if cand in name:
                                    matches.append(os.path.abspath(entry.path))
                                    break
                        elif entry.is_dir(follow_symlinks=False):
                            lowp = entry.path.lower()
                            if "node_modules" in lowp or ".git" in lowp:
                                continue
                            walk(entry.path, depth-1)
                    except PermissionError:
                        continue
        except (PermissionError, FileNotFoundError):
            return
    for p in paths:
        if p and os.path.isdir(p):
            walk(p, max_depth)
            if len(matches) >= MAX_MATCHES_PER_CATEGORY or files_scanned >= max_files:
                break
    return matches

def prefetch_matches(suspect_names):
    result = []
    if not is_windows() or not os.path.isdir(PREFETCH_DIR):
        return result
    try:
        for fname in os.listdir(PREFETCH_DIR):
            fl = fname.lower()
            for cand in suspect_names:
                if cand in fl:
                    result.append(os.path.join(PREFETCH_DIR, fname))
                    break
            if len(result) >= MAX_MATCHES_PER_CATEGORY:
                break
    except Exception:
        pass
    return result

def registry_uninstall_matches(suspect_names):
    result = []
    if not is_windows():
        return result
    try:
        import winreg
    except Exception:
        return result
    keys_to_check = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    lowered = [s.lower() for s in suspect_names]
    for root, sub in keys_to_check:
        try:
            with winreg.OpenKey(root, sub) as k:
                for i in range(0, 5000):
                    try:
                        sk = winreg.EnumKey(k, i)
                        with winreg.OpenKey(k, sk) as skk:
                            try:
                                display = winreg.QueryValueEx(skk, "DisplayName")[0].lower()
                            except Exception:
                                display = ""
                            try:
                                uninstall = winreg.QueryValueEx(skk, "UninstallString")[0].lower()
                            except Exception:
                                uninstall = ""
                            combined = display + " " + uninstall
                            for cand in lowered:
                                if cand in combined:
                                    result.append(f"{display or sk} -> {uninstall or 'no uninstall string'}")
                                    break
                    except OSError:
                        break
                    if len(result) >= MAX_MATCHES_PER_CATEGORY:
                        break
        except Exception:
            continue
    return result

def scan_for_url_indicators(paths, url_indicators, max_files=500, max_results=30):
    results = []
    text_exts = {'.txt', '.log', '.json', '.cfg', '.ini', '.md', '.html'}
    files_scanned = 0
    lowered_ind = [u.lower() for u in url_indicators]
    for p in paths:
        if files_scanned >= max_files or len(results) >= max_results:
            break
        if not os.path.isdir(p):
            continue
        for root, dirs, files in os.walk(p):
            if root.count(os.sep) - p.count(os.sep) > MAX_FILE_DEPTH:
                continue
            for fname in files:
                if files_scanned >= max_files or len(results) >= max_results:
                    break
                ext = os.path.splitext(fname)[1].lower()
                if ext not in text_exts:
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', errors='ignore', encoding='utf-8') as fh:
                        content = fh.read(100000)
                        files_scanned += 1
                        lowerc = content.lower()
                        for ind in lowered_ind:
                            if ind in lowerc:
                                results.append(f"{ind} found in {fpath}")
                                break
                except Exception:
                    continue
            if files_scanned >= max_files or len(results) >= max_results:
                break
    return results

def determine_risk(active, files, reg, prefetch, browser_traces):
    score = 0
    if active:
        score += 3
    score += min(len(files), 3)
    score += min(len(reg), 2)
    score += min(len(prefetch), 2)
    score += min(len(browser_traces), 1)
    if score >= 5:
        return "High Risk"
    if score >= 2:
        return "Medium Risk"
    return "Low Risk"

def build_embed_payload(node_name, risk, active, files, reg, prefetch, browser_traces, scanned_paths):
    fields = []
    fields.append({"name": "Risk", "value": risk, "inline": False})
    fields.append({"name": "Active Executors", "value": "\n".join([f"PID {p} — {n}" for p,n in active]) if active else "None", "inline": False})
    fields.append({"name": "Found Files", "value": "\n".join(files[:10]) if files else "None", "inline": False})
    fields.append({"name": "Registry Traces", "value": "\n".join(reg[:6]) if reg else "None", "inline": False})
    fields.append({"name": "Prefetch Traces", "value": "\n".join(prefetch[:8]) if prefetch else "None", "inline": False})
    fields.append({"name": "Browser Traces (file matches)", "value": "\n".join(browser_traces[:6]) if browser_traces else "None", "inline": False})
    scanned = [p for p in scanned_paths if p and os.path.isdir(p)]
    scanned_str = ", ".join(scanned[:4]) if scanned else "N/A"
    embed = {
        "title": "PC SCAN RESULT",
        "description": f"Node: {node_name}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields": fields,
        "footer": {"text": f"Scanned: {scanned_str} • DRY_RUN={DRY_RUN}"}
    }
    return embed

def send_embed(webhook_url, payload, username=None, avatar_url=None):
    data = {"embeds": [payload]}
    if username:
        data["username"] = username
    if avatar_url:
        data["avatar_url"] = avatar_url
    try:
        r = requests.post(webhook_url, json=data, timeout=15)
        if r.status_code in (200, 204):
            print("[+] Sent embed to webhook.")
        else:
            print(f"[!] Failed to send embed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[!] Error sending webhook: {e}")

def scanner_main():
    print("[*] Running scanner...")
    node = platform.node()
    active = detect_active_executors(SUSPECT_NAMES)
    files_found = search_files_for_names(SEARCH_PATHS, SUSPECT_FILENAMES)
    reg_matches = registry_uninstall_matches(SUSPECT_NAMES) if is_windows() else []
    prefetch = prefetch_matches(SUSPECT_NAMES) if is_windows() else []
    browser_traces = scan_for_url_indicators(SEARCH_PATHS, SUSPECT_URLS)
    risk = determine_risk(active, files_found, reg_matches, prefetch, browser_traces)
    embed_payload = build_embed_payload(node, risk, active, files_found, reg_matches, prefetch, browser_traces, SEARCH_PATHS)
    if not WEBHOOK_URL or "your_webhook" in WEBHOOK_URL:
        print("RISK:", risk)
        print("Active:", active)
        print("Files Found:", files_found[:20])
        print("Registry:", reg_matches[:20])
        print("Prefetch:", prefetch[:20])
        print("Browser traces:", browser_traces[:20])
    else:
        send_embed(WEBHOOK_URL, embed_payload)
    print("[*] Scanner complete.")
    return {
        "risk": risk,
        "active": active,
        "files_found": files_found,
        "registry": reg_matches,
        "prefetch": prefetch,
        "browser_traces": browser_traces
    }

def _safe_kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=3)
        return True
    except Exception:
        return False

def _delete_file(path):
    try:
        os.remove(path)
        return True
    except Exception:
        return False

def _delete_prefetch(path):
    return _delete_file(path)

def _delete_registry_uninstall_entries_by_name(names):
    if not is_windows():
        return []
    results = []
    try:
        import winreg
    except Exception:
        return results
    keys_to_check = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    lowered = [n.lower() for n in names]
    for root, sub in keys_to_check:
        try:
            with winreg.OpenKey(root, sub, 0, winreg.KEY_READ | winreg.KEY_WRITE) as k:
                i = 0
                to_delete = []
                while True:
                    try:
                        sk = winreg.EnumKey(k, i)
                        with winreg.OpenKey(k, sk) as skk:
                            try:
                                display = (winreg.QueryValueEx(skk, "DisplayName")[0] or "").lower()
                            except Exception:
                                display = ""
                            try:
                                uninstall = (winreg.QueryValueEx(skk, "UninstallString")[0] or "").lower()
                            except Exception:
                                uninstall = ""
                            combined = display + " " + uninstall
                            for cand in lowered:
                                if cand in combined:
                                    to_delete.append(sk)
                                    break
                        i += 1
                    except OSError:
                        break
                for subkey in to_delete:
                    try:
                        if not DRY_RUN and ALLOW_MODIFICATIONS:
                            winreg.DeleteKey(k, subkey)
                            results.append((subkey, "deleted"))
                        else:
                            results.append((subkey, "would delete"))
                    except Exception as e:
                        results.append((subkey, f"failed: {e}"))
        except Exception:
            continue
    return results

def cleaner_main(scan_results):
    files = scan_results.get("files_found", [])
    active = scan_results.get("active", [])
    prefetch = scan_results.get("prefetch", [])
    registry = scan_results.get("registry", [])
    print("[*] Cleaner (DRY_RUN = {})".format(DRY_RUN))
    print("Detected active executors:")
    for pid, name in active:
        print(f"  PID {pid} — {name}")
    print("Detected files:")
    for f in files[:50]:
        print(f"  {f}")
    print("Detected prefetch entries:")
    for p in prefetch[:50]:
        print(f"  {p}")
    print("Detected registry traces:")
    for r in registry[:50]:
        print(f"  {r}")

    if DRY_RUN:
        print("\n[!] Running in DRY_RUN mode. No changes will be made.")
    if not ALLOW_MODIFICATIONS:
        print("[!] ALLOW_MODIFICATIONS is False. Cleaner will not perform destructive actions.")
    if not (ALLOW_MODIFICATIONS and not DRY_RUN):
        print("[*] To perform actual cleanup: set ALLOW_MODIFICATIONS=True in the script and restart, then choose CLEANER and confirm.")
        return

    token = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    print("\nCONFIRMATION REQUIRED")
    print(f"Type the confirmation token to proceed with destructive actions: {token}")
    typed = input("Token: ").strip()
    if typed != token:
        print("[!] Confirmation token mismatch. Aborting clean operation.")
        return

    print("[*] Proceeding with cleanup actions...")

    for pid, name in active:
        try:
            if not DRY_RUN:
                _safe_kill_process(pid)
                print(f"[+] Terminated PID {pid} ({name})")
            else:
                print(f"[DRY] Would terminate PID {pid} ({name})")
        except Exception as e:
            print(f"[!] Error terminating PID {pid}: {e}")

    for f in files:
        if os.path.isfile(f):
            if not DRY_RUN:
                ok = _delete_file(f)
                print(f"[+] Deleted file: {f}" if ok else f"[!] Failed to delete file: {f}")
            else:
                print(f"[DRY] Would delete file: {f}")

    for p in prefetch:
        if os.path.isfile(p):
            if not DRY_RUN:
                ok = _delete_prefetch(p)
                print(f"[+] Deleted prefetch: {p}" if ok else f"[!] Failed to delete prefetch: {p}")
            else:
                print(f"[DRY] Would delete prefetch: {p}")

    reg_names = [r.split(" -> ")[0] if " -> " in r else r for r in registry]
    reg_results = _delete_registry_uninstall_entries_by_name(reg_names)
    for rr in reg_results:
        print(f"[REG] {rr[0]} -> {rr[1]}")

    print("[*] Clean complete.")

def ascii_title():
    print(r"""
 █████  ██████  ██   ██     ███████  ██████  █████  ███    ██ ███    ██ ███████ ██████  
██   ██ ██   ██ ██  ██      ██      ██      ██   ██ ████   ██ ████   ██ ██      ██   ██ 
███████ ██████  █████       ███████ ██      ███████ ██ ██  ██ ██ ██  ██ █████   ██████  
██   ██ ██   ██ ██  ██           ██ ██      ██   ██ ██  ██ ██ ██  ██ ██ ██      ██   ██ 
██   ██ ██   ██ ██   ██     ███████  ██████ ██   ██ ██   ████ ██   ████ ███████ ██   ██ 
                                                                                        
                                                                                        """)

def menu():
    ascii_title()
    print("1 > SCANNER")
    print("2 > CLEANER")
    print("q > QUIT")
    return input("Choose option: ").strip().lower()

def main():
    choice = menu()
    if choice == "1":
        scan_results = scanner_main()
    elif choice == "2":
        scan_results = scanner_main()
        cleaner_main(scan_results)
    else:
        print("Exiting.")
        return

if __name__ == "__main__":
    main()
