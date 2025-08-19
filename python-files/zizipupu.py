import os
import sys
import time
import threading
import psutil
import subprocess
import ctypes
import keyboard
import win32con
import win32gui
import random
import string
import re
from colorama import Fore, init
from rich.console import Console
from rich.live import Live
from time import sleep

init()
shutdown_event = threading.Event()
suspended_threads = []
console = Console()
title_thread_active = True
dnscache_proc = None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        script = sys.argv[0]
        params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()

def set_random_title():
    length = random.randint(12, 21)
    title = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def title_updater():
    while title_thread_active:
        set_random_title()
        time.sleep(0.05)

def resize_console():
    os.system('mode con: cols=70 lines=20')

def make_transparent():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        win32gui.SetWindowLong(hwnd, -20, win32gui.GetWindowLong(hwnd, -20) | 0x80000)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 200, 2)

class UIManager:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def setup_console():
        resize_console()
        make_transparent()
        UIManager.clear_screen()
        title_thread = threading.Thread(target=title_updater, daemon=True)
        title_thread.start()

class ProcessManager:
    @staticmethod
    def kill_process(process_name):
        try:
            subprocess.run(f"taskkill /f /im {process_name}", shell=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    @staticmethod
    def is_process_running(process_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False

class ServiceManager:
    @staticmethod
    def stop_service(service_name):
        try:
            subprocess.check_call(['sc', 'stop', service_name],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def start_service(service_name):
        try:
            subprocess.check_call(['sc', 'start', service_name],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

def show_countdown(seconds):
    console = Console()
    with Live(console=console, refresh_per_second=10) as live:
        for remaining in range(seconds, 0, -1):
            minutes, secs = divmod(remaining, 60)
            live.update(f"> BYPASSING, JOIN THE MATCH IMMEDIATELY WHEN THE GAME STARTS | {minutes:02d}:{secs:02d}")
            sleep(1)

def l0g(msg, type='info'):
    if type == 'info':
        print(Fore.CYAN + '[+] ' + msg)
    elif type == 'success':
        print(Fore.GREEN + '[+] ' + msg)
    elif type == 'warn':
        print(Fore.YELLOW + '[!] ' + msg)
    elif type == 'error':
        print(Fore.RED + '[!] ' + msg)
    elif type == 'step':
        print(Fore.BLUE + '[>] ' + msg)

def find_process(name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == name:
            return proc
    return None

def wait_for_valorant():
    l0g('Waiting for Valorant', 'info')
    while True:
        proc = find_process('vgc.exe')
        if proc:
            l0g('Valorant Found.', 'success')
            return
        time.sleep(1)

def resume_suspended_threads():
    global dnscache_proc
    try:
        if dnscache_proc:
            dnscache_proc.resume()
    except Exception as e:
        l0g(f"Resume failed: {e}", "error")

def suspend_dns_cache():
    global dnscache_proc
    try:
        result = subprocess.run('tasklist /svc /fi "imagename eq svchost.exe"', shell=True, capture_output=True, text=True)
        lines = result.stdout.splitlines()

        for line in lines:
            if "Dnscache" in line:
                match = re.search(r'\b(\d+)\b', line)
                if match:
                    pid = int(match.group(1))
                    try:
                        dnscache_proc = psutil.Process(pid)
                        dnscache_proc.suspend()
                        return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        l0g("Could not suspend Dnscache process, (might be AccessDenied)", 'error')
                        return False

        l0g("Dnscache process not found, where is it?", 'warn')
        return False

    except Exception as e:
        l0g(f"Exception in suspend_dns_cache: {str(e)}", 'error')
        return False

def bypass_process():
    ServiceManager.stop_service("vgc")
    ProcessManager.kill_process("vgtray.exe")
    wait_for_valorant()
    show_countdown(90)
    if not suspend_dns_cache():
        l0g("Suspend failed.", "error")
        return
    l0g("BYPASS COMPLETE BRO! IF YOU GET A CONNECTION ERROR OR SOMETHING, PRESS F12", "step")
    keyboard.wait("f12")
    keyboard.add_hotkey("f12", resume_suspended_threads)
    resume_suspended_threads()
    ProcessManager.kill_process("VALORANT.exe")
    ProcessManager.kill_process("VALORANT-Win64-Shipping.exe")
    ProcessManager.kill_process("vgc.exe")
    os.system(f"netsh winsock reset >nul 2>&1")
    os.system(f"netsh int ip reset >nul 2>&1")
    os.system(f"ipconfig /release >nul 2>&1")
    os.system(f"ipconfig /renew >nul 2>&1")
    os.system(f"ipconfig /flushdns >nul 2>&1")
    os.system(f"netsh winhttp reset proxy >nul 2>&1")
    os.system("cls")

def main():
    run_as_admin()
    UIManager.setup_console()
    try:
        while True:
            bypass_process()
    except KeyboardInterrupt:
        global title_thread_active
        title_thread_active = False

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        title_thread_active = False
        print(f'[ERROR] {e}')
