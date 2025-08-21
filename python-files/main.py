import threading
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
import subprocess
import pyautogui

# ========= CONFIG =========
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
LOG_FILE = "macro_console_debug.log"
PAGE_BOOT_WAIT = 5   # temps initial pour laisser la fenêtre s'ouvrir
START_DELAY = 2      # délai fixe avant d'exécuter les macros
DELAY_MIN = 0.1      # délai min entre actions
DELAY_MAX = 0.3      # délai max entre actions
KEY_HOLD = 0.05      # maintien down pour fiabiliser la prise en compte
ALT_F4_DELAY_MIN = 5
ALT_F4_DELAY_MAX = 8
# ==========================

# --- PyAutoGUI config ---
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

# --- Logging ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("macro_console")

def pause():
    d = random.uniform(DELAY_MIN, DELAY_MAX)
    logger.debug(f"Pause {d:.3f}s")
    time.sleep(d)

def press(key, times=1, loglabel=None):
    for i in range(times):
        d = random.uniform(DELAY_MIN, DELAY_MAX)
        lbl = loglabel or key
        logger.info(f"[Keys] {lbl} ({i+1}/{times}) — delay {d:.3f}s")
        pyautogui.keyDown(key)
        time.sleep(KEY_HOLD)
        pyautogui.keyUp(key)
        time.sleep(d)

def type_text(txt, loglabel=None):
    logger.info(f"[Keys] TAPER {loglabel or 'texte'}: '{txt}'")
    pyautogui.typewrite(txt, interval=0)
    pause()

def fast_scroll_down(duration_sec=2.0):
    logger.info(f"[Scroll] Début scroll vers le bas pendant {duration_sec}s (pleine vitesse)")
    end = time.time() + duration_sec
    while time.time() < end:
        pyautogui.scroll(-1500)
        time.sleep(0.01)
    logger.info("[Scroll] Fin du scroll")

def run_macro(url, nom, password, status_cb=None, on_done=None, ui_log_cb=None,
              chrome_path=None, proxy_enabled=False, proxy_type="socks4",
              proxy_host="", proxy_port=""):
    def log(msg):
        logger.info(msg)
        print(msg)
        if ui_log_cb: ui_log_cb(msg)

    try:
        bin_path = chrome_path or CHROME_PATH
        if not os.path.exists(bin_path):
            raise FileNotFoundError(
                f"Chrome introuvable au chemin: {bin_path}\n"
                "Corrige le champ 'Chemin Chrome' dans l'UI."
            )

        # ---- Lancement Chrome (incognito + proxy optionnel) ----
        log("[Init] Lancement de Chrome… (incognito" + (", proxy ON" if proxy_enabled else ", proxy OFF") + ")")
        cmd = [bin_path, "--incognito", "--new-window"]

        if proxy_enabled:
            # Normalise le type
            scheme = proxy_type.lower().strip()
            if scheme not in ("http", "https", "socks4", "socks5"):
                scheme = "socks4"
            host = proxy_host.strip()
            port = str(proxy_port).strip()
            if not host or not port:
                raise ValueError("Proxy activé mais host/port manquants.")
            cmd.append(f"--proxy-server={scheme}://{host}:{port}")
            # limite le bypass local
            cmd.append("--proxy-bypass-list=<-loopback>")
            # pour SOCKS: éviter fuite DNS (résolution par le proxy)
            if scheme.startswith("socks"):
                cmd.append("--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE localhost")

        cmd.append(url)
        proc = subprocess.Popen(cmd, shell=False)
        log(f"[Init] PID Chrome: {proc.pid}")

        # ---- Attentes avant macro (inchangé) ----
        if status_cb: status_cb("Ouverture de la page…")
        time.sleep(PAGE_BOOT_WAIT)
        pause()

        log(f"[WAIT] Attente de {START_DELAY} secondes avant exécution des macros…")
        if status_cb: status_cb(f"Attente {START_DELAY} secondes avant de commencer…")
        time.sleep(START_DELAY)

        # ---- Macro (inchangée) ----
        if status_cb: status_cb("Exécution de la séquence clavier…")
        log("[Seq] Début séquence")

        press("tab", 2, "TAB")
        press("down", 1, "↓")
        press("tab", 1, "TAB")
        press("down", 1, "↓")
        press("tab", 1, "TAB")
        press("down", 30, "↓↓ (30)")
        press("tab", 1, "TAB")
        type_text(nom, "Nom")
        press("tab", 1, "TAB")
        type_text(password, "Mot de passe")

        fast_scroll_down(2.0)

        press("tab", 5, "TAB")

        log("[WAIT] Pause finale de 3 secondes avant ENTER…")
        time.sleep(3)

        press("enter", 1, "ENTER")

        # ALT+F4 après 3–10s
        final_wait = random.uniform(ALT_F4_DELAY_MIN, ALT_F4_DELAY_MAX)
        log(f"[WAIT] Attente {final_wait:.2f}s puis ALT+F4…")
        time.sleep(final_wait)
        logger.info("[Keys] ALT+F4")
        pyautogui.hotkey("alt", "f4")

        log("[Seq] Séquence terminée ✅ (fenêtre fermée)")
        if status_cb: status_cb("Séquence terminée ✅")
    except Exception as e:
        logger.exception("Erreur pendant l'exécution")
        if status_cb: status_cb(f"Erreur : {e}")
        messagebox.showerror("Erreur", str(e))
    finally:
        if on_done: on_done()

# ---------- Interface ----------
def main():
    root = tk.Tk()
    root.title("Macro (Incognito) – Avec Proxy (optionnel)")
    root.geometry("920x520")

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    url_var = tk.StringVar(value="https://www.google.com")  # tu peux mettre ce que tu veux
    nom_var = tk.StringVar(value="testrk")
    pwd_var = tk.StringVar(value="12345678910")

    # Proxy defaults from your screenshot (SOCKS4 129.151.72.85:80)
    use_proxy_var = tk.BooleanVar(value=True)
    proxy_type_var = tk.StringVar(value="socks4")
    proxy_host_var = tk.StringVar(value="129.151.72.85")
    proxy_port_var = tk.StringVar(value="80")

    ttk.Label(frm, text="Chemin Chrome :").grid(row=0, column=0, sticky="w")
    chrome_entry = ttk.Entry(frm, width=60)
    chrome_entry.insert(0, CHROME_PATH)
    chrome_entry.grid(row=0, column=1, sticky="ew", pady=4, columnspan=3)

    ttk.Label(frm, text="URL (incognito) :").grid(row=1, column=0, sticky="w")
    url_entry = ttk.Entry(frm, textvariable=url_var, width=60)
    url_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4)

    ttk.Label(frm, text="Nom :").grid(row=2, column=0, sticky="w")
    nom_entry = ttk.Entry(frm, textvariable=nom_var, width=30)
    nom_entry.grid(row=2, column=1, sticky="w", pady=4)

    ttk.Label(frm, text="Password :").grid(row=2, column=2, sticky="w")
    pwd_entry = ttk.Entry(frm, textvariable=pwd_var, show="•", width=30)
    pwd_entry.grid(row=2, column=3, sticky="w", pady=4)

    # ----- Proxy UI -----
    proxy_frame = ttk.LabelFrame(frm, text="Proxy (optionnel)")
    proxy_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(8,4))
    ttk.Checkbutton(proxy_frame, text="Utiliser un proxy", variable=use_proxy_var).grid(row=0, column=0, padx=6, pady=6, sticky="w")

    ttk.Label(proxy_frame, text="Type :").grid(row=0, column=1, sticky="e")
    proxy_type_cb = ttk.Combobox(proxy_frame, textvariable=proxy_type_var, values=["http", "https", "socks4", "socks5"], width=10, state="readonly")
    proxy_type_cb.grid(row=0, column=2, padx=4, sticky="w")

    ttk.Label(proxy_frame, text="Host :").grid(row=0, column=3, sticky="e")
    proxy_host_entry = ttk.Entry(proxy_frame, textvariable=proxy_host_var, width=22)
    proxy_host_entry.grid(row=0, column=4, padx=4, sticky="w")

    ttk.Label(proxy_frame, text="Port :").grid(row=0, column=5, sticky="e")
    proxy_port_entry = ttk.Entry(proxy_frame, textvariable=proxy_port_var, width=8)
    proxy_port_entry.grid(row=0, column=6, padx=4, sticky="w")

    status_var = tk.StringVar(value="Prêt.")
    status_lbl = ttk.Label(frm, textvariable=status_var)
    status_lbl.grid(row=4, column=0, columnspan=4, sticky="w", pady=(8,6))

    # ===== Tableau Nom / Password / conection (avec séparateurs) =====
    table_frame = ttk.Frame(frm)
    table_frame.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=(6,0))
    frm.grid_rowconfigure(5, weight=1)
    for col in (1, 2):
        frm.grid_columnconfigure(col, weight=1)

    columns = ("nom", "password", "conection")
    cred_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
    cred_table.heading("nom", text="Nom")
    cred_table.heading("password", text="Password")
    cred_table.heading("conection", text="conection")
    cred_table.column("nom", width=240, anchor="w")
    cred_table.column("password", width=240, anchor="w")
    cred_table.column("conection", width=200, anchor="w")
    cred_table.pack(side="left", fill="both", expand=True)

    scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=cred_table.yview)
    cred_table.configure(yscrollcommand=scroll_y.set)
    scroll_y.pack(side="right", fill="y")

    def ui_log(msg):
        pass  # pas de console

    def set_status(msg):
        status_var.set(msg)
        root.update_idletasks()

    def on_done():
        start_btn.config(state="normal")

    def insert_with_separator(values_tuple):
        if len(cred_table.get_children()) > 0:
            sep = ("─"*24, "─"*24, "─"*20)
            cred_table.insert("", "end", values=sep)
        cred_table.insert("", "end", values=values_tuple)

    def start():
        url = url_var.get().strip()
        nom = nom_var.get()
        pwd = pwd_var.get()
        chrome_path = chrome_entry.get().strip()

        if not url:
            messagebox.showwarning("URL manquante", "Veuillez saisir une URL.")
            return
        if not chrome_path:
            messagebox.showwarning("Chrome manquant", "Veuillez renseigner le chemin de Chrome.")
            return

        # Ajoute la ligne au tableau (Nom / Password / conection vide)
        insert_with_separator((nom, pwd, ""))

        start_btn.config(state="disabled")
        set_status("Démarrage…")

        t = threading.Thread(
            target=run_macro,
            args=(
                url, nom, pwd, set_status, on_done, ui_log, chrome_path,
                use_proxy_var.get(), proxy_type_var.get(), proxy_host_var.get(), proxy_port_var.get()
            ),
            daemon=True
        )
        t.start()

    start_btn = ttk.Button(frm, text="Lancer la macro", command=start)
    start_btn.grid(row=6, column=0, columnspan=4, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
