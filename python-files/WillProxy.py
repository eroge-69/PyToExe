import random
import requests
import socks
import socket
import threading
import time
import keyboard
import ctypes
from colorama import init, Fore

init(autoreset=True)

# ASCII Header
header = r"""
 _|          _|  _|  _|  _|      _|_|_|    _|_|_|      _|_|    _|      _|  _|      _|  
 _|          _|      _|  _|      _|    _|  _|    _|  _|    _|    _|  _|      _|  _|    
 _|    _|    _|  _|  _|  _|      _|_|_|    _|_|_|    _|    _|      _|          _|      
   _|  _|  _|    _|  _|  _|      _|        _|    _|  _|    _|    _|  _|        _|      
     _|  _|      _|  _|  _|      _|        _|    _|    _|_|    _|      _|      _|      
"""
print(header)
print(Fore.RED + "Nigger Proxy That Provides No Secureity So Yeah Nigger Use WIll PROXY\n")

# Example proxy list (replace with full JSON)
proxies_list = [{"IP_Address":"184.170.248.5","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:11:32"},{"IP_Address":"72.195.34.58","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:09:32"},{"IP_Address":"67.201.33.10","Port":"25283","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:17:12"},{"IP_Address":"142.54.228.193","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:33:32"},{"IP_Address":"198.8.94.170","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:08:13"},{"IP_Address":"199.58.185.9","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:36:32"},{"IP_Address":"184.178.172.5","Port":"15303","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:09:12"},{"IP_Address":"184.178.172.3","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:09:12"},{"IP_Address":"142.54.229.249","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:09:12"},{"IP_Address":"192.252.214.20","Port":"15864","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:12:12"},{"IP_Address":"74.119.147.209","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:20:23"},{"IP_Address":"107.181.161.81","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:14:12"},{"IP_Address":"184.178.172.14","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:12:32"},{"IP_Address":"184.178.172.17","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:12:32"},{"IP_Address":"98.170.57.249","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:24:22"},{"IP_Address":"72.210.221.197","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"72.206.181.103","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"72.206.181.123","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"72.206.181.97","Port":"64943","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"72.210.208.101","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"72.195.114.169","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"72.210.221.223","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"72.210.252.134","Port":"46164","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"72.210.252.137","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:17:12"},{"IP_Address":"72.217.216.239","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:20:14"},{"IP_Address":"98.162.25.23","Port":"4145","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:17:12"},{"IP_Address":"192.111.137.34","Port":"18765","Country":"United States","Delay":"6","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:18:13"},{"IP_Address":"98.170.57.231","Port":"4145","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:17:22"},{"IP_Address":"184.181.217.194","Port":"4145","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:11:12"},{"IP_Address":"192.111.139.165","Port":"4145","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:36:32"},{"IP_Address":"184.181.217.213","Port":"4145","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:11:12"},{"IP_Address":"184.181.217.210","Port":"4145","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:11:12"},{"IP_Address":"72.195.34.59","Port":"4145","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:09:32"},{"IP_Address":"72.195.34.60","Port":"27391","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:09:32"},{"IP_Address":"184.178.172.11","Port":"4145","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:11:12"},{"IP_Address":"184.178.172.25","Port":"15291","Country":"United States","Delay":"7","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:09:32"},{"IP_Address":"98.162.25.29","Port":"31679","Country":"United States","Delay":"8","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:17:32"},{"IP_Address":"184.178.172.26","Port":"4145","Country":"United States","Delay":"8","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:22:32"},{"IP_Address":"184.170.249.65","Port":"4145","Country":"United States","Delay":"9","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:14:32"},{"IP_Address":"104.200.135.46","Port":"4145","Country":"United States","Delay":"9","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:17:32"},{"IP_Address":"69.61.200.104","Port":"36181","Country":"United States","Delay":"10","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:19:12"},{"IP_Address":"66.42.224.229","Port":"41679","Country":"United States","Delay":"10","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:19:12"},{"IP_Address":"72.195.34.41","Port":"4145","Country":"United States","Delay":"11","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:19:32"},{"IP_Address":"72.195.34.35","Port":"27360","Country":"United States","Delay":"11","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:19:32"},{"IP_Address":"68.1.210.163","Port":"4145","Country":"United States","Delay":"11","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:19:32"},{"IP_Address":"70.166.167.55","Port":"57745","Country":"United States","Delay":"11","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:19:32"},{"IP_Address":"72.195.34.42","Port":"4145","Country":"United States","Delay":"11","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:19:32"},{"IP_Address":"192.252.220.89","Port":"4145","Country":"United States","Delay":"12","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:22:32"},{"IP_Address":"184.181.217.201","Port":"4145","Country":"United States","Delay":"12","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:22:32"},{"IP_Address":"174.77.111.198","Port":"49547","Country":"United States","Delay":"13","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:03:22"},{"IP_Address":"174.77.111.197","Port":"4145","Country":"United States","Delay":"13","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:03:22"},{"IP_Address":"174.77.111.196","Port":"4145","Country":"United States","Delay":"13","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:03:22"},{"IP_Address":"174.75.211.222","Port":"4145","Country":"United States","Delay":"13","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:03:22"},{"IP_Address":"174.64.199.82","Port":"4145","Country":"United States","Delay":"13","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:03:22"},{"IP_Address":"174.64.199.79","Port":"4145","Country":"United States","Delay":"13","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:03:22"},{"IP_Address":"98.178.72.21","Port":"10919","Country":"United States","Delay":"13","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:27:12"},{"IP_Address":"98.175.31.195","Port":"4145","Country":"United States","Delay":"14","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:27:12"},{"IP_Address":"98.181.137.80","Port":"4145","Country":"United States","Delay":"14","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:27:12"},{"IP_Address":"192.111.135.17","Port":"18302","Country":"United States","Delay":"14","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:28:32"},{"IP_Address":"192.252.220.92","Port":"17328","Country":"United States","Delay":"14","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:28:32"},{"IP_Address":"98.181.137.83","Port":"4145","Country":"United States","Delay":"14","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:27:12"},{"IP_Address":"98.188.47.132","Port":"4145","Country":"United States","Delay":"14","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:27:12"},{"IP_Address":"98.188.47.150","Port":"4145","Country":"United States","Delay":"14","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:27:12"},{"IP_Address":"199.116.114.11","Port":"4145","Country":"United States","Delay":"14","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:28:33"},{"IP_Address":"184.181.217.220","Port":"4145","Country":"United States","Delay":"15","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:28:32"},{"IP_Address":"184.178.172.18","Port":"15280","Country":"United States","Delay":"19","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:22:22"},{"IP_Address":"98.162.25.4","Port":"31654","Country":"United States","Delay":"21","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:25:32"},{"IP_Address":"98.162.25.7","Port":"31653","Country":"United States","Delay":"21","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:25:32"},{"IP_Address":"184.181.217.206","Port":"4145","Country":"United States","Delay":"23","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:27:32"},{"IP_Address":"184.178.172.28","Port":"15294","Country":"United States","Delay":"23","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:27:32"},{"IP_Address":"74.119.144.60","Port":"4145","Country":"United States","Delay":"25","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:21:32"},{"IP_Address":"98.162.25.16","Port":"4145","Country":"United States","Delay":"25","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:26:33"},{"IP_Address":"24.249.199.12","Port":"4145","Country":"United States","Delay":"30","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:12:32"},{"IP_Address":"142.54.239.1","Port":"4145","Country":"United States","Delay":"32","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:26:33"},{"IP_Address":"68.71.254.6","Port":"4145","Country":"United States","Delay":"32","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:29:32"},{"IP_Address":"142.54.226.214","Port":"4145","Country":"United States","Delay":"33","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:26:33"},{"IP_Address":"24.249.199.4","Port":"4145","Country":"United States","Delay":"34","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:12:32"},{"IP_Address":"192.252.209.155","Port":"14455","Country":"United States","Delay":"35","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:18:13"},{"IP_Address":"198.8.84.3","Port":"4145","Country":"United States","Delay":"37","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:19:11"},{"IP_Address":"184.170.245.148","Port":"4145","Country":"United States","Delay":"37","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:17:12"},{"IP_Address":"192.111.129.145","Port":"16894","Country":"United States","Delay":"37","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:17:12"},{"IP_Address":"184.185.2.12","Port":"4145","Country":"United States","Delay":"39","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:11:22"},{"IP_Address":"199.58.184.97","Port":"4145","Country":"United States","Delay":"40","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:19:11"},{"IP_Address":"192.111.134.10","Port":"4145","Country":"United States","Delay":"40","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 15:18:13"},{"IP_Address":"142.54.232.6","Port":"4145","Country":"United States","Delay":"42","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:54:12"},{"IP_Address":"142.54.231.38","Port":"4145","Country":"United States","Delay":"55","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:54:12"},{"IP_Address":"104.200.152.30","Port":"4145","Country":"United States","Delay":"57","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 14:44:32"},{"IP_Address":"206.220.175.2","Port":"4145","Country":"United States","Delay":"66","Type":"SOCKS5","Anonymity":"High","Last_Checked":"2024-05-05 16:05:07"}
]

# Hide/show console window
user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')
SW_HIDE = 0
SW_SHOW = 5
hWnd = kernel32.GetConsoleWindow()

numlock_count = 0
window_hidden = False

def toggle_window():
    global numlock_count, window_hidden
    if keyboard.is_pressed("num lock"):
        numlock_count += 1
        print(f"[NumLock pressed {numlock_count}/3]")
        time.sleep(0.3)  # debounce
        if numlock_count >= 3:
            if not window_hidden:
                user32.ShowWindow(hWnd, SW_HIDE)
                print("[WINDOW HIDDEN]")
                window_hidden = True
            else:
                user32.ShowWindow(hWnd, SW_SHOW)
                print("[WINDOW VISIBLE]")
                window_hidden = False
            numlock_count = 0  # reset

def get_random_socks5_proxy():
    proxy = random.choice(proxies_list)
    ip = proxy["IP_Address"]
    port = int(proxy["Port"])
    
    socks.set_default_proxy(socks.SOCKS5, ip, port)
    socket.socket = socks.socksocket
    
    return ip, port

def fetch(url="http://httpbin.org/ip"):
    ip, port = get_random_socks5_proxy()
    try:
        response = requests.get(url, timeout=10)
        print(Fore.GREEN + "[SUCCESS] " + Fore.YELLOW + f"IP: {ip}" + Fore.WHITE + f" | Status: {response.status_code}")
    except Exception as e:
        print(Fore.RED + "[FAIL] " + Fore.YELLOW + f"IP: {ip} | Error: {e}")

def spam_requests():
    while True:
        fetch()
        time.sleep(2)

def monitor_keys():
    while True:
        toggle_window()
        time.sleep(0.1)

if __name__ == "__main__":
    threading.Thread(target=spam_requests, daemon=True).start()
    threading.Thread(target=monitor_keys, daemon=True).start()
    
    while True:
        time.sleep(1)
