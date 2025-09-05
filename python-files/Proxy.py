import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import json
import os
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from bs4 import BeautifulSoup
import time


task_queue = queue.Queue()
stop_requested = False


def process_queue():
    while not task_queue.empty():
        status, url, proxy, info = task_queue.get()
        tree.insert('', 'end', values=(url, proxy, status, info))
    root.after(500, process_queue)  # перевіряй чергу кожні 500 мс

CONFIG_FILE = "config.json"
DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept_language": "en-US,en;q=0.5",
    "accept_encoding": "gzip, deflate, br",
    "connection": "keep-alive"
}

last_download_config = {}
last_proxy_index = 0
pending_response = None

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                url_entry.insert(0, data.get("url", ""))
                ua_entry.insert(0, data.get("user_agent", ""))
                cookies_entry.insert(0, data.get("cookies", ""))
                referer_entry.insert(0, data.get("referer", ""))
                connection_entry.insert(0, data.get("connection", DEFAULT_HEADERS["connection"]))
                accept_entry.insert(0, data.get("accept", DEFAULT_HEADERS["accept"]))
                accept_lang_entry.insert(0, data.get("accept_language", DEFAULT_HEADERS["accept_language"]))
                accept_enc_entry.insert(0, data.get("accept_encoding", DEFAULT_HEADERS["accept_encoding"]))
                custom_header_key_entry.insert(0, data.get("custom_header_key", ""))
                custom_header_value_entry.insert(0, data.get("custom_header_value", ""))
        except Exception as e:
            print(f"[!] Не вдалося завантажити config.json: {e}")
    else:
        accept_entry.insert(0, DEFAULT_HEADERS["accept"])
        accept_lang_entry.insert(0, DEFAULT_HEADERS["accept_language"])
        accept_enc_entry.insert(0, DEFAULT_HEADERS["accept_encoding"])

def save_config():
    data = {
        "url": url_entry.get().strip(),
        "user_agent": ua_entry.get().strip(),
        "cookies": cookies_entry.get().strip(),
        "referer": referer_entry.get().strip(),
        "accept": accept_entry.get().strip(),
        "accept_language": accept_lang_entry.get().strip(),
        "accept_encoding": accept_enc_entry.get().strip(),
        "connection": connection_entry.get().strip(),
        "custom_header_key": custom_header_key_entry.get().strip(),
        "custom_header_value": custom_header_value_entry.get().strip()
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[!] Не вдалося зберегти config.json: {e}")

def fetch_geonode_proxies(limit=50):
    try:
        url = f"https://proxylist.geonode.com/api/proxy-list?limit={limit}&page=1&sort_by=lastChecked&sort_type=desc"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        proxies = []
        for item in data.get("data", []):
            ip = item.get("ip")
            port = item.get("port")
            protocols = item.get("protocols", [])
            if ip and port and protocols:
                scheme = protocols[0].lower()
                proxies.append(f"{scheme}://{ip}:{port}")
        return proxies
    except Exception as e:
        print(f"[!] Помилка при отриманні проксі з Geonode: {e}")
        return []

def fetch_proxyscrape_proxies_all_types(country="UA", timeout=10000):
    protocols = ["http", "socks4", "socks5"]
    all_proxies = []

    for protocol in protocols:
        try:
            url = (
                f"https://api.proxyscrape.com/v2/?request=displayproxies"
                f"&protocol={protocol}&timeout={timeout}&country={country}&ssl=all&anonymity=all"
            )
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            raw_list = res.text.strip().splitlines()
            formatted = [f"{protocol}://{ip.strip()}" for ip in raw_list if ip.strip()]
            print(f"[i] Отримано {len(formatted)} {protocol.upper()} проксі")
            all_proxies.extend(formatted)
        except Exception as e:
            print(f"[!] Помилка для {protocol.upper()}: {e}")

    return all_proxies

def gather_all_proxies():
    proxies = set()

    # --- 1. ProxyScrape (HTTP, SOCKS4, SOCKS5) ---
    def get_from_proxyscrape():
        all_protocols = ["http", "socks4", "socks5"]
        for proto in all_protocols:
            try:
                url = (
                    f"https://api.proxyscrape.com/v2/?request=displayproxies"
                    f"&protocol={proto}&timeout=15000&country=UA&ssl=all&anonymity=all"
                )
                res = requests.get(url, timeout=10)
                res.raise_for_status()
                for line in res.text.strip().splitlines():
                    if line.strip():
                        proxies.add(f"{proto}://{line.strip()}")
                print(f"[+] ProxyScrape {proto.upper()} — {len(res.text.strip().splitlines())}")
            except Exception as e:
                print(f"[!] ProxyScrape {proto.upper()} error: {e}")

    # --- 2. Geonode (з параметрами) ---
    def get_from_geonode():
        try:
            for page in range(1, 4):  # можна більше сторінок
                url = (
                    f"https://proxylist.geonode.com/api/proxy-list"
                    f"?limit=100&page={page}&country=UA"
                    f"&anonymityLevel=elite&speed=fast"
                )
                res = requests.get(url, timeout=10)
                res.raise_for_status()
                data = res.json()
                for item in data.get("data", []):
                    ip = item.get("ip")
                    port = item.get("port")
                    protos = item.get("protocols", [])
                    if ip and port and protos:
                        proxies.add(f"{protos[0].lower()}://{ip}:{port}")
                print(f"[+] Geonode Page {page} — {len(data.get('data', []))}")
        except Exception as e:
            print(f"[!] Geonode error: {e}")

    # --- 3. Proxy-List.download ---
    def get_from_proxylist_download():
        urls = [
            "https://www.proxy-list.download/api/v1/get?type=http&country=UA",
            "https://www.proxy-list.download/api/v1/get?type=socks4&country=UA",
            "https://www.proxy-list.download/api/v1/get?type=socks5&country=UA"
        ]
        for url in urls:
            proto = re.search(r"type=(\w+)", url).group(1)
            success = False
            attempts = 0
    
            while not success and attempts < 3:
                try:
                    time.sleep(5)  # ⏳ пауза перед запитом
                    res = requests.get(url, timeout=10)
                    if res.status_code == 429:
                        raise Exception("429 Too Many Requests")
                    res.raise_for_status()
    
                    lines = res.text.strip().splitlines()
                    for line in lines:
                        if line.strip():
                            proxies.add(f"{proto.lower()}://{line.strip()}")
    
                    print(f"[+] ProxyList.Download {proto.upper()} — {len(lines)}")
                    success = True
    
                except Exception as e:
                    attempts += 1
                    print(f"[!] ProxyList.Download {proto.upper()} error (спроба {attempts}): {e}")
                    time.sleep(10 * attempts)  # ⌛ збільшена пауза для наступної спроби

    # --- 4. Spys.one (HTML-скрейпінг) ---
    def get_from_spys():
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
            }
            res = requests.get("http://spys.one/en/free-proxy-list/UA/", headers=headers, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            scripts = soup.find_all("script")
            ip_port_pairs = re.findall(r'(\d{1,3}(?:\.\d{1,3}){3}).*?(\d{2,5})', res.text)
            for ip, port in ip_port_pairs:
                proxies.add(f"http://{ip}:{port}")
            print(f"[+] Spys.one — {len(ip_port_pairs)}")
        except Exception as e:
            print(f"[!] Spys.one error: {e}")

    # Виклик усіх джерел
    get_from_proxyscrape()
    get_from_geonode()
    get_from_proxylist_download()
    get_from_spys()

    print(f"[i] Загальна кількість проксі перед перевіркою: {len(proxies)}")
    return list(proxies)

def on_closing():
    save_config()
    root.destroy()


def download_task(url, headers, proxy_list, output_path):
    """Перебирає проксі для одного URL."""
    for proxy in proxy_list:
        try:
            response = requests.get(
                url,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=20,
                verify=False
            )
            response.raise_for_status()
            if stop_requested:
                task_queue.put(("STOPPED", url, proxy, "Користувач зупинив"))
                return
            
            if "text/html" in response.headers.get("Content-Type", "") or response.content.startswith(b"<html"):
                preview = response.content[:10].decode(errors="replace")
                result = ("HTML", url, proxy, preview)
            elif len(response.content) == 0:
                result = ("EMPTY", url, proxy, "")
            else:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                result = ("OK", url, proxy, "")
            task_queue.put(result)
            return
        except Exception as e:
            continue
    task_queue.put(("FAILED", url, "", ""))

def check_proxy(proxy, url, headers, output_path):
    if stop_requested:
        return (proxy, "Зупинено", "Зупинено користувачем")
    proxies = {"http": proxy, "https": proxy}
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=20, verify=False)
        response.raise_for_status()

        if stop_requested:
            return (proxy, "Зупинено", "Зупинено користувачем")

        content_type = response.headers.get("Content-Type", "").lower()
        preview = response.content[:10].decode(errors="replace")

        if "text/html" in content_type or response.content.lstrip().startswith(b"<html"):
            info = f"HTML: {preview}"
            status = "HTML отримано"
        elif len(response.content) == 0:
            info = "Порожній файл"
            status = "Порожній"
        else:
            with open(output_path, "wb") as f:
                f.write(response.content)
            info = ""
            status = "OK"

        return (proxy, status, info)

    except Exception as e:
        if stop_requested:
            return (proxy, "Зупинено", "Зупинено користувачем")
        return (proxy, "Помилка", str(e))


def start_download():

    global last_download_config, last_proxy_index, pending_response,stop_requested
    stop_requested = False 
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Помилка", "Введіть URL для завантаження")
        return

    headers = {
        "User-Agent": ua_entry.get().strip() or "MyDownloader",
        "Accept": accept_entry.get().strip(),
        "Accept-Language": accept_lang_entry.get().strip(),
        "Accept-Encoding": accept_enc_entry.get().strip(),
        "Connection": connection_entry.get().strip(),
    }

    # Де зберігати файл:
    output_path = filedialog.asksaveasfilename(title="Куди зберегти файл")
    if not output_path:
        return

    last_download_config = {
        "url": url,
        "headers": headers,
        "output_path": output_path
    }
    last_proxy_index = 0
    pending_response = None

    retry_btn.config(state="disabled")
    confirm_btn.config(state="disabled")
    download_btn.config(state="disabled")
    status_label.config(text="Починаємо завантаження...")

    threading.Thread(target=try_multiple_proxies, daemon=True).start()

last_download_config = {}
last_proxy_index = 0
pending_response = None

def try_multiple_proxies():
    global last_download_config

    proxy_list = gather_all_proxies()
    url = last_download_config.get("url")
    headers = last_download_config.get("headers")
    output_path = last_download_config.get("output_path")

    if not url or not headers or not output_path:
        status_label.config(text="Відсутні налаштування для завантаження", fg="red")
        return

    status_label.config(text="Перевірка проксі (паралельно)...", fg="blue")
    download_btn.config(state="disabled")
    retry_btn.config(state="disabled")
    confirm_btn.config(state="disabled")

    def runner():
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_proxy = {executor.submit(check_proxy, proxy, url, headers, output_path): proxy for proxy in proxy_list}

            for future in as_completed(future_to_proxy):
                if stop_requested:
                    break
                proxy = future_to_proxy[future]
                try:
                    proxy, status, info = future.result()
                    tree.insert('', 'end', values=(url, proxy, status, info))
                    if status == "OK":
                        status_label.config(text=f"Завантажено з проксі {proxy}", fg="green")
                        break  # зупиняємо після успішної загрузки
                except Exception as e:
                    tree.insert('', 'end', values=(url, proxy, "Помилка", str(e)))

        download_btn.config(state="normal")
        stop_btn.config(state="disabled")
        retry_btn.config(state="normal")

    stop_btn.config(state="normal")
    threading.Thread(target=runner, daemon=True).start()

def confirm_and_save_file():
    global pending_response
    if not pending_response:
        return
    output_path = last_download_config["output_path"]
    with open(output_path, 'wb') as f:
        f.write(pending_response.content)
    messagebox.showinfo("Збережено", f"HTML-файл збережено: {output_path}")
    status_label.config(text="Файл збережено вручну", fg="green")
    pending_response = None
    confirm_btn.config(state="disabled")
    retry_btn.config(state="disabled")
    download_btn.config(state="normal")

def stop_download():
    global stop_requested
    stop_requested = True
    status_label.config(text="Зупинено користувачем", fg="red")
    download_btn.config(state="normal")
    stop_btn.config(state="disabled")
    retry_btn.config(state="disabled")
    confirm_btn.config(state="disabled")


# --- GUI ---
root = tk.Tk()
root.title("Завантажувач через проксі (потоковий)")

tk.Label(root, text="URL:").grid(row=0, column=0, sticky="e")
url_entry = tk.Entry(root, width=90)
url_entry.grid(row=0, column=1)

tk.Label(root, text="User-Agent:").grid(row=1, column=0, sticky="e")
ua_entry = tk.Entry(root, width=90)
ua_entry.grid(row=1, column=1)

tk.Label(root, text="Cookies:").grid(row=2, column=0, sticky="e")
cookies_entry = tk.Entry(root, width=90)
cookies_entry.grid(row=2, column=1)

tk.Label(root, text="Referer:").grid(row=3, column=0, sticky="e")
referer_entry = tk.Entry(root, width=90)
referer_entry.grid(row=3, column=1)

tk.Label(root, text="Accept:").grid(row=4, column=0, sticky="e")
accept_entry = tk.Entry(root, width=90)
accept_entry.grid(row=4, column=1)

tk.Label(root, text="Accept-Language:").grid(row=5, column=0, sticky="e")
accept_lang_entry = tk.Entry(root, width=90)
accept_lang_entry.grid(row=5, column=1)

tk.Label(root, text="Accept-Encoding:").grid(row=6, column=0, sticky="e")
accept_enc_entry = tk.Entry(root, width=90)
accept_enc_entry.grid(row=6, column=1)

tk.Label(root, text="Connection:").grid(row=7, column=0, sticky="e")
connection_entry = tk.Entry(root, width=90)
connection_entry.grid(row=7, column=1)

tk.Label(root, text="Custom Header Key:").grid(row=8, column=0, sticky="e")
custom_header_key_entry = tk.Entry(root, width=90)
custom_header_key_entry.grid(row=8, column=1)

tk.Label(root, text="Custom Header Value:").grid(row=9, column=0, sticky="e")
custom_header_value_entry = tk.Entry(root, width=90)
custom_header_value_entry.grid(row=9, column=1)

download_btn = tk.Button(root, text="Завантажити", command=start_download, bg="#4CAF50", fg="white")
download_btn.grid(row=10, column=0, columnspan=2, pady=10)

stop_btn = tk.Button(root, text="Стоп", command=stop_download, bg="#f44336", fg="white", state="disabled")
stop_btn.grid(row=10, column=1, columnspan=3, pady=10)


from tkinter import ttk

tree = ttk.Treeview(root, columns=("URL", "Proxy", "Status", "Info"), show='headings')
tree.heading("URL", text="URL")
tree.heading("Proxy", text="Proxy")
tree.heading("Status", text="Статус")
tree.heading("Info", text="Інфо")
tree.grid(row=11, column=0, columnspan=2, sticky="nsew")

def copy_selection(event=None):
    selected_items = tree.selection()
    if not selected_items:
        return
    lines = []
    for item in selected_items:
        values = tree.item(item, "values")
        line = "\t".join(values)  # або ", " або інший роздільник
        lines.append(line)
    text_to_copy = "\n".join(lines)
    root.clipboard_clear()
    root.clipboard_append(text_to_copy)
    root.update()  # щоб буфер обміну оновився

# Прив’язуємо Ctrl+C до копіювання
tree.bind("<Control-c>", copy_selection)
tree.bind("<Control-C>", copy_selection)

# Додати налаштування розтягування
root.grid_rowconfigure(11, weight=1)
root.grid_columnconfigure(1, weight=1)


retry_btn = tk.Button(root, text="Спробувати інший проксі", command=try_multiple_proxies, bg="#2196F3", fg="white", state="disabled")
retry_btn.grid(row=12, column=0, columnspan=2)

confirm_btn = tk.Button(root, text="Зберегти цей файл", command=confirm_and_save_file, bg="#FF9800", fg="white", state="disabled")
confirm_btn.grid(row=13, column=0, columnspan=2)

status_label = tk.Label(root, text="Готовий до завантаження", fg="gray")
status_label.grid(row=14, column=0, columnspan=2)

root.protocol("WM_DELETE_WINDOW", on_closing)
load_config()
root.after(500, process_queue)
root.mainloop()
