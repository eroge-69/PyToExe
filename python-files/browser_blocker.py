import psutil
import time
import pygetwindow as gw

BLOCKED_KEYWORD = "www.facebook.com"
BROWSERS = ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"]

def match_cmdline(cmdline):
    return BLOCKED_KEYWORD.lower() in ' '.join(cmdline).lower()

def match_window_titles():
    for window in gw.getWindowsWithTitle(""):
        try:
            title = window.title.lower()
            if BLOCKED_KEYWORD in title:
                pid = window._hWndToPid(window._hWnd)
                proc = psutil.Process(pid)
                if proc.name().lower() in BROWSERS:
                    proc.kill()
        except Exception:
            continue

def monitor():
    while True:
        # Check by command-line
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'].lower() in BROWSERS and match_cmdline(proc.info['cmdline']):
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Check by window title
        match_window_titles()
        time.sleep(5)

if __name__ == "__main__":
    monitor()
