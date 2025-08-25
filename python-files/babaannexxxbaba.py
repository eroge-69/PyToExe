# ultimate_troll.py
# Gelişmiş, tamamen zararsız troll akışı:
# 1) Hacker Attack simülasyonu (Matrix + loglar)
# 2) Fake Ransomware tam ekran (geri sayım + fake input)
# 3) BSOD Simülasyonu (çok gerçekçi görünüm)
# Panik tuşu: Esc
# Sistem dosyalarına/ağ/ayarlara DOKUNMAZ.

import tkinter as tk
from tkinter import ttk
import random, time

# ---------- Ortak yardımcılar ----------
PANIC_KEYS = {"Escape": True}

class FullscreenStage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Utility")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")
        self.root.bind("<Key>", self._panic)
        self.root.bind("<Escape>", self._panic)
        self.root.protocol("WM_DELETE_WINDOW", self._panic)
        # en öne
        try:
            self.root.attributes("-topmost", True)
        except:
            pass

    def _panic(self, event=None):
        # Esc vs. ile anında çıkış
        if event is None or event.keysym in PANIC_KEYS:
            try:
                self.root.destroy()
            except:
                pass

    def run(self):
        self.root.mainloop()

    def next_stage(self, fn):
        # mevcut pencereyi kapat, bir sonraki sahneyi aç
        try:
            self.root.destroy()
        except:
            pass
        fn()

# ---------- Sahne 1: Hacker Attack ----------
def stage_hacker_attack():
    app = FullscreenStage()
    root = app.root

    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    W = root.winfo_screenwidth()
    H = root.winfo_screenheight()

    # Matrix sütunları
    cols = W // 16
    drops = [random.randint(0, H // 16) for _ in range(cols)]
    charset = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    logs = tk.Text(root, height=10, bg="black", fg="#00ff6a", insertbackground="#00ff6a",
                   relief="flat", font=("Consolas", 12))
    logs.place(relx=0.05, rely=0.65, relwidth=0.9, relheight=0.3)
    logs.configure(state="disabled")

    def add_log(line):
        logs.configure(state="normal")
        logs.insert("end", line + "\n")
        logs.see("end")
        logs.configure(state="disabled")

    scripted = [
        "[*] Initializing network scanner...",
        "[*] Probing firewall rules...",
        "[*] Bypassing firewall... OK",
        "[*] Elevating privileges... OK",
        "[*] Accessing system files... OK",
        "[*] Dumping credentials...",
        "[*] Tracing internal IP: 192.168.%d.%d" % (random.randint(1, 254), random.randint(1, 254)),
        "[*] Uploading payload... OK",
        "[!] SYSTEM COMPROMISED!"
    ]
    script_idx = 0
    last_script_time = time.time()

    def tick():
        nonlocal script_idx, last_script_time
        canvas.delete("all")

        # Matrix yağmuru
        for i in range(cols):
            x = i * 16 + 8
            y = drops[i] * 16
            ch = random.choice(charset)
            canvas.create_text(x, y, text=ch, fill="#00ff6a", font=("Consolas", 14))
            if random.random() > 0.975:
                drops[i] = 0
            else:
                drops[i] += 1
            if drops[i] * 16 > H:
                drops[i] = 0

        # Scripted loglar yavaş yavaş
        now = time.time()
        if script_idx < len(scripted) and now - last_script_time > 0.6:
            add_log(scripted[script_idx])
            script_idx += 1
            last_script_time = now

        # Bitti mi? Son satır geldikten 1.5 sn sonra sonraki sahneye
        if script_idx == len(scripted) and now - last_script_time > 1.5:
            app.next_stage(stage_ransomware)
            return

        root.after(33, tick)  # ~30 FPS

    tick()
    app.run()

# ---------- Sahne 2: Fake Ransomware ----------
def stage_ransomware():
    app = FullscreenStage()
    root = app.root
    root.configure(bg="#140000")

    # Ana çerçeve
    frame = tk.Frame(root, bg="#140000")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    title = tk.Label(frame, text="YOUR FILES ARE ENCRYPTED!", fg="#ff2b2b", bg="#140000",
                     font=("Segoe UI", 40, "bold"))
    title.pack(pady=10)

    subtitle = tk.Label(frame, text="Send 1.5 BTC to the address below to decrypt.",
                        fg="#ffaaaa", bg="#140000", font=("Segoe UI", 16))
    subtitle.pack(pady=(0, 10))

    timer_var = tk.StringVar(value="10:00")
    timer_lbl = tk.Label(frame, textvariable=timer_var, fg="#ffffff", bg="#140000",
                         font=("Consolas", 36, "bold"))
    timer_lbl.pack(pady=10)

    addr_box = tk.Label(frame, text="BTC Wallet: bc1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                        fg="#ffaa00", bg="#140000", font=("Consolas", 14))
    addr_box.pack(pady=(0, 10))

    pin_lbl = tk.Label(frame, text="Enter decryption key:", fg="#ffcccc", bg="#140000",
                       font=("Segoe UI", 14))
    pin_lbl.pack()
    pin_entry = tk.Entry(frame, show="*", width=28, font=("Consolas", 14), relief="flat")
    pin_entry.pack(pady=6)
    msg_var = tk.StringVar(value="")
    msg_lbl = tk.Label(frame, textvariable=msg_var, fg="#ff6666", bg="#140000", font=("Segoe UI", 12))
    msg_lbl.pack()

    def fake_check():
        msg_var.set("Invalid key!")
        root.after(900, lambda: msg_var.set(""))

    btns = tk.Frame(frame, bg="#140000")
    btns.pack(pady=8)
    tk.Button(btns, text="Unlock", command=fake_check, bg="#330000", fg="#ffcccc",
              font=("Segoe UI", 11), relief="flat", padx=12, pady=6).pack(side="left", padx=6)
    tk.Button(btns, text="Help", command=fake_check, bg="#330000", fg="#ffcccc",
              font=("Segoe UI", 11), relief="flat", padx=12, pady=6).pack(side="left", padx=6)

    # Sayaç (10:00 → 00:00)
    total = 10 * 60
    start = time.time()

    def tick():
        nonlocal total, start
        elapsed = int(time.time() - start)
        left = max(total - elapsed, 0)
        m, s = divmod(left, 60)
        timer_var.set(f"{m:02d}:{s:02d}")
        # (Gösterim amaçlı) süreyi hızlandır: 10 dakikayı ~60 sn'de bitir
        if left == 0 or elapsed > 60:
            app.next_stage(stage_bsod_sim)
            return
        root.after(1000, tick)

    tick()
    app.run()

# ---------- Sahne 3: BSOD Simülasyonu ----------
def stage_bsod_sim():
    app = FullscreenStage()
    root = app.root
    BLUE = "#0175d8"
    WHITE = "#ffffff"
    root.configure(bg=BLUE)

    wrap = tk.Frame(root, bg=BLUE)
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    sad = tk.Label(wrap, text=":(", fg=WHITE, bg=BLUE, font=("Segoe UI", 120, "bold"))
    sad.pack(anchor="w")

    t1 = tk.Label(
        wrap,
        text="Your PC ran into a problem and needs to restart. We’re just collecting some error info, and then we’ll restart for you.",
        fg=WHITE, bg=BLUE, wraplength=900, justify="left", font=("Segoe UI", 18)
    )
    t1.pack(anchor="w", pady=(10, 6))

    pct_var = tk.StringVar(value="0% complete")
    pct = tk.Label(wrap, textvariable=pct_var, fg=WHITE, bg=BLUE, font=("Segoe UI", 18))
    pct.pack(anchor="w", pady=(0, 14))

    # QR benzeri placeholder
    qr = tk.Canvas(wrap, width=150, height=150, bg=WHITE, highlightthickness=0)
    qr.pack(anchor="w")
    # basit siyah kareler
    for _ in range(120):
        x = random.randint(0, 145)
        y = random.randint(0, 145)
        size = random.choice([4, 6])
        qr.create_rectangle(x, y, x+size, y+size, fill="black", width=0)

    info = tk.Label(
        wrap,
        text="For more information about this issue and possible fixes, visit: https://aka.ms/bsod\nStop code: FAKE_SIMULATION_NOT_REAL",
        fg=WHITE, bg=BLUE, font=("Segoe UI", 14), justify="left"
    )
    info.pack(anchor="w", pady=(12, 0))

    progress = 0
    def fill():
        nonlocal progress
        progress += random.randint(1, 5)
        progress = min(progress, 100)
        pct_var.set(f"{progress}% complete")
        if progress >= 100:
            # Final reveal
            reveal = tk.Label(root, text="JUST KIDDING — harmless simulation 😊\nPress Esc to exit.",
                              fg=WHITE, bg=BLUE, font=("Segoe UI", 24, "bold"))
            reveal.place(relx=0.5, rely=0.85, anchor="center")
            return
        root.after(180, fill)

    fill()
    app.run()

# ---------- Başlat ----------
if __name__ == "__main__":
    stage_hacker_attack()
