#!/usr/bin/env python3
"""
upload_to_gdoc.py

Reads 'cloudflared_output.txt' from the current directory
and uploads its full text to a Google Doc via an Apps Script Web App.
"""

import os
import sys
import requests

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────
APPSCRIPT_URL = "https://script.google.com/macros/s/AKfycbzVNgEFja_eUyo3ZYGpe98xvIwYrIscKeEJGBrsGkhUmDoO1yTec05mA2zPOevdIEq_/exec"
# ────────────────────────────────────────────────────────────────────────────────

def upload_txt_to_gdoc(txt_filename: str):
    # Ensure the file exists in the same directory
    if not os.path.isfile(txt_filename):
        print(f"❌ File not found: {txt_filename}")
        sys.exit(1)

    # Read the entire file
    with open(txt_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # Build JSON payload
    payload = {"content": content}

    # Send POST request
    try:
        resp = requests.post(APPSCRIPT_URL, json=payload, timeout=30)
    except requests.RequestException as e:
        print("❌ Request error:", e)
        sys.exit(1)

    # Check response
    if resp.status_code == 200 and resp.text.strip() == "OK":
        print("✅ Uploaded successfully!")
    else:
        print("❌ Upload failed:")
        print("   HTTP Status:", resp.status_code)
        print("   Response   :", resp.text)


if __name__ == "__main__":
    TXT_FILE = "cloudflared_output.txt"
    # Optionally allow passing a different filename on the command line:
    if len(sys.argv) == 2:
        TXT_FILE = sys.argv[1]
    print(f"Uploading '{TXT_FILE}' to Google Doc…")
    upload_txt_to_gdoc(TXT_FILE)
