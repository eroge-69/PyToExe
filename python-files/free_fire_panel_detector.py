
import os
import psutil
import time
import subprocess
import socket
import pymsgbox
import pyautogui
from datetime import datetime

emulators = ["Bluestacks", "LDPlayer", "MEmu", "Nox", "GameLoop"]
suspicious_files = [
    "modmenu.dll", "aimbot.dll", "injector.exe", "cheatengine.exe",
    "gg_mod.apk", "speedhack.dll", "libmodmenu.so",
    "hackconfig.ini", "ffmod.ini", "wallhack.exe"
]
suspicious_extensions = [".ini", ".dll", ".exe", ".so", ".apk", ".pak", ".obb"]
suspicious_processes = ["autohotkey.exe", "python.exe", "node.exe", "java.exe"]
suspicious_ports = [5555, 8888, 31337]
search_paths = ["C:\\", "D:\\", "E:\\"]
log_file = "panel_check_log.txt"
alert_enabled = True
screenshot_folder = "screenshots"

if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

def log(msg):
    time_stamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_msg = f"{time_stamp} {msg}"
    print(full_msg)
    with open(log_file, "a") as f:
        f.write(full_msg + "\n")

def alert_user(reason):
    if alert_enabled:
        pymsgbox.alert(text=f"Suspicious activity detected:\n{reason}",
                       title="⚠️ Free Fire Panel Alert")
        print('\a')
        filename = f"{screenshot_folder}/alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(filename)
        log(f"📸 Screenshot saved: {filename}")

def detect_emulator():
    for proc in psutil.process_iter(['name']):
        try:
            pname = proc.info['name'].lower()
            for emu in emulators:
                if emu.lower() in pname:
                    return emu
        except:
            continue
    return None

def scan_files():
    found = []
    for path in search_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                lower = file.lower()
                if lower in suspicious_files or any(lower.endswith(ext) for ext in suspicious_extensions):
                    full_path = os.path.join(root, file)
                    found.append(full_path)
    return found

def detect_adb_devices():
    try:
        output = subprocess.check_output("adb devices", shell=True).decode()
        if "device" in output and not "List of devices" in output:
            return True
    except:
        pass
    return False

def check_ports():
    open_ports = []
    for port in suspicious_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                open_ports.append(port)
    return open_ports

def detect_scripting_tools():
    found = []
    for proc in psutil.process_iter(['name']):
        try:
            pname = proc.info['name'].lower()
            if pname in suspicious_processes:
                found.append(pname)
        except:
            continue
    return found

def run_panel_monitor(interval=30):
    log("🛡️ Free Fire Panel Detector Started (with Alert System)...")
    while True:
        issues = []

        emulator = detect_emulator()
        if emulator:
            msg = f"Emulator detected: {emulator}"
            log(f"🛑 {msg}")
            issues.append(msg)
        else:
            log("✅ No emulator running.")

        mods = scan_files()
        if mods:
            log("🚨 Suspicious files detected:")
            for m in mods:
                log(f"➡ {m}")
            issues.append("Modded Free Fire files detected")
        else:
            log("✅ No suspicious files found.")

        if detect_adb_devices():
            log("🛑 ADB-connected device detected")
            issues.append("ADB connection (possible remote control)")
        else:
            log("✅ No ADB devices connected.")

        ports = check_ports()
        if ports:
            log(f"🛑 Suspicious ports open: {ports}")
            issues.append(f"Ports: {ports}")
        else:
            log("✅ No suspicious ports.")

        scripts = detect_scripting_tools()
        if scripts:
            log("🛑 Suspicious scripting processes: " + ", ".join(scripts))
            issues.append("Script tools running: " + ", ".join(scripts))
        else:
            log("✅ No suspicious scripting tools.")

        if issues:
            alert_reason = "\n".join(issues)
            alert_user(alert_reason)

        log("⏳ Waiting for next scan...\n")
        time.sleep(interval)

run_panel_monitor()
