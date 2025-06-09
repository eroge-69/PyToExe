import requests
from requests.exceptions import RequestException
from base64 import b64encode
from datetime import datetime
import urllib3
import time
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIGURAZIONE ===
HOST = "192.168.1.1"
PORTS = [80, 443, 8000, 8443, 52869, 5001]
USERNAME = "admin"
PASSWORD = "XU9EU#@Ye3"
TIMEOUT = 5

AUTH_HEADER = {
    "Authorization": "Basic " + b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
}
WORDLIST_PATHS = [
    "admin", "debug", "diagnostic", "test", "setup", "config",
    "data", "cgi-bin/", "cgi-bin/test.sh", "cgi-bin/diagnostic.cgi",
    "webconfig", "log", "status", "dev", "hidden", "advanced",
    "backup", "system", "sysinfo", "nmu", "nmu.htm", "nmustatus.cgi",
    "tools", "reboot", "snmp", "ping.cgi", "upload.cgi", "firmware", "shell.cgi",
    "goform/sysTools", "goform/sysReboot", "goform/diag_test", "goform/ping"
]

LOG_FILE = f"scan_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# === FUNZIONI BASE ===
def log(text):
    print(text)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def get_snippet(content):
    return content[:200].replace('\n', ' ').replace('\r', '')

# === SCANSIONI ===
def scan_root_pages():
    log("[*] Verifica root per tutte le porte...")
    for port in PORTS:
        protocol = "https" if port in [443, 8443] else "http"
        url = f"{protocol}://{HOST}:{port}/"
        try:
            r = requests.get(url, headers=AUTH_HEADER, timeout=TIMEOUT, verify=False)
            snippet = get_snippet(r.text)
            log(f"[+] [{r.status_code}] {url} -> {snippet}")
        except RequestException as e:
            log(f"[-] {url} errore: {e.__class__.__name__}")

def scan_common_paths():
    log("[*] Inizio scansione endpoint noti...")
    for port in PORTS:
        protocol = "https" if port in [443, 8443] else "http"
        for path in WORDLIST_PATHS:
            url = f"{protocol}://{HOST}:{port}/{path}"
            try:
                r = requests.get(url, headers=AUTH_HEADER, timeout=TIMEOUT, verify=False)
                if r.status_code not in [404, 400]:
                    log(f"[+] [{r.status_code}] {url} -> {get_snippet(r.text)}")
            except RequestException:
                pass

def scan_upnp():
    url = f"http://{HOST}:52869"
    try:
        log("[*] Controllo UPnP GET...")
        r = requests.get(url, timeout=TIMEOUT)
        log(f"[+] {url} -> {get_snippet(r.text)}")
    except RequestException:
        log("[-] UPnP GET fallito")

    try:
        log("[*] Controllo UPnP POST SOAP...")
        headers = {
            "SOAPAction": "\"urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress\"",
            "Content-Type": "text/xml; charset=\"utf-8\""
        }
        body = '''<?xml version="1.0"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
        s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:GetExternalIPAddress xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1" />
        </s:Body>
        </s:Envelope>'''
        r = requests.post(url, headers=headers, data=body, timeout=TIMEOUT)
        log(f"[+] SOAP POST su {url} -> {get_snippet(r.text)}")
    except RequestException:
        log("[-] UPnP SOAP fallito")

def extract_csrf_and_session():
    log("[*] Estrazione token da cookie...")
    url = f"http://{HOST}/"
    try:
        r = requests.get(url, headers=AUTH_HEADER, timeout=TIMEOUT)
        cookies = r.cookies.get_dict()
        csrf = re.search(r'csrf_token\s*=\s*"?(.*?)"?[;"]', r.text)
        log(f"[+] Cookie: {cookies}")
        if csrf:
            log(f"[+] CSRF Token: {csrf.group(1)}")
    except RequestException:
        log("[-] Estrazione fallita")

def attempt_login_post():
    log("[*] Tentativo POST di login su endpoint noti...")
    login_paths = ["login.cgi", "login", "goform/login"]
    for port in PORTS:
        protocol = "https" if port in [443, 8443] else "http"
        for path in login_paths:
            url = f"{protocol}://{HOST}:{port}/{path}"
            try:
                data = {"username": USERNAME, "password": PASSWORD}
                r = requests.post(url, data=data, timeout=TIMEOUT, verify=False)
                if r.status_code not in [400, 404]:
                    log(f"[+] POST {url} [{r.status_code}] -> {get_snippet(r.text)}")
            except RequestException:
                pass

# === AVVIO ===
if __name__ == "__main__":
    log(f"[!] Inizio scansione avanzata su {HOST}")
    scan_root_pages()
    scan_common_paths()
    scan_upnp()
    extract_csrf_and_session()
    attempt_login_post()
    log(f"[✓] Completato. Log salvato in: {LOG_FILE}")
