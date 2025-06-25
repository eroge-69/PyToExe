
import os
import json
import hashlib
from datetime import datetime

BROWSER_PATHS = {
    "Chrome": os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"),
    "Edge": os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data"),
    "Brave": os.path.expanduser("~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Login Data"),
    "Firefox": os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
}

def get_file_metadata(file_path):
    try:
        stats = os.stat(file_path)
        metadata = {
            "exists": True,
            "last_accessed": datetime.fromtimestamp(stats.st_atime).isoformat(),
            "last_modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "file_size": stats.st_size,
            "md5_hash": hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        }
    except Exception as e:
        metadata = {
            "exists": False,
            "error": str(e)
        }
    return metadata

def scan_firefox_profiles():
    profile_dir = BROWSER_PATHS["Firefox"]
    results = {}
    if os.path.exists(profile_dir):
        for profile in os.listdir(profile_dir):
            login_file = os.path.join(profile_dir, profile, "logins.json")
            if os.path.exists(login_file):
                results[f"Firefox ({profile})"] = get_file_metadata(login_file)
    return results

def scan_browser_files():
    report = {}
    for browser, path in BROWSER_PATHS.items():
        if browser == "Firefox":
            report.update(scan_firefox_profiles())
        else:
            report[browser] = get_file_metadata(path)
    return report

report_data = scan_browser_files()
report_filename = "browser_credential_forensics_report.json"
with open(report_filename, "w") as f:
    json.dump(report_data, f, indent=4)

print(f"Forensic report saved to {report_filename}")
