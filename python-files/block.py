import os
import time
import socket
import threading
import keyboard
import firebase_admin
from firebase_admin import db, credentials

# Firebase setup
cred = credentials.Certificate("firebase.json")  # get it from Firebase Console > Service accounts
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rgp-mana-default-rtdb.firebaseio.com/'
})

pause_until = 0

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

def shutdown_pc():
    print("[!] Shutting down system...")
    os.system("shutdown /s /t 0")

def firebase_check():
    ref = db.reference("turn")
    while True:
        if time.time() < pause_until:
            time.sleep(1)
            continue

        if not is_connected():
            print("[!] No internet. Forcing shutdown.")
            shutdown_pc()

        try:
            val = ref.get()
            if val is not None and str(val).strip().lower() == "off":
                print("[!] Firebase 'turn=off'. Forcing shutdown.")
                shutdown_pc()
        except:
            print("[!] Firebase error. Assuming offline. Forcing shutdown.")
            shutdown_pc()

        time.sleep(2)

def listen_shift_v():
    global pause_until
    def activate_pause():
        global pause_until
        print("[*] Shift + V detected. Disabling shutdown for 10 minutes.")
        pause_until = time.time() + 600
    keyboard.add_hotkey("shift+v", activate_pause)
    keyboard.wait()

if __name__ == "__main__":
    threading.Thread(target=firebase_check, daemon=True).start()
    threading.Thread(target=listen_shift_v, daemon=True).start()
    while True:
        time.sleep(10)
