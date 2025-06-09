import subprocess
import sys
import time
import os

PROXY_PORT = 8888
CHROMIUM_PATH = r"E:\prox\chromium\bin\chrome.exe"  # Change to your Chromium path

def start_proxy():
    # Start the proxy.py server on the specified port
    # --hostname 127.0.0.1 to bind locally, you can change as needed
    proc = subprocess.Popen([
        sys.executable, "-m", "proxy", 
        "--hostname", "127.0.0.1", 
        "--port", str(PROXY_PORT)
    ])
    return proc

def open_chromium_with_proxy():
    proxy_server = f"http://127.0.0.1:{PROXY_PORT}"
    args = [
        CHROMIUM_PATH,
        f"--proxy-server={proxy_server}",
        "https://www.google.com"  # Default startup page
    ]
    subprocess.Popen(args)

def main():
    proxy_proc = start_proxy()
    print(f"Proxy server started on port {PROXY_PORT}")

    # Give proxy some time to start
    time.sleep(2)

    open_chromium_with_proxy()
    print("Chromium opened with proxy")

    try:
        # Keep the script running while proxy is alive
        proxy_proc.wait()
    except KeyboardInterrupt:
        print("Stopping proxy...")
        proxy_proc.terminate()
        proxy_proc.wait()

if __name__ == "__main__":
    main()
