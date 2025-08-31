
# KoxkOptimizer Next‑Gen DIRECT GUI
# Requisiti: Windows, Python 3.8+, esecuzione come Amministratore
import os, sys, subprocess, ctypes, time, shutil
from pathlib import Path

# --- GUI stack: preferisci CustomTkinter; fallback a Tkinter ---
try:
    import customtkinter as ctk
    GUI_LIB = "customtkinter"
except Exception:
    import tkinter as ctk  # fallback ridotto
    GUI_LIB = "tkinter"
    from tkinter import messagebox

APP_TITLE = "Koxk Optimizer — DIRECT Next‑Gen"
LOGO_PATH = os.path.join(os.path.dirname(__file__), "KoxkOptimizer.ico")

# ---------- Helper di privilegio admin ----------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def relaunch_as_admin():
    params = " ".join([f'"{a}"' for a in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

# ---------- Runner utility ----------
def run(cmd, shell=True):
    """Esegue cmd e ritorna (code, out, err)"""
    try:
        proc = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def reg_add(path, name, typ, data):
    return run(f'reg add "{path}" /v {name} /t {typ} /d {data} /f')

def reg_delete(path):
    return run(f'reg delete "{path}" /f')

def service_config(name, start):
    return run(f'sc config "{name}" start={start}')

def service_stop(name):
    return run(f'sc stop "{name}"')

def service_start(name):
    return run(f'sc start "{name}"')

def bcdedit_set(key, value):
    return run(f'bcdedit /set {key} {value}')

def netsh(cmd):
    return run(f'netsh {cmd}')

def info(msg):
    print("[INFO]", msg)

# ---------- Blocchi di tweak (reali) ----------
def ultimate_performance():
    run('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61')
    run('powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61')
    run('powercfg -change -monitor-timeout-ac 0')
    run('powercfg -change -disk-timeout-ac 0')
    run('powercfg -change -standby-timeout-ac 0')
    run('powercfg -change -hibernate-timeout-ac 0')

def disable_bloat_services():
    # Safe-ish: meno servizi Xbox/telemetria
    for s in ["SysMain","DiagTrack","XblGameSave","XboxGipSvc","XboxNetApiSvc","MapsBroker","Fax","RemoteRegistry"]:
        service_stop(s)
        service_config(s, "disabled")

def enable_default_services():
    for s in ["SysMain","DiagTrack","XblGameSave","XboxGipSvc","XboxNetApiSvc","MapsBroker","Fax","RemoteRegistry"]:
        service_config(s, "auto")

def gamebar_off():
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "ShowStartupPanel", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", "REG_DWORD", 0)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", "REG_DWORD", 0)

def mouse_no_accel():
    reg_add(r"HKCU\Control Panel\Mouse", "MouseSpeed", "REG_SZ", 0)
    reg_add(r"HKCU\Control Panel\Mouse", "MouseThreshold1", "REG_SZ", 0)
    reg_add(r"HKCU\Control Panel\Mouse", "MouseThreshold2", "REG_SZ", 0)

def timer_kernel():
    bcdedit_set("useplatformtick", "yes")
    bcdedit_set("disabledynamictick", "yes")
    bcdedit_set("tscsyncpolicy", "Enhanced")

def network_low_ping():
    netsh("int tcp set global autotuninglevel=disabled")
    netsh("int tcp set global chimney=disabled")
    netsh("int tcp set global rss=enabled")
    netsh("int tcp set global ecncapability=disabled")
    netsh("int tcp set global timestamps=disabled")

def background_apps_off():
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", "REG_DWORD", 1)

def prefetch_clean():
    run(r'del /q /f %SystemRoot%\Prefetch\*.*')

def reset_defaults():
    enable_default_services()
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", "REG_DWORD", 1)

def dns_google():
    netsh('interface ip set dns "Ethernet" static 8.8.8.8')
    netsh('interface ip add dns "Ethernet" 8.8.4.4 index=2')

def dns_cloudflare():
    netsh('interface ip set dns "Ethernet" static 1.1.1.1')
    netsh('interface ip add dns "Ethernet" 1.0.0.1 index=2')

def dns_reset():
    netsh('interface ip set dns "Ethernet" dhcp')

def defender_off():
    # richiede che la Tamper Protection sia off dalle impostazioni
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware", "REG_DWORD", 1)
    service_stop("WinDefend")
    service_config("WinDefend", "disabled")

def defender_on():
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware", "REG_DWORD", 0)
    service_config("WinDefend", "auto")
    service_start("WinDefend")

def wupdate_off():
    service_stop("wuauserv")
    service_config("wuauserv", "disabled")

def wupdate_on():
    service_config("wuauserv", "auto")
    service_start("wuauserv")

def search_off():
    service_stop("WSearch")
    service_config("WSearch", "disabled")

def search_on():
    service_config("WSearch", "delayed-auto")
    service_start("WSearch")

def nvidia_perf_tweaks():
    # Nota: non tutti i driver leggono queste chiavi. Serve riavvio/ri-logon.
    reg_add(r"HKCU\Software\NVIDIA Corporation\Global\NVTweak", "LowLatencyMode", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\NVIDIA Corporation\Global\NVTweak", "PowerMizerEnable", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\NVIDIA Corporation\Global\NVTweak", "VSync", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\NVIDIA Corporation\Global\NVTweak", "FlatPanelScaling", "REG_DWORD", 3)

def keyboard_low_delay():
    # Filter keys tuning (valori conservativi)
    reg_add(r"HKCU\Control Panel\Accessibility\Keyboard Response","AutoRepeatDelay","REG_SZ",200)
    reg_add(r"HKCU\Control Panel\Accessibility\Keyboard Response","AutoRepeatRate","REG_SZ",10)

def stretched(resx, resy):
    # Fortnite GameUserSettings.ini
    user = os.environ.get("USERNAME","")
    ini = Path.home() / "AppData/Local/FortniteGame/Saved/Config/WindowsClient/GameUserSettings.ini"
    try:
        ini.parent.mkdir(parents=True, exist_ok=True)
        if ini.exists():
            content = ini.read_text(errors="ignore")
        else:
            content = ""
        # Inserisci/aggiorna risoluzione
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if "ResolutionSizeX=" in line:
                line = f"ResolutionSizeX={resx}"
            elif "ResolutionSizeY=" in line:
                line = f"ResolutionSizeY={resy}"
            elif "LastUserConfirmedResolutionSizeX=" in line:
                line = f"LastUserConfirmedResolutionSizeX={resx}"
            elif "LastUserConfirmedResolutionSizeY=" in line:
                line = f"LastUserConfirmedResolutionSizeY={resy}"
            new_lines.append(line)
        if not new_lines:
            new_lines = [
                f"ResolutionSizeX={resx}",
                f"ResolutionSizeY={resy}",
                f"LastUserConfirmedResolutionSizeX={resx}",
                f"LastUserConfirmedResolutionSizeY={resy}",
            ]
        ini.write_text("\n".join(new_lines), encoding="utf-8")
    except Exception as e:
        info(f"Errore GameUserSettings: {e}")
    # scaling GPU
    nvidia_perf_tweaks()

# --- Modalità composte ---
def mode_school():
    reset_defaults()
    search_on()
    defender_on()
    wupdate_on()

def mode_gaming():
    ultimate_performance()
    disable_bloat_services()
    gamebar_off()
    mouse_no_accel()
    timer_kernel()
    network_low_ping()
    background_apps_off()
    nvidia_perf_tweaks()

def mode_ultra():
    mode_gaming()
    keyboard_low_delay()
    prefetch_clean()

def mode_inferno():
    # ATTENZIONE: Defender/Update OFF
    mode_ultra()
    defender_off()
    wupdate_off()
    search_off()

def mode_apocalypsis():
    # Spinge ancora di più: molti servizi off (uso a proprio rischio)
    mode_inferno()
    for s in ["BITS","LanmanServer","PrintSpooler","TabletInputService"]:
        service_stop(s)
        service_config(s, "disabled")

# -------- GUI --------
if GUI_LIB == "customtkinter":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk if GUI_LIB=="customtkinter" else ctk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        try:
            self.iconbitmap(LOGO_PATH)
        except Exception:
            pass
        self.geometry("1024x700")

        # Notebook / Tabs
        if GUI_LIB=="customtkinter":
            tabview = ctk.CTkTabview(self)
            tabview.pack(expand=True, fill="both", padx=12, pady=12)
            tabs = {
                "Modalità": tabview.add("Modalità"),
                "Tweak": tabview.add("Tweak"),
                "Rete & Ping": tabview.add("Rete & Ping"),
                "Stretched": tabview.add("Stretched"),
                "NVIDIA": tabview.add("NVIDIA"),
                "README": tabview.add("README"),
            }
        else:
            from tkinter import ttk
            tabview = ttk.Notebook(self)
            tabview.pack(expand=True, fill="both")
            tabs = {}
            for name in ["Modalità","Tweak","Rete & Ping","Stretched","NVIDIA","README"]:
                frame = ctk.Frame(tabview)
                tabview.add(frame, text=name)
                tabs[name] = frame

        self.build_modes_tab(tabs["Modalità"])
        self.build_tweaks_tab(tabs["Tweak"])
        self.build_network_tab(tabs["Rete & Ping"])
        self.build_stretched_tab(tabs["Stretched"])
        self.build_nvidia_tab(tabs["NVIDIA"])
        self.build_readme_tab(tabs["README"])

    def make_btn(self, parent, text, cmd):
        if GUI_LIB=="customtkinter":
            b = ctk.CTkButton(parent, text=text, command=cmd)
        else:
            b = ctk.Button(parent, text=text, command=cmd)
        b.pack(pady=6, padx=8, anchor="w")
        return b

    def build_modes_tab(self, tab):
        self.make_btn(tab, "Modalità Scuola (compatibile)", mode_school)
        self.make_btn(tab, "Modalità Gaming", mode_gaming)
        self.make_btn(tab, "Modalità Gaming ULTRA", mode_ultra)
        self.make_btn(tab, "KOXK INFERNO MODE 🔥 (Defender/Update OFF)", mode_inferno)
        self.make_btn(tab, "APOCALYPSIS MODE ☠️ (Uso a rischio)", mode_apocalypsis)

    def build_tweaks_tab(self, tab):
        self.make_btn(tab, "Ultimate Performance Plan", ultimate_performance)
        self.make_btn(tab, "Disattiva servizi inutili", disable_bloat_services)
        self.make_btn(tab, "Game Bar / DVR OFF", gamebar_off)
        self.make_btn(tab, "No accelerazione mouse", mouse_no_accel)
        self.make_btn(tab, "Timer kernel (bcdedit)", timer_kernel)
        self.make_btn(tab, "Rete low ping (netsh)", network_low_ping)
        self.make_btn(tab, "App background OFF", background_apps_off)
        self.make_btn(tab, "Pulisci Prefetch", prefetch_clean)
        self.make_btn(tab, "RESET predefiniti", reset_defaults)
        self.make_btn(tab, "Riattiva Defender", defender_on)
        self.make_btn(tab, "Disattiva Defender", defender_off)
        self.make_btn(tab, "WinUpdate ON", wupdate_on)
        self.make_btn(tab, "WinUpdate OFF", wupdate_off)
        self.make_btn(tab, "Ricerca Windows ON", search_on)
        self.make_btn(tab, "Ricerca Windows OFF", search_off)
        self.make_btn(tab, "Keyboard low delay (FilterKeys)", keyboard_low_delay)

    def build_network_tab(self, tab):
        self.make_btn(tab, "Imposta DNS Google", dns_google)
        self.make_btn(tab, "Imposta DNS Cloudflare", dns_cloudflare)
        self.make_btn(tab, "DNS Automatico (DHCP)", dns_reset)
        self.make_btn(tab, "netsh int ip reset", lambda: netsh("int ip reset"))
        self.make_btn(tab, "ipconfig /flushdns", lambda: run("ipconfig /flushdns"))
        self.make_btn(tab, "Mostra MTU consigli (1472+28 = 1500)", lambda: None)

    def build_stretched_tab(self, tab):
        self.make_btn(tab, "Fortnite 1750x1080 + GPU scaling", lambda: stretched(1750,1080))
        self.make_btn(tab, "Fortnite 1440x1080 + GPU scaling", lambda: stretched(1440,1080))

    def build_nvidia_tab(self, tab):
        self.make_btn(tab, "NVIDIA: Low Latency + Prestazioni + No VSync", nvidia_perf_tweaks)

    def build_readme_tab(self, tab):
        text = (
            "Koxk Optimizer — DIRECT\n\n"
            "Questa versione applica davvero i tweak.\n"
            "Usa le modalità per profilo completo oppure i pulsanti singoli.\n"
            "Inferno/Apocalypsis disattivano Defender/Update.\n"
            "Per ripristinare usa i pulsanti in Tweak (Riattiva Defender/Update).\n"
        )
        if GUI_LIB=="customtkinter":
            lbl = ctk.CTkLabel(tab, text=text, justify="left")
            lbl.pack(padx=12, pady=12, anchor="nw")
        else:
            import tkinter as tk
            lbl = tk.Label(tab, text=text, justify="left", anchor="nw")
            lbl.pack(padx=12, pady=12, anchor="nw")

if __name__ == "__main__":
    if not is_admin():
        # Rilancia come Admin
        relaunch_as_admin()
        sys.exit(0)
    app = App()
    app.mainloop()
