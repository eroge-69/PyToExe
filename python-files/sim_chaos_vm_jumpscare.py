# sim_chaos_vm_jumpscare.py
# VM için zararsız kaos simülasyonu + jumpscare
# Gereksinimler: pillow (resim için), winsound (Windows), jumpscare.jpg ve jumpscare.wav opsiyonel
# Çalıştır: python sim_chaos_vm_jumpscare.py
# EXE yapmak: pyinstaller --onefile --windowed --add-data "resim.jpg;." --add-data "jumpscare.jpg;." --add-data "jumpscare.wav;." sim_chaos_vm_jumpscare.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading, time, random, sys, os

# Pillow opsiyonel (resim gösterim)
try:
    from PIL import Image, ImageTk
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

# Windows ses
try:
    import winsound
    HAVE_WINSOUND = True
except Exception:
    HAVE_WINSOUND = False

# ---------------- CONFIG ----------------
POPUP_PER_WAVE = 50
MAX_WAVES = 2
POPUP_STAGGER = 0.05
GLITCH_DURATION = 20
BOOT_DURATION = 6
IMAGE_PATH = "resim.jpg"
JUMPSCARE_IMAGE = "jumpscare.jpg"
JUMPSCARE_WAV = "jumpscare.wav"
JUMPSCARE_DURATION = 0.6  # saniye
# ----------------------------------------

root = tk.Tk()
root.withdraw()
popup_windows = []
popup_lock = threading.Lock()
closed_count = 0
wave_count = 0

def safe_beep_sequence(duration_sec=GLITCH_DURATION):
    if not HAVE_WINSOUND:
        return
    end = time.time() + duration_sec
    freqs = [250, 360, 480, 720, 1000, 1300, 1700]
    while time.time() < end:
        f = random.choice(freqs) + random.randint(-80,80)
        d = random.randint(30, 160)
        try:
            winsound.Beep(max(37,int(f)), d)
        except Exception:
            break
        time.sleep(random.random()*0.03)

def make_popup(i, wave_idx):
    w = tk.Toplevel()
    w.title(f"Notice_{wave_idx+1}_{i+1}")
    x = 60 + (i*13) % (root.winfo_screenwidth()-360)
    y = 40 + (i*9) % (root.winfo_screenheight()-220)
    w.geometry(f"360x120+{x}+{y}")
    w.attributes("-topmost", True)

    frm = tk.Frame(w, padx=8, pady=8)
    frm.pack(expand=True, fill="both")
    lbl = tk.Label(frm, text="YouAreIdiot", font=("Helvetica", 18, "bold"), fg="red")
    lbl.pack()
    sub = tk.Label(frm, text="zipler... şeker kapanırsa daha çok çıkacak...", font=("Helvetica", 9))
    sub.pack()
    btn = tk.Button(frm, text="Kapat", width=10, command=lambda: close_popup(w))
    btn.pack(pady=(8,0))

    w.protocol("WM_DELETE_WINDOW", lambda: close_popup(w))
    return w

def close_popup(w):
    global closed_count, wave_count
    try: w.destroy()
    except: pass
    with popup_lock:
        closed_count += 1
        if closed_count >= 1 and wave_count < MAX_WAVES:
            if wave_count < MAX_WAVES:
                threading.Thread(target=spawn_wave, args=(POPUP_PER_WAVE,), daemon=True).start()

def spawn_wave(count):
    global popup_windows, wave_count
    with popup_lock:
        if wave_count >= MAX_WAVES: return
        current_wave = wave_count
        wave_count += 1
    for i in range(count):
        try: w = make_popup(i, current_wave); popup_windows.append(w)
        except: pass
        time.sleep(POPUP_STAGGER)

def close_all_popups():
    global popup_windows
    with popup_lock:
        for w in list(popup_windows):
            try: w.destroy()
            except: pass
        popup_windows.clear()

def fullscreen_boot_screen(on_close_callback=None):
    boot = tk.Toplevel()
    boot.title("BOOT")
    boot.attributes("-fullscreen", True)
    boot.configure(bg="black")
    boot.attributes("-topmost", True)

    def close_boot(event=None):
        try: boot.destroy()
        except: pass
        if on_close_callback: on_close_callback()

    boot.bind("<Escape>", close_boot)
    boot.protocol("WM_DELETE_WINDOW", close_boot)

    lbl = tk.Label(boot, text="BOOST LOADER\nYükleniyor...", fg="lime", bg="black", font=("Consolas", 36))
    lbl.pack(expand=True)
    pb = ttk.Progressbar(boot, orient="horizontal", mode="determinate", length=1000)
    pb.pack(pady=30)
    pb['maximum'] = 100

    def progress_run():
        start = time.time()
        while time.time() - start < BOOT_DURATION:
            elapsed = time.time() - start
            pct = min(100, ((elapsed / BOOT_DURATION) ** 0.9) * 100 + random.random()*6)
            try: pb['value'] = pct
            except: pass
            time.sleep(0.04)
        pb['value'] = 100
        time.sleep(0.25)
        # Jumpscare
        show_jumpscare(boot)
        # normal resim / efekt
        show_image_on_toplevel(boot)

    threading.Thread(target=progress_run, daemon=True).start()

def show_jumpscare(parent):
    try:
        top = tk.Toplevel()
        top.attributes("-fullscreen", True)
        top.attributes("-topmost", True)
        top.configure(bg="black")
        # resim
        if HAVE_PIL and JUMPSCARE_IMAGE and os.path.exists(JUMPSCARE_IMAGE):
            img = Image.open(JUMPSCARE_IMAGE)
            img = img.resize((parent.winfo_screenwidth(), parent.winfo_screenheight()), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(top, image=photo)
            lbl.image = photo
            lbl.pack(fill="both", expand=True)
        # kısa ses
        if HAVE_WINSOUND and JUMPSCARE_WAV and os.path.exists(JUMPSCARE_WAV):
            threading.Thread(target=lambda: winsound.PlaySound(JUMPSCARE_WAV, winsound.SND_FILENAME | winsound.SND_ASYNC), daemon=True).start()
        parent.update()
        time.sleep(JUMPSCARE_DURATION)
        top.destroy()
    except: pass

def show_image_on_toplevel(parent):
    if HAVE_PIL and IMAGE_PATH and os.path.exists(IMAGE_PATH):
        try:
            sw, sh = parent.winfo_screenwidth(), parent.winfo_screenheight()
            img = Image.open(IMAGE_PATH).convert("RGB").resize((sw, sh), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(parent, image=photo)
            lbl.image = photo
            lbl.pack(fill="both", expand=True)
            return
        except: pass
    fallback_color_flash(parent)

def fallback_color_flash(parent):
    for i in range(10):
        c = "#" + "".join([f"{random.randint(0,255):02x}" for _ in range(3)])
        frm = tk.Frame(parent, bg=c, height= int(parent.winfo_screenheight()/10))
        frm.pack(fill="x")
        parent.update()
        time.sleep(0.07)
    for child in list(parent.winfo_children()):
        if isinstance(child, tk.Frame):
            try: child.destroy()
            except: pass

def main_simulation():
    threading.Thread(target=spawn_wave, args=(POPUP_PER_WAVE,), daemon=True).start()
    threading.Thread(target=safe_beep_sequence, args=(GLITCH_DURATION,), daemon=True).start()
    time.sleep(GLITCH_DURATION)
    close_all_popups()
    root.after(100, lambda: fullscreen_boot_screen())

# GUI Kontrol
ctrl = tk.Toplevel()
ctrl.title("Sim Kontrol (VM recommended)")
ctrl.geometry("420x220+200+120")
ctrl.attributes("-topmost", True)
tk.Label(ctrl, text="Sanal Kaos Simülasyonu + Jumpscare (VM)", font=("Helvetica", 14, "bold")).pack(pady=(12,6))

tk.Button(ctrl, text="Başlat (VM'de dene)", width=30, command=lambda: threading.Thread(target=main_simulation, daemon=True).start()).pack(pady=(8,6))
tk.Button(ctrl, text="Kapat", width=30, command=lambda: (close_all_popups(), root.quit(), sys.exit(0))).pack(pady=(6,8))
tk.Label(ctrl, text="NOT: Jumpscare güvenli, internet gerçek anlamda kapatılmaz.", fg="gray").pack(pady=(6,0))

root.mainloop()
