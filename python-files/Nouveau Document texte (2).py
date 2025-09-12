# ultra_flipper.py
# Simulation ultra-flippante, INOFFENSIVE
# Raccourcis pour quitter immédiatement : Échap ou Ctrl+Q

import tkinter as tk
from tkinter import messagebox
import threading, time, random
import winsound
import sys

STOP = False  # flag global pour arrêter

def on_key(event=None):
    global STOP
    STOP = True

def on_ctrl_q(event=None):
    global STOP
    if (event.state & 0x4) != 0:
        STOP = True

def panic_beeps():
    try:
        for freq, dur in [(1200,120),(800,120),(1500,180),(600,120),(2000,300)]:
            if STOP: return
            winsound.Beep(freq,dur)
            time.sleep(0.05)
    except RuntimeError:
        pass

def spawn_popups(root):
    messages = [
        "ERREUR CRITIQUE : SYSTÈME COMPROMIS",
        "AVERTISSEMENT : INTRUSION DÉTECTÉE",
        "DANGER : FICHIERS CORROMPUS",
        "SÉCURITÉ : AUCUNE RÉPONSE DU KERNEL",
        "ALERTE : RÉSEAU ROMPU"
    ]
    for _ in range(8):
        if STOP: break
        try:
            top = tk.Toplevel(root)
            top.title("Sécurité Windows")
            top.geometry("420x120+{}+{}".format(random.randint(0,600), random.randint(0,300)))
            top.configure(bg="#111")
            lbl = tk.Label(top, text=random.choice(messages),
                           font=("Segoe UI", 12, "bold"), fg="white", bg="#111",
                           wraplength=380, justify="center")
            lbl.pack(expand=True, padx=8, pady=8)
            threading.Thread(target=lambda: winsound.Beep(800+random.randint(-200,400),180), daemon=True).start()
            top.after(3000, lambda w=top: w.destroy())
            time.sleep(0.45)
        except Exception:
            pass

def big_screen_show(root):
    global STOP
    bs = tk.Toplevel(root)
    bs.attributes("-fullscreen", True)
    bs.configure(bg="black")
    bs.focus_set()
    bs.grab_set()

    big = tk.Label(bs, text="!!! SYSTÈME COMPROMIS !!!",
                   font=("Consolas",48,"bold"), fg="#00FF00", bg="black")
    big.pack(pady=40)

    prog_lbl = tk.Label(bs, text="Analyse en cours : 0%", font=("Consolas",28),
                        fg="#00FF00", bg="black")
    prog_lbl.pack(pady=10)

    tech = tk.Text(bs, width=120, height=12, bg="black", fg="#00FF00", font=("Consolas",12))
    tech.insert("end", "Dump mémoire:\n")
    for i in range(12):
        tech.insert("end", f"0x{random.randint(0x1000,0xFFFF):04X}: {random.randint(0,999999999):09d}  ERR\n")
    tech.configure(state="disabled")
    tech.pack(pady=10)

    for p in range(1,101):
        if STOP: break
        prog_lbl.config(text=f"Analyse en cours : {p}%")
        big.config(fg="#FF3333" if p%2==0 else "#00FF00")
        if p>85 and p%3==0:
            threading.Thread(target=panic_beeps, daemon=True).start()
        bs.update()
        time.sleep(0.06)

    if not STOP:
        for s in range(10,0,-1):
            if STOP: break
            prog_lbl.config(text=f"Redémarrage automatique dans {s} s")
            bs.update()
            winsound.Beep(1000+(10*(10-s)),140)
            time.sleep(0.9)
    try:
        bs.destroy()
    except Exception:
        pass

def reveal_and_exit(root):
    global STOP
    STOP = True
    time.sleep(0.4)
    try:
        messagebox.showinfo("C'est une blague","Ceci était une simulation INOFFENSIVE.\nAucun fichier n'a été modifié.\nAppuie sur OK pour quitter.")
    except Exception:
        pass
    root.quit()
    root.destroy()
    sys.exit(0)

def main_show():
    global STOP
    root = tk.Tk()
    root.withdraw()
    root.bind_all("<Escape>", lambda e: on_key(e))
    root.bind_all("<Control-q>", lambda e: on_ctrl_q(e))

    t1 = threading.Thread(target=spawn_popups, args=(root,), daemon=True)
    t1.start()
    threading.Thread(target=panic_beeps, daemon=True).start()

    for _ in range(10):
        if STOP: break
        time.sleep(0.25)

    if STOP:
        reveal_and_exit(root)
        return

    big_screen_show(root)
    reveal_and_exit(root)

if __name__=="__main__":
    try:
        main_show()
    except KeyboardInterrupt:
        STOP=True
        try:
            messagebox.showinfo("Interrompu","Simulation arrêtée.")
        except Exception:
            pass
        sys.exit(0)
