import keyboard
import threading
import time
import signal
import sys

keyboard_locked = False
hook_id = None
timeout_seconds = 60  # temps avant déverrouillage auto (0 = désactivé)
timeout_timer = None

def unlock():
    global keyboard_locked, hook_id, timeout_timer
    if timeout_timer:
        timeout_timer.cancel()
        timeout_timer = None
    if hook_id is not None:
        keyboard.unhook(hook_id)
    keyboard_locked = False
    print("\n✅ Keyboard unlocked!")

def lock():
    global keyboard_locked, hook_id, timeout_timer
    if keyboard_locked:
        return
    keyboard_locked = True
    hook_id = keyboard.hook(block_keys, suppress=True)
    print("🔒 Keyboard locked!")
    if timeout_seconds > 0:
        # lance un timer de déverrouillage automatique
        def timeout_unlock():
            print(f"\n⏰ Timeout atteint ({timeout_seconds}s). Déverrouillage automatique.")
            unlock()
        timeout_timer = threading.Timer(timeout_seconds, timeout_unlock)
        timeout_timer.start()

def toggle_lock():
    global keyboard_locked
    if keyboard_locked:
        unlock()
    else:
        lock()

def block_keys(e):
    global keyboard_locked
    if keyboard_locked:
        if e.event_type == 'down' and e.name == 'f3':
            toggle_lock()
            return False  # bloque F3 aussi pour éviter qu’il tape dans une app
        return False  # bloque tout

# Ignore Ctrl+C pour éviter un arrêt du script pendant verrouillage
def signal_handler(sig, frame):
    if keyboard_locked:
        print("\n⚠️ Script verrouillé — Ctrl+C ignoré.")
    else:
        print("\nArrêt du script.")
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Touche F3 pour toggle lock/unlock
keyboard.add_hotkey('f3', toggle_lock, suppress=True)

print("🔔 Appuie sur F3 pour verrouiller/déverrouiller le clavier.")
print(f"⏳ Timeout déverrouillage auto réglé à {timeout_seconds} secondes." if timeout_seconds > 0 else "⏳ Pas de timeout activé.")

keyboard.wait()
