#!/usr/bin/env python3
# steam_cleaner.py — run this on the TARGET Windows PC
# Deletes Steam login/cache metadata after you log out / shut Steam down

import os, sys, time, shutil, glob, subprocess

def find_steam_base():
    """
    Detect Steam base using registry first, then common paths (incl. F:).
    Returns first existing dir or None.
    """
    reg_queries = [
        r'reg query "HKLM\SOFTWARE\WOW6432Node\Valve\Steam" /v InstallPath',
        r'reg query "HKLM\SOFTWARE\Valve\Steam" /v InstallPath',
        r'reg query "HKCU\Software\Valve\Steam" /v SteamPath',
    ]
    for q in reg_queries:
        try:
            out = subprocess.check_output(q, shell=True, text=True, stderr=subprocess.STDOUT)
            # parse last token as path
            parts = [p.strip() for p in out.splitlines() if "InstallPath" in p or "SteamPath" in p]
            if parts:
                p = parts[0].split()[-1]
                if os.path.isdir(p):
                    return p
        except Exception:
            pass

    # Fall back to common install locations (add/edit if needed)
    candidates = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        r"D:\Steam",
        r"D:\Program Files (x86)\Steam",
        r"D:\Program Files\Steam",
        r"E:\Steam",
        r"F:\Steam",
        # Some people keep Steam under a SteamLibrary root:
        r"F:\SteamLibrary\steam",
        r"E:\SteamLibrary\steam",
        r"D:\SteamLibrary\steam",
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    return None

def kill_steam():
    # best-effort stop
    try:
        subprocess.run('taskkill /F /IM steam.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def rm_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"[i] Deleted file: {path}")
    except Exception as e:
        print(f"[!] Failed to delete {path}: {e}")

def rm_tree(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
            print(f"[i] Deleted folder: {path}")
    except Exception as e:
        print(f"[!] Failed to delete {path}: {e}")

def clean_steam_metadata(base):
    """
    Remove login tokens & caches that keep you signed in.
    Safe set (what you asked for):
      - config\loginusers.vdf
      - ssfn* files in base
      - htmlcache\
      - appcache\httpcache\  (optional but useful)
    """
    config = os.path.join(base, "config")
    htmlcache = os.path.join(base, "htmlcache")
    appcache_http = os.path.join(base, "appcache", "httpcache")

    # loginusers.vdf
    rm_file(os.path.join(config, "loginusers.vdf"))

    # ssfn tokens in base
    for token in glob.glob(os.path.join(base, "ssfn*")):
        rm_file(token)

    # caches
    rm_tree(htmlcache)
    rm_tree(appcache_http)

def main():
    print("[i] SteamCleaner (Windows) starting…")

    base = find_steam_base()
    if not base:
        print("[!] Steam base not found in registry or standard paths.")
        sys.exit(2)

    print(f"[i] Steam base detected: {base}")

    # Ensure Steam is closed, give cloud a moment
    kill_steam()
    print("[i] Waiting 5s for Steam Cloud sync to settle…")
    time.sleep(5)

    clean_steam_metadata(base)
    print("[✓] Done.")

if __name__ == "__main__":
    main()
