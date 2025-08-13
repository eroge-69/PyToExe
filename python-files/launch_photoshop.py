import os
import time
import webbrowser

# === CONFIGURATION ===
approval_file = r"F:\OneDrive - Creative Engineers Ltd\PhotoshopApproval\approval.txt"
form_url = "https://forms.office.com/r/UmcUd7MP2T"
photoshop_path =  r"C:\Program Files\Adobe\Adobe Photoshop 2021\Photoshop_real.exe"

# === STEP 1: Delete any old approval file ===
if os.path.exists(approval_file):
     try:
         os.remove(approval_file)
         print("[INFO] Old approval file deleted.")
     except Exception as e:
         print(f"[WARNING] Could not delete old approval file: {e}")

# === STEP 2: Open Microsoft Form ===
print("[INFO] Opening Microsoft Form for approval request...")
webbrowser.open(form_url)

print("[INFO] Waiting for Shamim Reza's approval...")

# === STEP 3: Wait for approval file ===
while True:
    if os.path.exists(approval_file):
        try:
            with open(approval_file, 'r', encoding='utf-8') as file:
                content = file.read().strip().lower()
                if content == 'approved':
                    print("[INFO] Approval received.")
                    break
        except Exception as e:
            print(f"[WARNING] Error reading approval file: {e}")
    time.sleep(5)

# === STEP 4: Launch Photoshop ===
print("[INFO] Launching Photoshop...")
try:
    os.startfile(photoshop_path)
except Exception as e:
    print(f"[ERROR] Failed to launch Photoshop: {e}")

# === STEP 5: Delete approval file ===
try:
    os.remove(approval_file)
    print("[INFO] Approval file removed for next use.")
except Exception as e:
    print(f"[WARNING] Could not delete approval file: {e}")
