#!/usr/bin/env python3
import os, sys, json, uuid, hashlib, subprocess, ctypes, webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# ------------------- Config -------------------
DARK_BG = "#121212"
BTN_BG = "#1E3A8A"
BTN_FG = "#FFFFFF"
TEXT_COLOR = "#FFFFFF"
INPUT_BG = "#1E1E1E"
FONT = ("Consolas", 10)

KEY_STORAGE_FILE = "keys.json"
BLACKLIST_FILE = "blacklist.json"
ACCOUNTS_FILE = "accounts.json"
APPLIED_STATE_FILE = "applied_state.json"
KICK_URL = "https://discord.gg/9ZtR8UWMM4"
# ---------------------------------------------

def resource_path(relative):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

def external_path(relative):
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    p = os.path.join(exe_dir, relative)
    return p if os.path.exists(p) else resource_path(relative)

def load_json_optional(filename):
    path = external_path(filename)
    if not os.path.exists(path): return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return None

def save_json_external(filename, data):
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    path = os.path.join(exe_dir, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except: return False

def get_hwid():
    return format(uuid.getnode(), '012x').upper()

def hash_password(pw):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

# ---------------- Key / Blacklist ----------------
def load_keys(): return load_json_optional(KEY_STORAGE_FILE) or []
def load_accounts(): return load_json_optional(ACCOUNTS_FILE) or []
def save_accounts(accounts): return save_json_external(ACCOUNTS_FILE, accounts)
def load_local_blacklist():
    bl = load_json_optional(BLACKLIST_FILE)
    return [s.strip().upper() for s in bl if isinstance(s,str)] if isinstance(bl,list) else []

def is_key_blacklisted(key):
    return key.strip().upper() in load_local_blacklist()

def verify_key_local(key):
    keyn = key.strip().upper()
    for entry in load_keys():
        if entry.get("key","").strip().upper() == keyn:
            if entry.get("hwid","").strip().upper() != get_hwid():
                return False, "HWID stimmt nicht überein!"
            try: exp_dt = datetime.fromisoformat(entry.get("expiry",""))
            except: return False, "Ungültiges Ablaufdatum!"
            if datetime.utcnow() > exp_dt: return False, "Key abgelaufen!"
            return True, exp_dt
    return False, "Key nicht gefunden!"

# --------------- Applied state ------------------
def load_applied_state():
    path = external_path(APPLIED_STATE_FILE)
    if not os.path.exists(path): return {}
    try:
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except: return {}
def save_applied_state(state):
    path = external_path(APPLIED_STATE_FILE)
    try:
        with open(path,"w",encoding="utf-8") as f:
            json.dump(state,f,indent=2,ensure_ascii=False)
        return True
    except: return False

def run_cmd(cmd):
    try:
        subprocess.run(cmd,shell=True,check=True)
        return True
    except: return False

# ---------------- Tweaks -------------------------
# 1) Autostart
AUTOSTART_SERVICES = ["SysMain","DiagTrack","WSearch"]
def get_service_start_type(s):
    try:
        out = subprocess.check_output(f"sc qc {s}",shell=True,stderr=subprocess.STDOUT).decode("utf-8","ignore")
        for l in out.splitlines():
            if "START_TYPE" in l.upper():
                return l.split(":")[-1].strip()
    except: return None

def apply_autostart(state):
    state.setdefault("autostart",{})
    for s in AUTOSTART_SERVICES:
        prev = get_service_start_type(s)
        state["autostart"][s] = prev
        run_cmd(f"net stop {s}")
        run_cmd(f"sc config {s} start= disabled")
    save_applied_state(state)

def undo_autostart(state):
    for s,prev in state.get("autostart",{}).items():
        run_cmd(f"sc config {s} start= auto")
        run_cmd(f"net start {s}")
    state.pop("autostart",None)
    save_applied_state(state)

# 2) Temp Cleanup
def apply_temp(state):
    state["temp"]=True
    run_cmd('powershell -Command "Get-ChildItem -Path $env:TEMP -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"')
    save_applied_state(state)
def undo_temp(state):
    state.pop("temp",None)
    save_applied_state(state)

# 3) Registry
def read_reg(keypath,val):
    try:
        out = subprocess.check_output(f'reg query "{keypath}" /v {val}',shell=True,stderr=subprocess.STDOUT).decode('utf-8','ignore')
        for l in out.splitlines():
            if val in l: return l.split()[-1]
    except: return None

def apply_registry(state):
    state.setdefault("registry",{})
    keypath = r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl"
    valname = "Win32PrioritySeparation"
    state["registry"][valname]=read_reg(keypath.replace("\\","\\\\"),valname)
    run_cmd(f'reg add "{keypath}" /v {valname} /t REG_DWORD /d 24 /f')
    save_applied_state(state)

def undo_registry(state):
    info = state.get("registry",{})
    keypath = r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl"
    valname = "Win32PrioritySeparation"
    prev = info.get(valname)
    if prev: run_cmd(f'reg add "{keypath}" /v {valname} /t REG_DWORD /d {prev} /f')
    state.pop("registry",None)
    save_applied_state(state)

# 4) Visual
def get_active_scheme():
    try:
        out = subprocess.check_output("powercfg /getactivescheme",shell=True,stderr=subprocess.STDOUT).decode("utf-8","ignore")
        import re
        m = re.search(r"([0-9a-fA-F\-]{36})",out)
        return m.group(1) if m else None
    except: return None

def apply_visual(state):
    state.setdefault("visual",{})
    prev = get_active_scheme()
    state["visual"]["prev"]=prev
    HIGH = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    run_cmd(f"powercfg /setactive {HIGH}")
    save_applied_state(state)

def undo_visual(state):
    prev = state.get("visual",{}).get("prev")
    if prev: run_cmd(f"powercfg /setactive {prev}")
    state.pop("visual",None)
    save_applied_state(state)

# 5) Game Boost
def apply_game(state):
    state["game"]={"applied_at":datetime.utcnow().isoformat()}
    run_cmd('powershell -Command "Get-Process -Name Fortnite -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = \'High\' }"')
    save_applied_state(state)
def undo_game(state):
    state.pop("game",None)
    save_applied_state(state)

# 6) Network
def read_autotune():
    try:
        out = subprocess.check_output("netsh interface tcp show global",shell=True,stderr=subprocess.STDOUT).decode("utf-8","ignore")
        for l in out.splitlines():
            if "Receive Window" in l: return l.split(":")[-1].strip()
    except: return None

def apply_network(state):
    state.setdefault("network",{})
    state["network"]["prev"]=read_autotune()
    run_cmd("netsh interface tcp set global autotuninglevel=normal")
    save_applied_state(state)

def undo_network(state):
    prev = state.get("network",{}).get("prev")
    if prev:
        val = prev.lower()
        val="disabled" if "disabled" in val else "normal" if "normal" in val else prev
        run_cmd(f"netsh interface tcp set global autotuninglevel={val}")
    state.pop("network",None)
    save_applied_state(state)

APPLY_FUNCS = {
    "autostart":(apply_autostart,undo_autostart),
    "temp":(apply_temp,undo_temp),
    "registry":(apply_registry,undo_registry),
    "visual":(apply_visual,undo_visual),
    "game":(apply_game,undo_game),
    "network":(apply_network,undo_network)
}

# ---------------- Admin & Undo All ----------------
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def undo_all_and_exit(reason="Key invalid or blacklisted"):
    state = load_applied_state()
    for k in list(APPLY_FUNCS.keys())[::-1]:
        try: APPLY_FUNCS[k][1](state)
        except: pass
    try: os.remove(external_path(APPLIED_STATE_FILE))
    except: pass
    try: messagebox.showerror("Zugriff gesperrt", reason)
    except: print(reason)
    try: webbrowser.open(KICK_URL,new=2)
    except: pass
    try: os._exit(1)
    except: sys.exit(1)

# ---------------- GUI ----------------
def start_tweaks_gui(username, expiry_dt, user_key):
    root = tk.Tk()
    root.title(f"44Service V2 - {username}")
    root.configure(bg=DARK_BG)
    root.geometry("450x520")
    root.resizable(False,False)

    tk.Label(root, text=f"Schlüssel gültig bis: {expiry_dt.strftime('%d.%m.%Y %H:%M')}",
             bg=DARK_BG, fg=TEXT_COLOR, font=("Consolas", 8)).pack(anchor="ne", padx=8,pady=6)

    def periodic_check():
        if is_key_blacklisted(user_key): undo_all_and_exit("Key wurde geblacklistet!")
        ok, info = verify_key_local(user_key)
        if not ok: undo_all_and_exit(f"Key ungültig: {info}")
        root.after(30000,periodic_check)
    root.after(30000,periodic_check)

    var_map={}
    categories = [
        ("Autostart-Optimierung","autostart"),
        ("Temporäre Dateien & Cache löschen","temp"),
        ("Registry-Optimierung / Cleaner","registry"),
        ("Visuelle Effekte / Performance-Einstellungen","visual"),
        ("Game Boost / Prozesspriorität","game"),
        ("Netzwerk-Tweaks","network")
    ]
    frame = tk.Frame(root,bg=DARK_BG)
    frame.pack(fill="both",expand=True,padx=12,pady=4)
    for text,key in categories:
        var=tk.IntVar(value=0)
        cb=tk.Checkbutton(frame,text=text,variable=var,bg=DARK_BG,fg=TEXT_COLOR,
                          selectcolor=BTN_BG,activebackground=DARK_BG,activeforeground=TEXT_COLOR,
                          font=FONT,anchor="w",justify="left",wraplength=400)
        cb.pack(fill="x",padx=6,pady=6)
        var_map[key]=var

    def on_apply():
        if is_key_blacklisted(user_key): undo_all_and_exit("Key wurde geblacklistet!")
        ok, info = verify_key_local(user_key)
        if not ok: undo_all_and_exit(f"Key ungültig: {info}")
        state=load_applied_state() or {}
        for k,(apply_fn,undo_fn) in APPLY_FUNCS.items():
            if var_map.get(k,tk.IntVar()).get(): apply_fn(state)
        messagebox.showinfo("Fertig","Ausgewählte Tweaks angewendet.")

    def on_undo():
        state=load_applied_state() or {}
        for k in list(APPLY_FUNCS.keys())[::-1]:
            try: APPLY_FUNCS[k][1](state)
            except: pass
        messagebox.showinfo("Fertig","Angewendete Tweaks rückgängig gemacht.")

    tk.Button(root,text="Apply selected tweaks",command=on_apply,
              bg=BTN_BG,fg=BTN_FG,activebackground="#3749AB",borderwidth=0,font=("Consolas",12)).pack(fill="x",padx=12,pady=(8,4))
    tk.Button(root,text="Undo applied tweaks",command=on_undo,
              bg="#6b6b6b",fg=BTN_FG,activebackground="#4b4b4b",borderwidth=0,font=("Consolas",10)).pack(fill="x",padx=12,pady=(0,12))

    if not is_admin():
        messagebox.showwarning("Admin benötigt","Einige Tweaks benötigen Adminrechte. Starte das Programm als Admin.")

    root.mainloop()

# ---------------- Login / Register ----------------
def start_login_gui():
    win=tk.Tk()
    win.title("44Service - Login/Register")
    win.configure(bg=DARK_BG)
    win.geometry("420x300")
    win.resizable(False,False)

    tk.Label(win,text="Username:",bg=DARK_BG,fg=TEXT_COLOR,font=FONT).pack(pady=(12,4))
    entry_user=tk.Entry(win,bg=INPUT_BG,fg=TEXT_COLOR,insertbackground=TEXT_COLOR,font=FONT)
    entry_user.pack(pady=2)

    tk.Label(win,text="Passwort:",bg=DARK_BG,fg=TEXT_COLOR,font=FONT).pack(pady=(8,4))
    entry_pw=tk.Entry(win,show="*",bg=INPUT_BG,fg=TEXT_COLOR,insertbackground=TEXT_COLOR,font=FONT)
    entry_pw.pack(pady=2)

    tk.Label(win,text="Key:",bg=DARK_BG,fg=TEXT_COLOR,font=FONT).pack(pady=(8,4))
    entry_key=tk.Entry(win,bg=INPUT_BG,fg=TEXT_COLOR,insertbackground=TEXT_COLOR,font=FONT)
    entry_key.pack(pady=2)

    tk.Label(win,text=f"Local HWID: {get_hwid()}",bg=DARK_BG,fg="gray",font=("Consolas",8)).pack(pady=(6,2))

    def on_register():
        u=entry_user.get().strip(); p=entry_pw.get().strip(); k=entry_key.get().strip().upper()
        if not u or not p or not k: messagebox.showerror("Fehler","Alle Felder ausfüllen!"); return
        ok,info=verify_key_local(k)
        if not ok: messagebox.showerror("Fehler",f"Key ungültig: {info}"); return
        accounts=load_accounts()
        if any(a.get("username")==u for a in accounts): messagebox.showerror("Fehler","Username existiert!"); return
        accounts.append({"username":u,"password":hash_password(p),"key":k})
        save_accounts(accounts)
        messagebox.showinfo("Erfolg","Account erstellt. Login möglich.")

    def on_login():
        u=entry_user.get().strip(); p=entry_pw.get().strip(); k=entry_key.get().strip().upper()
        if is_key_blacklisted(k): undo_all_and_exit("Key geblacklistet!")
        accounts=load_accounts()
        for a in accounts:
            if a.get("username")==u and a.get("password")==hash_password(p):
                if a.get("key","").strip().upper()!=k: messagebox.showerror("Fehler","Key stimmt nicht mit Account!"); return
                ok,info=verify_key_local(k)
                if not ok: messagebox.showerror("Fehler",info); return
                win.destroy(); start_tweaks_gui(u,info,k); return
        messagebox.showerror("Fehler","Username/Passwort nicht korrekt!")

    tk.Button(win,text="Register",command=on_register,bg=BTN_BG,fg=BTN_FG,font=FONT,borderwidth=0).pack(pady=(10,4))
    tk.Button(win,text="Login",command=on_login,bg=BTN_BG,fg=BTN_FG,font=FONT,borderwidth=0).pack()

    win.mainloop()

if __name__=="__main__":
    start_login_gui()
