"""
ShadowGuard PRO 2.0 - Safe Edition
Automatiserad scanner + builder + autofix (SIMULATED - SAFE)
"""

import os
import sys
import time
import subprocess
import random
try:
    import PySimpleGUI as sg
except Exception:
    sg = None

PROJECT_FILE = "shadowguard_pro.py"
MALWARE_SIGNATURES = ["virus.exe", "trojan.dll", "worm.scr", "spyware.dat"]
QUARANTINE = []

def ensure_gui_available():
    if sg is None:
        print("PySimpleGUI not found. Please install with: pip install PySimpleGUI")
        return False
    return True

def log_print(window, msg):
    if window is not None:
        try:
            window['-LOG-'].print(msg)
        except Exception:
            pass
    print(msg)

def check_and_install_packages(window=None):
    """Install missing packages if possible (user consent recommended)."""
    import pkg_resources
    installed = {pkg.key for pkg in pkg_resources.working_set}
    changed = False
    for pkg in ["PySimpleGUI", "pyinstaller"]:
        if pkg.lower() not in installed:
            log_print(window, f"[INFO] Paket saknas: {pkg} — försöker installera...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                changed = True
            except Exception as e:
                log_print(window, f"[WARN] Kunde inte installera {pkg}: {e}")
        else:
            log_print(window, f"[OK] Paket redan installerat: {pkg}")
    return changed

def scan_files(window=None):
    log_print(window, "[SCAN] Startar filskanning (SIMULATED)...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            # only simulate; do not modify real files
            if file in MALWARE_SIGNATURES:
                QUARANTINE.append(os.path.join(root, file))
                log_print(window, f"[THREAT] Hot upptäckt (simulated): {file} → lagras i simul. karantän")
            else:
                log_print(window, f"[SAFE] {os.path.join(root, file)}")
    log_print(window, "[SCAN] Klar (SIMULATED). Ingen fil ändrad.")

def scan_and_fix_files(window=None):
    """Scan .py files and fix common, non-destructive issues (like stray backslash-escapes in docstrings)."""
    fixes = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    fixed = content.replace('\"""', '"""')
                    if content != fixed:
                        # only rewrite if difference and file is writable
                        try:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(fixed)
                            fixes += 1
                            log_print(window, f"[FIX] Rättade docstring-escape i: {filepath}")
                        except Exception as e:
                            log_print(window, f"[WARN] Kunde inte skriva fil {filepath}: {e}")
                except Exception as e:
                    log_print(window, f"[WARN] Kunde inte läsa fil {filepath}: {e}")
    log_print(window, f"[FIX] Klar. Antal filer ändrade: {fixes}")
    return fixes

def build_exe(window=None):
    """Build shadowguard_pro.py into a single EXE using PyInstaller."""
    if not os.path.exists(PROJECT_FILE):
        log_print(window, f"[ERROR] Hittar inte projektfilen: {PROJECT_FILE}")
        return False
    log_print(window, "[BUILD] Startar PyInstaller (this may take a minute)...")
    try:
        subprocess.check_call([sys.executable, '-m', 'PyInstaller', '--onefile', '--noconsole', PROJECT_FILE])
        log_print(window, '[DONE] Build klar. Kolla dist/ katalogen.')
        return True
    except Exception as e:
        log_print(window, f"[ERROR] Bygg misslyckades: {e}")
        return False

def create_build_launcher():
    layout = [
        [sg.Text('ShadowGuard PRO 2.0 - AutoFix & Build (SAFE simulation mode)')],
        [sg.Button('Check & Install Packages'), sg.Button('Scan (Simulated)'), sg.Button('Fix .py files'), sg.Button('Build EXE'), sg.Button('Show Quarantine'), sg.Button('Exit')],
        [sg.HorizontalSeparator()],
        [sg.Multiline(size=(90,20), key='-LOG-', autoscroll=True)]
    ]
    window = sg.Window('ShadowGuard PRO 2.0', layout, finalize=True, resizable=True)
    return window

def run_gui():
    if not ensure_gui_available():
        return
    window = create_build_launcher()
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Check & Install Packages':
            check_and_install_packages(window=window)
        if event == 'Scan (Simulated)':
            scan_files(window=window)
        if event == 'Fix .py files':
            scan_and_fix_files(window=window)
        if event == 'Build EXE':
            ok = build_exe(window=window)
            if ok:
                sg.popup('Build finished', 'Check dist\\ for the executable.')
        if event == 'Show Quarantine':
            sg.popup('Simulated Quarantine', '\n'.join(QUARANTINE) if QUARANTINE else 'No simulated items.')
    window.close()

if __name__ == '__main__':
    run_gui()
