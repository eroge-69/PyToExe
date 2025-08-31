# ===================================================
# Educational Malware Behavior Simulation Script
# For use in sandbox environments (e.g., Any.Run)
# Purpose: Demonstrate common malware behaviors SAFELY
# This script does NOT harm systems or steal data.
# ===================================================

import os
import time
import sys
import subprocess
import winreg  # Only on Windows
from datetime import datetime

# === 1. Simulate: File Creation (like a dropper) ===
print("[*] Step 1: Simulating payload drop...")
time.sleep(2)

# Create a fake "malicious" file in temp directory
temp_dir = os.getenv('TEMP')
fake_payload = os.path.join(temp_dir, "system_update.exe")

try:
    with open(fake_payload, 'w') as f:
        f.write("This is a simulated malware payload. For educational purposes only.\n")
        f.write(f"Generated at: {datetime.now()}\n")
    print(f"[+] Created simulated file: {fake_payload}")
except Exception as e:
    print(f"[-] File creation failed: {e}")

# === 2. Simulate: Registry Modification (persistence attempt) ===
print("\n[*] Step 2: Simulating registry persistence...")
time.sleep(2)

try:
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
    winreg.SetValueEx(key, "SystemUpdater", 0, winreg.REG_SZ, fake_payload)
    winreg.CloseKey(key)
    print(f"[+] Simulated registry persistence added: SystemUpdater -> {fake_payload}")
except Exception as e:
    print(f"[-] Registry write failed: {e}")

# === 3. Simulate: Process Execution ===
print("\n[*] Step 3: Simulating process execution...")
time.sleep(2)

try:
    # Launch Notepad as a "payload" (harmless)
    proc = subprocess.Popen(['notepad.exe'])
    print("[+] Launched notepad.exe (simulated payload execution)")
    time.sleep(3)
    proc.terminate()
except Exception as e:
    print(f"[-] Process execution failed: {e}")

# === 4. Simulate: Network Connection (HTTP GET) ===
print("\n[*] Step 4: Simulating C2 beacon...")
time.sleep(2)

try:
    import urllib.request
    # Connect to a safe, public endpoint (no real C2)
    url = "http://connectivitycheck.gstatic.com/generate_204"
    with urllib.request.urlopen(url, timeout=5) as response:
        print(f"[+] Simulated beacon sent. Status: {response.status} (No data exfiltrated)")
except Exception as e:
    print(f"[-] Network connection failed or blocked: {e}")

# === 5. Simulate: Obfuscation (string encoding) ===
print("\n[*] Step 5: Simulating string obfuscation...")
time.sleep(2)

obfuscated = "U2ltdWxhdGVkIE1hbHdhcmUgLSBodHRwczovL2dvaG9zdC5jb20="  # Base64 for "Simulated Malware - https://google.com"
import base64
decoded = base64.b64decode(obfuscated).decode('utf-8')
print(f"[i] Decoded string: {decoded}")

# === Final Message ===
print("\n[✔] Simulation Complete. This was a SAFE educational demo.")
print("No real malware was executed. No data was stolen or encrypted.")