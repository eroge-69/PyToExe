import os
import sqlite3
import shutil
import time
import tempfile
from datetime import datetime

CONFIG_FILE = "config.txt"

# ======== Utility ========

def load_config():
    config = {}
    current = None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
                config[current] = {}
            else:
                if "=" in line and current:
                    k, v = line.split("=", 1)
                    config[current][k.strip()] = os.path.expandvars(v.strip())
    return config

def copy_to_temp(path):
    """Copy file sang temp tru?c khi d?c (trnh lock)."""
    if not os.path.exists(path):
        return None
    temp_dir = tempfile.gettempdir()
    os.makedirs(temp_dir, exist_ok=True)
    tmpfile = os.path.join(temp_dir, f"history_copy_{int(time.time()*1000)}.db")
    try:
        shutil.copy2(path, tmpfile)
        return tmpfile
    except Exception as e:
        print(f"[!] Copy l?i {path}: {e}")
        return None

def firefox_time_to_chrome_time(firefox_time):
    """Chuy?n d?i th?i gian Firefox (s t? 1970) sang Chrome (s t? 1601)."""
    if not firefox_time:
        return 0
    EPOCH_DIFF_MICROS = 11644473600 * 1000000
    return firefox_time + EPOCH_DIFF_MICROS

# ======== Read history ========

def read_chrome_history(path):
    tmpfile = copy_to_temp(path)
    if not tmpfile:
        return []
    rows = []
    try:
        conn = sqlite3.connect(tmpfile)
        cur = conn.cursor()
        cur.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100")
        rows = cur.fetchall()
        conn.close()
    except Exception as e:
        print(f"[!] L?i d?c Chrome: {e}")
    finally:
        try: os.remove(tmpfile)
        except: pass
    return rows

def read_firefox_history(path):
    tmpfile = copy_to_temp(path)
    if not tmpfile:
        return []
    rows = []
    try:
        conn = sqlite3.connect(tmpfile)
        cur = conn.cursor()
        # join moz_places + moz_historyvisits
        cur.execute("""
            SELECT p.url, p.title, v.visit_date
            FROM moz_places p
            JOIN moz_historyvisits v ON p.id = v.place_id
            ORDER BY v.visit_date DESC LIMIT 100
        """)
        for url, title, visit_date in cur.fetchall():
            chrome_time = firefox_time_to_chrome_time(visit_date)
            rows.append((url, title, chrome_time))
        conn.close()
    except Exception as e:
        print(f"[!] L?i d?c Firefox: {e}")
    finally:
        try: os.remove(tmpfile)
        except: pass
    return rows

# ======== Fake history ========

def create_fake_history(fake_path, rows):
    """T?o file History gi? v?i b?ng urls + visits + visit_source."""
    os.makedirs(os.path.dirname(fake_path), exist_ok=True)
    if os.path.exists(fake_path):
        os.remove(fake_path)

    conn = sqlite3.connect(fake_path)
    cur = conn.cursor()

    cur.execute("""CREATE TABLE urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url LONGVARCHAR,
        title LONGVARCHAR,
        visit_count INTEGER DEFAULT 0,
        typed_count INTEGER DEFAULT 0,
        last_visit_time INTEGER NOT NULL DEFAULT 0,
        hidden INTEGER DEFAULT 0,
        favicon_id INTEGER DEFAULT 0
    );""")

    cur.execute("""CREATE TABLE visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url INTEGER NOT NULL,
        visit_time INTEGER NOT NULL,
        from_visit INTEGER,
        transition INTEGER DEFAULT 0,
        segment_id INTEGER,
        is_indexed INTEGER
    );""")

    cur.execute("""CREATE TABLE visit_source (
        id INTEGER PRIMARY KEY,
        source INTEGER NOT NULL
    );""")

    for i, (url, title, last_visit_time) in enumerate(rows, 1):
        cur.execute("INSERT INTO urls (id, url, title, visit_count, last_visit_time) VALUES (?, ?, ?, ?, ?)",
                    (i, url, title or "", 1, last_visit_time))
        cur.execute("INSERT INTO visits (id, url, visit_time, transition) VALUES (?, ?, ?, ?)",
                    (i, i, last_visit_time, 805306368))  # LINK
        cur.execute("INSERT INTO visit_source (id, source) VALUES (?, ?)", (i, 0))

    conn.commit()
    conn.close()

# ======== Main ========

def main():
    print("=== BrowserHistorySync Debug Mode ===")
    config = load_config()

    for browser, paths in config.items():
        real = paths.get("REAL_HISTORY")
        fake = paths.get("FAKE_HISTORY")

        if not real or not fake:
            print(f"[{browser}] ? Thi?u c?u hnh")
            continue

        print(f"[{browser}] ang x? l...")

        if browser.lower() in ("chrome", "coccoc"):
            rows = read_chrome_history(real)
        elif browser.lower() == "firefox":
            rows = read_firefox_history(real)
        else:
            print(f"[{browser}] ? Khng h? tr?")
            continue

        if rows:
            create_fake_history(fake, rows)
            print(f"[{browser}] ? T?o fake history ({len(rows)} b?n ghi)")
        else:
            print(f"[{browser}] ? Khng d?c du?c d? li?u")

if __name__ == "__main__":
    main()
