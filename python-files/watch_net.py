import time
import requests
import subprocess
import psutil

# Path to your existing login script
LOGIN_SCRIPT = "C:/Users/Hp/Desktop/net.py"

def is_connected():
    """Check if internet is working by pinging Google."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

def kill_chrome():
    """Force close Chrome."""
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] and "chrome.exe" in proc.info['name'].lower():
            try:
                proc.kill()
            except Exception:
                pass

if __name__ == "__main__":
    while True:
        if not is_connected():
            print("⚠️ Internet down → restarting login script...")
            # Close Chrome if it is running (so we get a fresh login)
            kill_chrome()
            # Launch your login script again
            subprocess.Popen(["python", LOGIN_SCRIPT])
            time.sleep(30)  # wait 30 sec before checking again
        else:
            print("✅ Internet is up")
        time.sleep(10)  # check every 10 sec
