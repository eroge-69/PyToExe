#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ein einfacher Sit/Stand‑Timer mit Bestätigungsdialog, Settings und optionalem Autostart.
Plattformen: Windows, macOS, Linux (X11/Wayland).
Nur Standardbibliothek (tkinter); Autostart-Installation nutzt winreg/Dateien je OS.

Startparameter:
  --install-autostart   richtet Autostart für die aktuelle ausführbare Datei ein
  --remove-autostart    entfernt den Autostart-Eintrag

Speichert Einstellungen in: ~/.sitstand_timer/settings.json
"""

import json
import os
import sys
import time
import platform
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- Konstanten & Pfade ----------
APP_NAME = "SitStandTimer"
HUMAN_APP_NAME = "Sit/Stand Timer"
CONFIG_DIR = Path.home() / ".sitstand_timer"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "stand_minutes": 45,   # Standard: 45 Minuten stehen
    "sit_minutes": 15,     # Standard: 15 Minuten sitzen
    "start_phase": "Stand",  # oder "Sitz"
    "autostart": False
}

# ---------- Hilfsfunktionen für Einstellungen ----------

def load_settings():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()



def save_settings(data):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Fehler", f"Einstellungen konnten nicht gespeichert werden: {e}")


# ---------- Autostart (optional) ----------

def _current_exec_path() -> str:
    """Gibt den Pfad zur aktuellen ausführbaren Datei/Script zurück."""
    if getattr(sys, 'frozen', False):  # PyInstaller/Bundle
        return sys.executable
    return os.path.abspath(sys.argv[0])


def install_autostart():
    """Richtet Autostart für den aktuellen Benutzer ein."""
    settings = load_settings()
    settings["autostart"] = True
    save_settings(settings)

    system = platform.system()
    exec_path = _current_exec_path()

    try:
        if system == "Windows":
            import winreg  # Standardbibliothek auf Windows
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exec_path}"')
            return True, "Autostart über Registry eingerichtet."
        elif system == "Darwin":  # macOS via LaunchAgents
            agents_dir = Path.home() / "Library" / "LaunchAgents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            plist_path = agents_dir / f"com.user.{APP_NAME.lower()}.plist"
            plist_content = f"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.user.{APP_NAME.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exec_path}</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><false/>
</dict>
</plist>
""".strip()
            plist_path.write_text(plist_content, encoding="utf-8")
            return True, f"Autostart über LaunchAgent angelegt: {plist_path}"
        else:  # Linux/BSD – Freedesktop .desktop
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            desktop_path = autostart_dir / f"{APP_NAME}.desktop"
            desktop_content = f"""
[Desktop Entry]
Type=Application
Name={HUMAN_APP_NAME}
Exec="{exec_path}"
X-GNOME-Autostart-enabled=true
""".strip()
            desktop_path.write_text(desktop_content, encoding="utf-8")
            return True, f"Autostart-Datei erstellt: {desktop_path}"
    except Exception as e:
        return False, f"Autostart konnte nicht eingerichtet werden: {e}"


def remove_autostart():
    settings = load_settings()
    settings["autostart"] = False
    save_settings(settings)

    system = platform.system()
    try:
        if system == "Windows":
            import winreg
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
            return True, "Autostart entfernt."
        elif system == "Darwin":
            plist_path = Path.home() / "Library" / "LaunchAgents" / f"com.user.{APP_NAME.lower()}.plist"
            if plist_path.exists():
                plist_path.unlink()
            return True, "LaunchAgent entfernt."
        else:
            desktop_path = Path.home() / ".config" / "autostart" / f"{APP_NAME}.desktop"
            if desktop_path.exists():
                desktop_path.unlink()
            return True, "Autostart-Datei entfernt."
    except Exception as e:
        return False, f"Autostart konnte nicht entfernt werden: {e}"


# ---------- Hauptanwendung ----------

class SitStandTimerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(HUMAN_APP_NAME)
        self.geometry("400x250")
        self.resizable(True, True)

        # Canvas + Scrollbar für Scrollbarkeit
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.settings = load_settings()
        self.current_phase = self.settings.get("start_phase", "Stand")
        self.remaining = self._phase_seconds(self.current_phase)
        self.running = False
        self._timer_job = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- UI ----------
    def _build_ui(self):
        pad = 10
        frm = ttk.Frame(self.scrollable_frame, padding=pad)
        frm.pack(fill="both", expand=True)

        self.phase_var = tk.StringVar(value=f"Aktuelle Phase: {self.current_phase}")
        self.time_var = tk.StringVar(value=self._format_time(self.remaining))

        lbl_phase = ttk.Label(frm, textvariable=self.phase_var, font=("Segoe UI", 14, "bold"))
        lbl_phase.pack(pady=(0, 6))
        lbl_time = ttk.Label(frm, textvariable=self.time_var, font=("Consolas", 28))
        lbl_time.pack(pady=(0, 10))

        btns = ttk.Frame(frm)
        btns.pack(pady=4)
        self.btn_start = ttk.Button(btns, text="Start", command=self.start)
        self.btn_pause = ttk.Button(btns, text="Pause", command=self.pause, state=tk.DISABLED)
        self.btn_skip = ttk.Button(btns, text="Phase überspringen", command=self.skip_phase)
        self.btn_start.grid(row=0, column=0, padx=4)
        self.btn_pause.grid(row=0, column=1, padx=4)
        self.btn_skip.grid(row=0, column=2, padx=4)

        sep = ttk.Separator(frm)
        sep.pack(fill="x", pady=8)

        cfg = ttk.Frame(frm)
        cfg.pack(fill="x")
        ttk.Label(cfg, text="Stehphase (min)").grid(row=0, column=0, sticky="w")
        ttk.Label(cfg, text="Sitzphase (min)").grid(row=1, column=0, sticky="w")
        self.spin_stand = tk.Spinbox(cfg, from_=1, to=240, width=5)
        self.spin_sit = tk.Spinbox(cfg, from_=1, to=240, width=5)
        self.spin_stand.delete(0, "end"); self.spin_stand.insert(0, str(self.settings["stand_minutes"]))
        self.spin_sit.delete(0, "end"); self.spin_sit.insert(0, str(self.settings["sit_minutes"]))
        self.spin_stand.grid(row=0, column=1, padx=6, pady=3, sticky="w")
        self.spin_sit.grid(row=1, column=1, padx=6, pady=3, sticky="w")

        # Zusätzliche Speichertaste direkt neben den Spinboxen
        btn_save_times = ttk.Button(cfg, text="Einstellungen speichern", command=self.save_settings)
        btn_save_times.grid(row=0, column=2, rowspan=2, padx=8, pady=3, sticky="ns")

        self.autostart_var = tk.BooleanVar(value=self.settings.get("autostart", False))
        self.chk_autostart = ttk.Checkbutton(cfg, text="Beim Anmelden automatisch starten", variable=self.autostart_var, command=self._toggle_autostart)
        self.chk_autostart.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6,0))

        for i in range(2):
            cfg.grid_columnconfigure(i, weight=1)

    # ---------- Timer-Logik ----------
    def _phase_seconds(self, phase: str) -> int:
        mins = self.settings["stand_minutes"] if phase == "Stand" else self.settings["sit_minutes"]
        return int(mins) * 60

    @staticmethod
    def _format_time(seconds: int) -> str:
        m, s = divmod(max(0, seconds), 60)
        return f"{m:02d}:{s:02d}"

    def start(self):
        self.running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL)
        self._tick()

    def pause(self):
        self.running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED)
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

    def skip_phase(self):
        if self.running:
            self.pause()
        self._switch_phase(confirm=False)

    def _tick(self):
        if not self.running:
            return
        self.time_var.set(self._format_time(self.remaining))
        if self.remaining <= 0:
            self.running = False
            self.btn_start.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            self._on_phase_finished()
            return
        self.remaining -= 1
        self._timer_job = self.after(1000, self._tick)

    def _on_phase_finished(self):
        # Akustischer Hinweis (optional, plattformunabhängig via Bell)
        try:
            self.bell()
        except Exception:
            pass
        phase_text = "Steh" if self.current_phase == "Stand" else "Sitz"
        next_phase = "Sitz" if self.current_phase == "Stand" else "Stand"
        msg = (f"Die {phase_text}phase ist abgelaufen.\n\n"
               f"Bitte wechsle jetzt zu: {next_phase}.\n\n"
               "Bestätige mit \"Weiter\", um den nächsten Timer zu starten.")
        if messagebox.askokcancel("Phase beendet", msg, icon="info"):
            self._switch_phase(confirm=True)
        else:
            # Nutzer möchte noch warten; wir zeigen 60s Snooze.
            snooze = 60
            self.remaining = snooze
            self.phase_var.set(f"Snooze – nächste Phase: {next_phase}")
            self.running = True
            self.btn_start.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            self._tick()

    def _switch_phase(self, confirm: bool):
        self.current_phase = "Sitz" if self.current_phase == "Stand" else "Stand"
        self.phase_var.set(f"Aktuelle Phase: {self.current_phase}")
        self.remaining = self._phase_seconds(self.current_phase)
        self.time_var.set(self._format_time(self.remaining))
        if confirm:
            self.start()

    # ---------- Einstellungen ----------
    def save_settings(self):
        try:
            stand = int(self.spin_stand.get())
            sit = int(self.spin_sit.get())
            if stand <= 0 or sit <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Ungültige Eingabe", "Bitte ganze Minuten > 0 angeben.")
            return

        self.settings["stand_minutes"] = stand
        self.settings["sit_minutes"] = sit
        save_settings(self.settings)

        # Phase überspringen wie beim Button "Phase überspringen"
        self.skip_phase()

    def _toggle_autostart(self):
        if self.autostart_var.get():
            ok, info = install_autostart()
        else:
            ok, info = remove_autostart()
        if not ok:
            messagebox.showwarning("Autostart", info)
        else:
            # Erfolg – Status bereits in install/remove gespeichert
            messagebox.showinfo("Autostart", info)

    def on_close(self):
        if self.running and messagebox.askyesno("Beenden?", "Der Timer läuft noch. Wirklich beenden?") is False:
            return
        self.destroy()


# ---------- CLI-Handler ----------

def main():
    if "--install-autostart" in sys.argv:
        ok, info = install_autostart()
        print("OK" if ok else "FEHLER", "-", info)
        return
    if "--remove-autostart" in sys.argv:
        ok, info = remove_autostart()
        print("OK" if ok else "FEHLER", "-", info)
        return

    app = SitStandTimerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
