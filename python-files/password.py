import os
import getpass
import shutil

# Konfiguration
CORRECT_PASSWORD = "hemmeligkode"
TARGET_FOLDER = r"C:\Users\IIDeF\Desktop\test-det"  # <-- ændr denne sti!
ALLOWED_ATTEMPTS = 3

# Filtyper der slettes
TARGET_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.mov', '.avi', '.txt', '.docx', '.pdf']

def delete_sensitive_files(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in TARGET_EXTENSIONS):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"Slettet: {file}")
                except Exception as e:
                    print(f"Fejl ved sletning af {file}: {e}")

# Kodecheck
for attempt in range(ALLOWED_ATTEMPTS):
    entered = getpass.getpass("Indtast adgangskode: ")
    if entered == CORRECT_PASSWORD:
        print("Adgang godkendt.")
        break
    else:
        print("Forkert kode.")
else:
    print("For mange forkerte forsøg. Sletter filer...")
    delete_sensitive_files(TARGET_FOLDER)
