import base64
import re

CONFIG_FILE = "config.xml"  # ή config.cfg

try:
    with open(CONFIG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()
except FileNotFoundError:
    print(f"❌ Δεν βρέθηκε το '{CONFIG_FILE}'. Βεβαιώσου ότι το αρχείο config.xml είναι στον ίδιο φάκελο.")
    input("Πάτησε Enter για έξοδο...")
    exit()

username_match = re.search(r"<Username>(.*?)</Username>", data, re.IGNORECASE)
password_match = re.search(r"<Password>(.*?)</Password>", data, re.IGNORECASE)

print("=== ΑΠΟΤΕΛΕΣΜΑΤΑ PPPoE ===")
if username_match:
    print(f"PPPoE Username: {username_match.group(1)}")
else:
    print("Δεν βρέθηκε PPPoE Username στο αρχείο.")

if password_match:
    raw_password = password_match.group(1)
    try:
        decoded = base64.b64decode(raw_password).decode("utf-8")
        if decoded.isprintable():
            print(f"PPPoE Password: {decoded}")
        else:
            print(f"PPPoE Password (δεν είναι κανονικό κείμενο): {raw_password}")
    except Exception:
        print(f"PPPoE Password: {raw_password}")
else:
    print("Δεν βρέθηκε PPPoE Password στο αρχείο.")

input("\nΠάτησε Enter για να κλείσει το παράθυρο...")
