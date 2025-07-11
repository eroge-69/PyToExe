import tkinter as tk
from tkinter import messagebox
import threading
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from urllib.parse import urlparse, parse_qs
from fake_useragent import UserAgent

# Daftar proxy yang diberikan
PROXIES = [
    "184.174.44.114:6540:dmproxy57:dmproxy57",
    "31.58.20.107:5791:dmproxy57:dmproxy57",
    "107.173.93.106:6060:dmproxy57:dmproxy57",
    "192.177.103.41:6534:dmproxy57:dmproxy57",
    "208.70.11.183:6264:dmproxy57:dmproxy57",
    "45.38.111.61:5976:dmproxy57:dmproxy57",
    "92.113.231.229:7314:dmproxy57:dmproxy57",
    "92.113.231.246:7331:dmproxy57:dmproxy57",
    "92.113.231.194:7279:dmproxy57:dmproxy57",
    "92.113.231.154:7239:dmproxy57:dmproxy57",
]

# List untuk menyimpan instance driver
drivers = []

def open_browser(proxy, video_id):
    try:
        ip, port, user, passw = proxy.split(":")
        proxy_url = f"http://{user}:{passw}@{ip}:{port}"
        options = {
            'proxy': {
                'http': proxy_url,
                'https': proxy_url,
                'no_proxy': 'localhost,127.0.0.1'
            }
        }
        ua = UserAgent()
        user_agent = ua.chrome  # User agent acak kompatibel dengan Chrome
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            seleniumwire_options=options,
            options=chrome_options
        )
        drivers.append(driver)
        url = f"https://www.youtube.com/watch?v={video_id}&list={video_id}"
        driver.get(url)
    except Exception as e:
        print(f"Error dengan proxy {proxy}: {e}")

def start():
    url = entry.get()
    if not url:
        messagebox.showerror("Error", "Masukkan URL YouTube")
        return
    parsed = urlparse(url)
    if parsed.netloc != "www.youtube.com" or parsed.path != "/watch":
        messagebox.showerror("Error", "URL YouTube tidak valid")
        return
    query = parse_qs(parsed.query)
    video_id = query.get("v", [None])[0]
    if not video_id:
        messagebox.showerror("Error", "Tidak dapat mengekstrak ID video")
        return
    for proxy in PROXIES:
        t = threading.Thread(target=open_browser, args=(proxy, video_id))
        t.start()

def stop():
    for driver in drivers:
        try:
            driver.quit()
        except:
            pass
    drivers.clear()
    messagebox.showinfo("Info", "Semua browser telah ditutup")

# Pengaturan GUI
root = tk.Tk()
root.title("Pemutar Video YouTube dengan Proxy")

tk.Label(root, text="URL YouTube:").pack()
entry = tk.Entry(root, width=50)
entry.pack()

start_button = tk.Button(root, text="Start", command=start)
start_button.pack()

stop_button = tk.Button(root, text="Stop", command=stop)
stop_button.pack()

def on_closing():
    stop()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()