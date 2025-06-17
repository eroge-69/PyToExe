import subprocess
import platform
import whois
import dns.resolver
import requests
import ssl
import socket
import time
import json
from urllib.parse import urlparse
import sys
from colorama import init, Fore, Style
import re
from bs4 import BeautifulSoup
import dns.query
import dns.dnssec
import os
import hashlib
import urllib.robotparser
import xml.etree.ElementTree as ET
import http.client
import email
from email import policy
import base64
import math

# Initialize colorama for colored terminal output
init()

# Banner in blue
BANNER = f"""{Fore.BLUE}
   _____ _               _               ____            _             
  / ____| |             | |             |  _ \          | |            
 | (___ | |__   __ _  __| | _____      _| |_) |_ __ ___ | | _____ _ __ 
  \___ \| '_ \ / _` |/ _` |/ _ \ \ /\ / /  _ <| '__/ _ \| |/ / _ \ '__|
  ____) | | | | (_| | (_| | (_) \ V  V /| |_) | | | (_) |   <  __/ |   
 |_____/|_| |_|\__,_|\__,_|\___/ \_/\_/ |____/|_|  \___/|_|\_\___|_|   
                                                                       

Join Telegram 
@akhackersredirect
@akhackersredirect
Deny, Defend Depose
One With The Best 
@akhackersredirect
{Style.RESET_ALL}"""

def clear_screen():
    subprocess.run("cls" if platform.system() == "Windows" else "clear", shell=True)

def get_domain(url):
    if not url:
        return None
    try:
        parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'https://{url}')
        domain = parsed.netloc
        domain = domain.split(':')[0]
        return domain if domain else None
    except Exception:
        return None

def ping_domain(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Ping Result ==={Style.RESET_ALL}")
    try:
        ping_command = ["ping", "-n" if platform.system() == "Windows" else "-c", "4", domain]
        output = subprocess.run(ping_command, capture_output=True, text=True, timeout=10)
        print(f"{Fore.LIGHTGREEN_EX}{output.stdout or 'No response'}{Style.RESET_ALL}")
    except subprocess.TimeoutExpired:
        print(f"{Fore.LIGHTGREEN_EX}Ping timed out{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error during ping: {str(e)}{Style.RESET_ALL}")

def whois_lookup(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== WHOIS Lookup ==={Style.RESET_ALL}")
    try:
        w = whois.whois(domain)
        print(f"{Fore.LIGHTGREEN_EX}{str(w) or 'No WHOIS data available'}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error fetching WHOIS data: {str(e)}{Style.RESET_ALL}")

def dns_lookup(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DNS Lookup ==={Style.RESET_ALL}")
    try:
        for record_type in ['A', 'MX', 'NS', 'TXT']:
            answers = dns.resolver.resolve(domain, record_type, raise_on_no_answer=False)
            if answers:
                print(f"{Fore.LIGHTGREEN_EX}{record_type} Records:{Style.RESET_ALL}")
                for rdata in answers:
                    print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
            else:
                print(f"{Fore.LIGHTGREEN_EX}No {record_type} records found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error fetching DNS data: {str(e)}{Style.RESET_ALL}")

def http_status(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== HTTP Status ==={Style.RESET_ALL}")
    try:
        response = requests.head(f"https://{domain}", timeout=5, allow_redirects=True)
        print(f"{Fore.LIGHTGREEN_EX}Status: {response.status_code} - {response.reason}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking HTTP status: {str(e)}{Style.RESET_ALL}")

def ssl_certificate(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== SSL Certificate ==={Style.RESET_ALL}")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                print(f"{Fore.LIGHTGREEN_EX}Issuer: {cert.get('issuer')}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTGREEN_EX}Subject: {cert.get('subject')}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTGREEN_EX}Valid from: {cert.get('notBefore')}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTGREEN_EX}Valid until: {cert.get('notAfter')}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error fetching SSL certificate: {str(e)}{Style.RESET_ALL}")

def page_load_time(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Page Load Time ==={Style.RESET_ALL}")
    try:
        start_time = time.time()
        response = requests.get(f"https://{domain}", timeout=10)
        end_time = time.time()
        print(f"{Fore.LIGHTGREEN_EX}Page load time: {(end_time - start_time):.2f} seconds{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error measuring page load time: {str(e)}{Style.RESET_ALL}")

def ip_geolocation(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== IP Geolocation ==={Style.RESET_ALL}")
    try:
        ip = socket.gethostbyname(domain)
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        if data.get("status") == "success":
            print(f"{Fore.LIGHTGREEN_EX}IP: {ip}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}City: {data.get('city')}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}Country: {data.get('country')}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}ISP: {data.get('isp')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No geolocation data available{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error fetching geolocation data: {str(e)}{Style.RESET_ALL}")

def port_scan(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Port Scan (Common Ports) ==={Style.RESET_ALL}")
    common_ports = [21, 22, 23, 25, 80, 443, 8080]
    try:
        ip = socket.gethostbyname(domain)
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                print(f"{Fore.LIGHTGREEN_EX}Port {port}: Open{Style.RESET_ALL}")
            else:
                print(f"{Fore.LIGHTGREEN_EX}Port {port}: Closed{Style.RESET_ALL}")
            sock.close()
    except Exception as e:
        print(f"{Fore.CYAN}Error during port scan: {str(e)}{Style.RESET_ALL}")

def security_headers(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Security Headers ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        headers = response.headers
        security_headers = [
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Strict-Transport-Security',
            'Referrer-Policy'
        ]
        for header in security_headers:
            value = headers.get(header, 'Not set')
            print(f"{Fore.LIGHTGREEN_EX}{header}: {value}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking security headers: {str(e)}{Style.RESET_ALL}")

def robots_txt(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Robots.txt Check ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/robots.txt", timeout=5)
        if response.status_code == 200:
            print(f"{Fore.LIGHTGREEN_EX}{response.text[:500] + ('...' if len(response.text) > 500 else '')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No robots.txt found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking robots.txt: {str(e)}{Style.RESET_ALL}")

def sitemap_check(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Sitemap Detection ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/sitemap.xml", timeout=5)
        if response.status_code == 200:
            print(f"{Fore.LIGHTGREEN_EX}Sitemap found at /sitemap.xml\nSample:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}{response.text[:500] + ('...' if len(response.text) > 500 else '')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No sitemap.xml found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking sitemap: {str(e)}{Style.RESET_ALL}")

def server_info(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Server Info ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        server = response.headers.get('Server', 'Not disclosed')
        powered_by = response.headers.get('X-Powered-By', 'Not disclosed')
        print(f"{Fore.LIGHTGREEN_EX}Server: {server}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}Powered-By: {powered_by}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error fetching server info: {str(e)}{Style.RESET_ALL}")

def link_count(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Link Count ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        print(f"{Fore.LIGHTGREEN_EX}Total links found: {len(links)}{Style.RESET_ALL}")
        if links:
            print(f"{Fore.LIGHTGREEN_EX}Sample links (up to 5):{Style.RESET_ALL}")
            for link in links[:5]:
                href = link.get('href', 'No href')
                print(f"{Fore.LIGHTGREEN_EX}  {href}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error counting links: {str(e)}{Style.RESET_ALL}")

def subdomain_enum(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Subdomain Enumeration ==={Style.RESET_ALL}")
    common_subdomains = ['www', 'mail', 'ftp', 'blog', 'shop']
    found_subdomains = []
    try:
        for sub in common_subdomains:
            sub_domain = f"{sub}.{domain}"
            try:
                socket.gethostbyname(sub_domain)
                found_subdomains.append(sub_domain)
            except:
                pass
        if found_subdomains:
            print(f"{Fore.LIGHTGREEN_EX}Found subdomains:{Style.RESET_ALL}")
            for sub in found_subdomains:
                print(f"{Fore.LIGHTGREEN_EX}  {sub}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No common subdomains found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error during subdomain enumeration: {str(e)}{Style.RESET_ALL}")

def traceroute(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Traceroute ==={Style.RESET_ALL}")
    try:
        traceroute_command = ["tracert" if platform.system() == "Windows" else "traceroute", domain]
        output = subprocess.run(traceroute_command, capture_output=True, text=True, timeout=30)
        print(f"{Fore.LIGHTGREEN_EX}{output.stdout or 'No response'}{Style.RESET_ALL}")
    except subprocess.TimeoutExpired:
        print(f"{Fore.LIGHTGREEN_EX}Traceroute timed out{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error during traceroute: {str(e)}{Style.RESET_ALL}")

def favicon_check(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Favicon Check ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/favicon.ico", timeout=5)
        if response.status_code == 200:
            print(f"{Fore.LIGHTGREEN_EX}Favicon found at /favicon.ico (Size: {len(response.content)} bytes){Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No favicon.ico found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking favicon: {str(e)}{Style.RESET_ALL}")

def dnssec_check(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DNSSEC Check ==={Style.RESET_ALL}")
    try:
        answers = dns.resolver.resolve(domain, 'DNSKEY', raise_on_no_answer=False)
        if answers:
            print(f"{Fore.LIGHTGREEN_EX}DNSSEC enabled: DNSKEY records found{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}DNSSEC not enabled: No DNSKEY records found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking DNSSEC: {str(e)}{Style.RESET_ALL}")

def tls_version(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== TLS Version Check ==={Style.RESET_ALL}")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                tls_version = ssock.version()
                print(f"{Fore.LIGHTGREEN_EX}TLS Version: {tls_version}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking TLS version: {str(e)}{Style.RESET_ALL}")

def sqlmap_scan(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== SQLMap Scan ==={Style.RESET_ALL}")
    try:
        result = subprocess.run(["sqlmap.py", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"{Fore.CYAN}SQLMap not found. Please install sqlmap (e.g., 'pip install sqlmap' or download from https://sqlmap.org/) and ensure 'sqlmap.py' is in your PATH.{Style.RESET_ALL}")
            return
        sqlmap_command = [
            "sqlmap.py",
            "-u", f"https://{domain}",
            "-a",
            "--batch"
        ]
        print(f"{Fore.LIGHTGREEN_EX}Running SQLMap (this may take a while)...{Style.RESET_ALL}")
        output = subprocess.run(sqlmap_command, capture_output=True, text=True, timeout=300)
        print(f"{Fore.LIGHTGREEN_EX}{output.stdout or 'No output from SQLMap'}{Style.RESET_ALL}")
        if output.stderr:
            print(f"{Fore.CYAN}SQLMap errors: {output.stderr}{Style.RESET_ALL}")
    except subprocess.TimeoutExpired:
        print(f"{Fore.LIGHTGREEN_EX}SQLMap scan timed out{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.CYAN}SQLMap not found. Please install sqlmap (e.g., 'pip install sqlmap' or download from https://sqlmap.org/) and ensure 'sqlmap.py' is in your PATH.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error running SQLMap: {str(e)}{Style.RESET_ALL}")

def check_xss_protection(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== XSS Protection Header Check ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        xss_header = response.headers.get('X-XSS-Protection', 'Not set')
        print(f"{Fore.LIGHTGREEN_EX}X-XSS-Protection: {xss_header}{Style.RESET_ALL}")
        if xss_header == 'Not set' or '0' in xss_header:
            print(f"{Fore.LIGHTGREEN_EX}Warning: XSS protection is disabled or not configured{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking XSS protection: {str(e)}{Style.RESET_ALL}")

def check_cors_policy(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== CORS Policy Check ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'Not set')
        print(f"{Fore.LIGHTGREEN_EX}Access-Control-Allow-Origin: {cors_header}{Style.RESET_ALL}")
        if cors_header == '*':
            print(f"{Fore.LIGHTGREEN_EX}Warning: Wildcard CORS policy may allow unauthorized access{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking CORS policy: {str(e)}{Style.RESET_ALL}")

def check_hsts_preload(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== HSTS Preload Check ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        hsts = response.headers.get('Strict-Transport-Security', 'Not set')
        if 'includeSubDomains' in hsts and 'preload' in hsts:
            print(f"{Fore.LIGHTGREEN_EX}HSTS Preload: Enabled ({hsts}){Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}HSTS Preload: Not enabled or not configured{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking HSTS preload: {str(e)}{Style.RESET_ALL}")

def check_robots_disallow(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Robots.txt Disallow Rules ==={Style.RESET_ALL}")
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"https://{domain}/robots.txt")
        rp.read()
        print(f"{Fore.LIGHTGREEN_EX}Disallow Rules:{Style.RESET_ALL}")
        for entry in rp.entries:
            for rule in entry.rulelines:
                if not rule.allowance:
                    print(f"{Fore.LIGHTGREEN_EX}  Disallow: {rule.path}{Style.RESET_ALL}")
        if not rp.entries:
            print(f"{Fore.LIGHTGREEN_EX}No disallow rules found or robots.txt not present{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking robots.txt disallow rules: {str(e)}{Style.RESET_ALL}")

def check_sitemap_urls(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Sitemap URLs Count ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/sitemap.xml", timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            print(f"{Fore.LIGHTGREEN_EX}Total URLs in sitemap: {len(urls)}{Style.RESET_ALL}")
            if urls:
                print(f"{Fore.LIGHTGREEN_EX}Sample URLs (up to 5):{Style.RESET_ALL}")
                for url in urls[:5]:
                    print(f"{Fore.LIGHTGREEN_EX}  {url.text}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No sitemap.xml found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking sitemap URLs: {str(e)}{Style.RESET_ALL}")

def check_page_size(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Page Size ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        size = len(response.content)
        print(f"{Fore.LIGHTGREEN_EX}Page size: {size / 1024:.2f} KB{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking page size: {str(e)}{Style.RESET_ALL}")

def check_redirect_chain(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Redirect Chain ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10, allow_redirects=True)
        history = response.history
        if history:
            print(f"{Fore.LIGHTGREEN_EX}Redirect chain:{Style.RESET_ALL}")
            for i, resp in enumerate(history, 1):
                print(f"{Fore.LIGHTGREEN_EX}  {i}. {resp.status_code} - {resp.url}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}  Final: {response.status_code} - {response.url}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No redirects detected{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking redirect chain: {str(e)}{Style.RESET_ALL}")

def check_cookie_security(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Cookie Security ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        cookies = response.cookies
        if cookies:
            print(f"{Fore.LIGHTGREEN_EX}Cookies found:{Style.RESET_ALL}")
            for cookie in cookies:
                secure = 'Yes' if cookie.secure else 'No'
                httponly = 'Yes' if cookie.has_nonstandard_attr('HttpOnly') else 'No'
                print(f"{Fore.LIGHTGREEN_EX}  {cookie.name}: Secure={secure}, HttpOnly={httponly}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No cookies found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking cookies: {str(e)}{Style.RESET_ALL}")

def check_ssl_cipher_suites(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== SSL Cipher Suites ==={Style.RESET_ALL}")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cipher = ssock.cipher()
                print(f"{Fore.LIGHTGREEN_EX}Cipher: {cipher[0]}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTGREEN_EX}Protocol: {cipher[1]}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTGREEN_EX}Key size: {cipher[2]} bits{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking SSL cipher suites: {str(e)}{Style.RESET_ALL}")

def check_dns_caa_records(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DNS CAA Records ==={Style.RESET_ALL}")
    try:
        answers = dns.resolver.resolve(domain, 'CAA', raise_on_no_answer=False)
        if answers:
            print(f"{Fore.LIGHTGREEN_EX}CAA Records:{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No CAA records found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking CAA records: {str(e)}{Style.RESET_ALL}")

def check_spf_record(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== SPF Record Check ==={Style.RESET_ALL}")
    try:
        answers = dns.resolver.resolve(domain, 'TXT', raise_on_no_answer=False)
        spf_records = [rdata.to_text() for rdata in answers if 'v=spf1' in rdata.to_text()]
        if spf_records:
            print(f"{Fore.LIGHTGREEN_EX}SPF Records:{Style.RESET_ALL}")
            for record in spf_records:
                print(f"{Fore.LIGHTGREEN_EX}  {record}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No SPF records found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking SPF record: {str(e)}{Style.RESET_ALL}")

def check_dkim_records(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DKIM Records Check ==={Style.RESET_ALL}")
    try:
        answers = dns.resolver.resolve(f"selector1._domainkey.{domain}", 'TXT', raise_on_no_answer=False)
        if answers:
            print(f"{Fore.LIGHTGREEN_EX}DKIM Records:{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No DKIM records found for selector1._domainkey{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking DKIM records: {str(e)}{Style.RESET_ALL}")

def check_dmarc_policy(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DMARC Policy Check ==={Style.RESET_ALL}")
    try:
        answers = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT', raise_on_no_answer=False)
        if answers:
            print(f"{Fore.LIGHTGREEN_EX}DMARC Records:{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No DMARC policy found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking DMARC policy: {str(e)}{Style.RESET_ALL}")

def check_favicon_hash(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Favicon Hash ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/favicon.ico", timeout=5)
        if response.status_code == 200:
            favicon_hash = hashlib.md5(response.content).hexdigest()
            print(f"{Fore.LIGHTGREEN_EX}Favicon MD5 Hash: {favicon_hash}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No favicon.ico found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking favicon hash: {str(e)}{Style.RESET_ALL}")

def check_robots_size(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Robots.txt Size ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/robots.txt", timeout=5)
        if response.status_code == 200:
            size = len(response.text)
            print(f"{Fore.LIGHTGREEN_EX}Robots.txt size: {size / 1024:.2f} KB{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No robots.txt found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking robots.txt size: {str(e)}{Style.RESET_ALL}")

def check_html_title(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== HTML Title ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No title found'
        print(f"{Fore.LIGHTGREEN_EX}Title: {title}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking HTML title: {str(e)}{Style.RESET_ALL}")

def check_meta_description(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Meta Description ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        meta = soup.find('meta', attrs={'name': re.compile('description', re.I)})
        description = meta['content'] if meta and 'content' in meta.attrs else 'No meta description found'
        print(f"{Fore.LIGHTGREEN_EX}Meta Description: {description}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking meta description: {str(e)}{Style.RESET_ALL}")

def check_canonical_url(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Canonical URL ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        canonical = soup.find('link', rel='canonical')
        url = canonical['href'] if canonical and 'href' in canonical.attrs else 'No canonical URL found'
        print(f"{Fore.LIGHTGREEN_EX}Canonical URL: {url}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking canonical URL: {str(e)}{Style.RESET_ALL}")

def check_alt_text_images(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Image Alt Text ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        missing_alt = [img.get('src', 'No src') for img in images if not img.get('alt')]
        print(f"{Fore.LIGHTGREEN_EX}Total images: {len(images)}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}Images missing alt text: {len(missing_alt)}{Style.RESET_ALL}")
        if missing_alt:
            print(f"{Fore.LIGHTGREEN_EX}Sample images missing alt text (up to 5):{Style.RESET_ALL}")
            for src in missing_alt[:5]:
                print(f"{Fore.LIGHTGREEN_EX}  {src}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking image alt text: {str(e)}{Style.RESET_ALL}")

def check_broken_links(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Broken Links ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        broken_links = []
        for link in links[:10]:  # Limit to 10 to avoid excessive requests
            href = link['href']
            if href.startswith(('http://', 'https://')):
                try:
                    r = requests.head(href, timeout=5, allow_redirects=True)
                    if r.status_code >= 400:
                        broken_links.append((href, r.status_code))
                except:
                    broken_links.append((href, 'Error'))
        if broken_links:
            print(f"{Fore.LIGHTGREEN_EX}Broken links found:{Style.RESET_ALL}")
            for href, status in broken_links:
                print(f"{Fore.LIGHTGREEN_EX}  {href} (Status: {status}){Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No broken links found (checked up to 10 links){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking broken links: {str(e)}{Style.RESET_ALL}")

def check_page_speed_score(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Page Speed Score (Basic) ==={Style.RESET_ALL}")
    try:
        start_time = time.time()
        response = requests.get(f"https://{domain}", timeout=10)
        end_time = time.time()
        load_time = end_time - start_time
        score = max(0, 100 - int(load_time * 10))  # Simple heuristic
        print(f"{Fore.LIGHTGREEN_EX}Estimated Page Speed Score: {score}/100 (Load time: {load_time:.2f}s){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking page speed score: {str(e)}{Style.RESET_ALL}")

def check_mobile_friendliness(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Mobile Friendliness ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport and 'width=device-width' in viewport.get('content', ''):
            print(f"{Fore.LIGHTGREEN_EX}Mobile-friendly: Viewport meta tag found{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}Not mobile-friendly: No viewport meta tag or incorrect configuration{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking mobile friendliness: {str(e)}{Style.RESET_ALL}")

def check_dns_soa_record(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DNS SOA Record ==={Style.RESET_ALL}")
    try:
        answers = dns.resolver.resolve(domain, 'SOA', raise_on_no_answer=False)
        if answers:
            print(f"{Fore.LIGHTGREEN_EX}SOA Record:{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No SOA record found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking SOA record: {str(e)}{Style.RESET_ALL}")

def check_ssl_certificate_chain(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== SSL Certificate Chain ==={Style.RESET_ALL}")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert_chain = ssock.getpeercertchain()
                print(f"{Fore.LIGHTGREEN_EX}Certificate chain length: {len(cert_chain)}{Style.RESET_ALL}")
                for i, cert in enumerate(cert_chain, 1):
                    print(f"{Fore.LIGHTGREEN_EX}  Certificate {i} Subject: {cert.get('subject')}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking SSL certificate chain: {str(e)}{Style.RESET_ALL}")

def check_server_response_time(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Server Response Time ==={Style.RESET_ALL}")
    try:
        start_time = time.time()
        response = requests.head(f"https://{domain}", timeout=5)
        end_time = time.time()
        print(f"{Fore.LIGHTGREEN_EX}Server response time: {(end_time - start_time) * 1000:.2f} ms{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking server response time: {str(e)}{Style.RESET_ALL}")

def check_content_encoding(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Content Encoding ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        encoding = response.headers.get('Content-Encoding', 'Not set')
        print(f"{Fore.LIGHTGREEN_EX}Content-Encoding: {encoding}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking content encoding: {str(e)}{Style.RESET_ALL}")

def check_open_graph_tags(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Open Graph Tags ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        og_tags = soup.find_all('meta', property=re.compile('og:'))
        if og_tags:
            print(f"{Fore.LIGHTGREEN_EX}Open Graph Tags:{Style.RESET_ALL}")
            for tag in og_tags[:5]:
                prop = tag.get('property', 'Unknown')
                content = tag.get('content', 'No content')
                print(f"{Fore.LIGHTGREEN_EX}  {prop}: {content}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No Open Graph tags found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking Open Graph tags: {str(e)}{Style.RESET_ALL}")

def check_robots_crawl_delay(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Robots.txt Crawl Delay ==={Style.RESET_ALL}")
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"https://{domain}/robots.txt")
        rp.read()
        delay = rp.crawl_delay('*')
        print(f"{Fore.LIGHTGREEN_EX}Crawl Delay: {delay if delay is not None else 'Not set'}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking crawl delay: {str(e)}{Style.RESET_ALL}")

def check_subdomain_takeover(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Subdomain Takeover Check ==={Style.RESET_ALL}")
    try:
        common_subdomains = ['www', 'mail', 'ftp', 'blog', 'shop']
        for sub in common_subdomains:
            sub_domain = f"{sub}.{domain}"
            try:
                answers = dns.resolver.resolve(sub_domain, 'CNAME', raise_on_no_answer=False)
                if answers:
                    print(f"{Fore.LIGHTGREEN_EX}{sub_domain}: CNAME found, possible takeover risk{Style.RESET_ALL}")
                    for rdata in answers:
                        print(f"{Fore.LIGHTGREEN_EX}  CNAME: {rdata}{Style.RESET_ALL}")
            except dns.resolver.NXDOMAIN:
                print(f"{Fore.LIGHTGREEN_EX}{sub_domain}: No DNS record, likely safe{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking subdomain takeover: {str(e)}{Style.RESET_ALL}")

def check_email_security_headers(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Email Security Headers ==={Style.RESET_ALL}")
    try:
        conn = http.client.HTTPSConnection(domain, timeout=10)
        conn.request("HEAD", "/")
        response = conn.getresponse()
        headers = response.getheaders()
        email_headers = ['ARC-Authentication-Results', 'ARC-Message-Signature', 'ARC-Seal']
        found = False
        for header, value in headers:
            if header in email_headers:
                print(f"{Fore.LIGHTGREEN_EX}{header}: {value}{Style.RESET_ALL}")
                found = True
        if not found:
            print(f"{Fore.LIGHTGREEN_EX}No email security headers found{Style.RESET_ALL}")
        conn.close()
    except Exception as e:
        print(f"{Fore.CYAN}Error checking email security headers: {str(e)}{Style.RESET_ALL}")

def check_api_endpoints(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== API Endpoints Check ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script', src=True)
        api_patterns = ['api', 'rest', 'graphql', 'endpoint']
        endpoints = []
        for script in scripts:
            src = script['src']
            if any(pattern in src.lower() for pattern in api_patterns):
                endpoints.append(src)
        if endpoints:
            print(f"{Fore.LIGHTGREEN_EX}Potential API endpoints:{Style.RESET_ALL}")
            for endpoint in endpoints[:5]:
                print(f"{Fore.LIGHTGREEN_EX}  {endpoint}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No potential API endpoints found in scripts{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking API endpoints: {str(e)}{Style.RESET_ALL}")

def check_csp_violations(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== CSP Violations Check ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        csp = response.headers.get('Content-Security-Policy', 'Not set')
        if csp == 'Not set':
            print(f"{Fore.LIGHTGREEN_EX}No Content-Security-Policy header found{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}CSP Header: {csp[:100] + ('...' if len(csp) > 100 else '')}{Style.RESET_ALL}")
            weak_directives = ['unsafe-inline', 'unsafe-eval']
            for directive in weak_directives:
                if directive in csp:
                    print(f"{Fore.LIGHTGREEN_EX}Warning: Found potentially unsafe CSP directive: {directive}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking CSP violations: {str(e)}{Style.RESET_ALL}")

def check_technology_stack(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Technology Stack ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        headers = response.headers
        tech_indicators = {
            'X-Powered-By': 'Not disclosed',
            'Server': 'Not disclosed',
            'X-Drupal': 'Drupal',
            'X-Generator': 'Content Management System',
            'X-WordPress': 'WordPress'
        }
        found = False
        for header, tech in tech_indicators.items():
            if header in headers:
                print(f"{Fore.LIGHTGREEN_EX}{header}: {headers[header]} ({tech}){Style.RESET_ALL}")
                found = True
        if not found:
            print(f"{Fore.LIGHTGREEN_EX}No clear technology indicators found in headers{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking technology stack: {str(e)}{Style.RESET_ALL}")

def check_dns_txt_records(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DNS TXT Records ==={Style.RESET_ALL}")
    try:
        answers = dns.resolver.resolve(domain, 'TXT', raise_on_no_answer=False)
        if answers:
            print(f"{Fore.LIGHTGREEN_EX}TXT Records:{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No TXT records found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking TXT records: {str(e)}{Style.RESET_ALL}")

def check_http2_support(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== HTTP/2 Support ==={Style.RESET_ALL}")
    try:
        conn = http.client.HTTPSConnection(domain, timeout=10)
        conn.request("HEAD", "/")
        response = conn.getresponse()
        protocol = response.version
        if protocol >= 20:
            print(f"{Fore.LIGHTGREEN_EX}HTTP/2 Supported: Protocol version {protocol/10:.1f}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}HTTP/2 Not Supported: Protocol version {protocol/10:.1f}{Style.RESET_ALL}")
        conn.close()
    except Exception as e:
        print(f"{Fore.CYAN}Error checking HTTP/2 support: {str(e)}{Style.RESET_ALL}")

def check_server_location(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Server Location ==={Style.RESET_ALL}")
    try:
        ip = socket.gethostbyname(domain)
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        if data.get("status") == "success":
            print(f"{Fore.LIGHTGREEN_EX}Server Location: {data.get('city')}, {data.get('regionName')}, {data.get('country')}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}Coordinates: {data.get('lat')}, {data.get('lon')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No server location data available{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking server location: {str(e)}{Style.RESET_ALL}")

def check_content_type(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Content Type ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        content_type = response.headers.get('Content-Type', 'Not set')
        print(f"{Fore.LIGHTGREEN_EX}Content-Type: {content_type}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking content type: {str(e)}{Style.RESET_ALL}")

def check_cache_control(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Cache Control ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        cache_control = response.headers.get('Cache-Control', 'Not set')
        print(f"{Fore.LIGHTGREEN_EX}Cache-Control: {cache_control}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking cache control: {str(e)}{Style.RESET_ALL}")

def check_last_modified(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Last Modified ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        last_modified = response.headers.get('Last-Modified', 'Not set')
        print(f"{Fore.LIGHTGREEN_EX}Last-Modified: {last_modified}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking last modified: {str(e)}{Style.RESET_ALL}")

def check_h1_tags(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== H1 Tags ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        h1_tags = soup.find_all('h1')
        print(f"{Fore.LIGHTGREEN_EX}Total H1 tags: {len(h1_tags)}{Style.RESET_ALL}")
        if h1_tags:
            print(f"{Fore.LIGHTGREEN_EX}H1 Tags (up to 5):{Style.RESET_ALL}")
            for h1 in h1_tags[:5]:
                print(f"{Fore.LIGHTGREEN_EX}  {h1.get_text(strip=True)}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking H1 tags: {str(e)}{Style.RESET_ALL}")

def check_external_links(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== External Links ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        external_links = [link['href'] for link in links if link['href'].startswith(('http://', 'https://')) and domain not in link['href']]
        print(f"{Fore.LIGHTGREEN_EX}Total external links: {len(external_links)}{Style.RESET_ALL}")
        if external_links:
            print(f"{Fore.LIGHTGREEN_EX}Sample external links (up to 5):{Style.RESET_ALL}")
            for link in external_links[:5]:
                print(f"{Fore.LIGHTGREEN_EX}  {link}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking external links: {str(e)}{Style.RESET_ALL}")

def check_internal_links(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Internal Links ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        internal_links = [link['href'] for link in links if not link['href'].startswith(('http://', 'https://')) or domain in link['href']]
        print(f"{Fore.LIGHTGREEN_EX}Total internal links: {len(internal_links)}{Style.RESET_ALL}")
        if internal_links:
            print(f"{Fore.LIGHTGREEN_EX}Sample internal links (up to 5):{Style.RESET_ALL}")
            for link in internal_links[:5]:
                print(f"{Fore.LIGHTGREEN_EX}  {link}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking internal links: {str(e)}{Style.RESET_ALL}")

def check_nofollow_links(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Nofollow Links ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        nofollow_links = soup.find_all('a', rel='nofollow')
        print(f"{Fore.LIGHTGREEN_EX}Total nofollow links: {len(nofollow_links)}{Style.RESET_ALL}")
        if nofollow_links:
            print(f"{Fore.LIGHTGREEN_EX}Sample nofollow links (up to 5):{Style.RESET_ALL}")
            for link in nofollow_links[:5]:
                print(f"{Fore.LIGHTGREEN_EX}  {link.get('href', 'No href')}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking nofollow links: {str(e)}{Style.RESET_ALL}")

def check_xmlrpc_exposure(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== XML-RPC Exposure ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/xmlrpc.php", timeout=5)
        if response.status_code == 200:
            print(f"{Fore.LIGHTGREEN_EX}XML-RPC found at /xmlrpc.php, potential security risk{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No XML-RPC found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking XML-RPC exposure: {str(e)}{Style.RESET_ALL}")

def check_wordpress_version(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== WordPress Version ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        meta = soup.find('meta', attrs={'name': 'generator', 'content': re.compile('WordPress', re.I)})
        version = meta['content'] if meta and 'content' in meta.attrs else 'Not detected'
        print(f"{Fore.LIGHTGREEN_EX}WordPress Version: {version}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking WordPress version: {str(e)}{Style.RESET_ALL}")

def check_schema_markup(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Schema Markup ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        schema_tags = soup.find_all(attrs={'itemscope': True})
        print(f"{Fore.LIGHTGREEN_EX}Total schema markup items: {len(schema_tags)}{Style.RESET_ALL}")
        if schema_tags:
            print(f"{Fore.LIGHTGREEN_EX}Sample schema types (up to 5):{Style.RESET_ALL}")
            for tag in schema_tags[:5]:
                schema_type = tag.get('itemtype', 'No type')
                print(f"{Fore.LIGHTGREEN_EX}  {schema_type}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking schema markup: {str(e)}{Style.RESET_ALL}")

def check_twitter_card_tags(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Twitter Card Tags ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile('twitter:', re.I)})
        if twitter_tags:
            print(f"{Fore.LIGHTGREEN_EX}Twitter Card Tags:{Style.RESET_ALL}")
            for tag in twitter_tags[:5]:
                name = tag.get('name', 'Unknown')
                content = tag.get('content', 'No content')
                print(f"{Fore.LIGHTGREEN_EX}  {name}: {content}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No Twitter Card tags found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking Twitter Card tags: {str(e)}{Style.RESET_ALL}")

def check_language_tag(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== HTML Language Tag ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        html_tag = soup.find('html')
        lang = html_tag.get('lang', 'Not set') if html_tag else 'Not set'
        print(f"{Fore.LIGHTGREEN_EX}Language Tag: {lang}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking language tag: {str(e)}{Style.RESET_ALL}")

def check_dns_ptr_record(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DNS PTR Record ==={Style.RESET_ALL}")
    try:
        ip = socket.gethostbyname(domain)
        answers = dns.resolver.resolve(dns.reversename.from_address(ip), 'PTR', raise_on_no_answer=False)
        if answers:
            print(f"{Fore.LIGHTGREEN_EX}PTR Records:{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No PTR records found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking PTR record: {str(e)}{Style.RESET_ALL}")

def check_robots_sitemap_reference(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Robots.txt Sitemap Reference ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/robots.txt", timeout=5)
        if response.status_code == 200:
            sitemaps = [line.split(': ')[1].strip() for line in response.text.split('\n') if line.lower().startswith('sitemap:')]
            if sitemaps:
                print(f"{Fore.LIGHTGREEN_EX}Sitemap references in robots.txt:{Style.RESET_ALL}")
                for sitemap in sitemaps[:5]:
                    print(f"{Fore.LIGHTGREEN_EX}  {sitemap}{Style.RESET_ALL}")
            else:
                print(f"{Fore.LIGHTGREEN_EX}No sitemap references found in robots.txt{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No robots.txt found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking robots.txt sitemap reference: {str(e)}{Style.RESET_ALL}")

def check_server_etag(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Server ETag ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        etag = response.headers.get('ETag', 'Not set')
        print(f"{Fore.LIGHTGREEN_EX}ETag: {etag}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking ETag: {str(e)}{Style.RESET_ALL}")

def check_hreflang_tags(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Hreflang Tags ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        hreflang_tags = soup.find_all('link', rel='alternate', hreflang=True)
        print(f"{Fore.LIGHTGREEN_EX}Total hreflang tags: {len(hreflang_tags)}{Style.RESET_ALL}")
        if hreflang_tags:
            print(f"{Fore.LIGHTGREEN_EX}Sample hreflang tags (up to 5):{Style.RESET_ALL}")
            for tag in hreflang_tags[:5]:
                hreflang = tag.get('hreflang', 'No hreflang')
                href = tag.get('href', 'No href')
                print(f"{Fore.LIGHTGREEN_EX}  {hreflang}: {href}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking hreflang tags: {str(e)}{Style.RESET_ALL}")

def check_dns_any_record(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== DNS ANY Query ==={Style.RESET_ALL}")
    try:
        answers = dns.resolver.resolve(domain, 'ANY', raise_on_no_answer=False)
        if answers:
            print(f"{Fore.LIGHTGREEN_EX}ANY Records:{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.LIGHTGREEN_EX}  {rdata}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No ANY records returned{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking ANY records: {str(e)}{Style.RESET_ALL}")

def check_security_txt(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Security.txt Check ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"https://{domain}/.well-known/security.txt", timeout=5)
        if response.status_code == 200:
            print(f"{Fore.LIGHTGREEN_EX}security.txt found at /.well-known/security.txt\nSample:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}{response.text[:500] + ('...' if len(response.text) > 500 else '')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No security.txt found (Status: {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking security.txt: {str(e)}{Style.RESET_ALL}")

def check_directory_enumeration(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Directory Enumeration ==={Style.RESET_ALL}")
    try:
        common_dirs = ['admin', 'login', 'wp-admin', 'config', 'backup', 'test', 'dev', 'staging']
        found_dirs = []
        for directory in common_dirs[:10]:  # Limit to 10 to avoid excessive requests
            url = f"https://{domain}/{directory}/"
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    found_dirs.append((directory, response.status_code))
                elif response.status_code in [301, 302]:
                    found_dirs.append((directory, f"{response.status_code} - Redirect"))
            except:
                pass
        if found_dirs:
            print(f"{Fore.LIGHTGREEN_EX}Found directories:{Style.RESET_ALL}")
            for dir_name, status in found_dirs:
                print(f"{Fore.LIGHTGREEN_EX}  /{dir_name}: {status}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No common directories found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error during directory enumeration: {str(e)}{Style.RESET_ALL}")

def check_subdomain_bruteforce(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Subdomain Brute-Forcing ==={Style.RESET_ALL}")
    try:
        subdomains = ['app', 'dev', 'test', 'api', 'staging', 'beta', 'secure', 'portal']
        found_subdomains = []
        for sub in subdomains[:10]:  # Limit to 10 to avoid excessive DNS queries
            sub_domain = f"{sub}.{domain}"
            try:
                answers = dns.resolver.resolve(sub_domain, 'A', raise_on_no_answer=False)
                if answers:
                    found_subdomains.append(sub_domain)
            except:
                pass
        if found_subdomains:
            print(f"{Fore.LIGHTGREEN_EX}Found subdomains:{Style.RESET_ALL}")
            for sub in found_subdomains:
                print(f"{Fore.LIGHTGREEN_EX}  {sub}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No subdomains found via brute-forcing{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error during subdomain brute-forcing: {str(e)}{Style.RESET_ALL}")

def check_http_methods(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== HTTP Methods Check ==={Style.RESET_ALL}")
    try:
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'TRACE']
        supported_methods = []
        for method in methods:
            try:
                response = requests.request(method, f"https://{domain}", timeout=5)
                if response.status_code in [200, 204, 301, 302, 405]:
                    supported_methods.append((method, response.status_code))
            except:
                pass
        if supported_methods:
            print(f"{Fore.LIGHTGREEN_EX}Supported HTTP Methods:{Style.RESET_ALL}")
            for method, status in supported_methods:
                print(f"{Fore.LIGHTGREEN_EX}  {method}: {status}{Style.RESET_ALL}")
                if method in ['PUT', 'DELETE', 'TRACE']:
                    print(f"{Fore.LIGHTGREEN_EX}  Warning: {method} method enabled, potential security risk{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No HTTP methods detected{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking HTTP methods: {str(e)}{Style.RESET_ALL}")

def check_sensitive_files(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== Sensitive Files Check ==={Style.RESET_ALL}")
    try:
        files = ['.env', 'config.php', '.git/config', 'backup.sql', 'db_backup.zip', 'config.json']
        found_files = []
        for file in files[:10]:  # Limit to 10 to avoid excessive requests
            url = f"https://{domain}/{file}"
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    found_files.append((file, response.status_code))
            except:
                pass
        if found_files:
            print(f"{Fore.LIGHTGREEN_EX}Found sensitive files (potential security risk):{Style.RESET_ALL}")
            for file, status in found_files:
                print(f"{Fore.LIGHTGREEN_EX}  /{file}: {status}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTGREEN_EX}No sensitive files found{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.CYAN}Error checking sensitive files: {str(e)}{Style.RESET_ALL}")

def ip_dorking(domain):
    print(f"{Fore.LIGHTGREEN_EX}\n=== IP Dorking ==={Style.RESET_ALL}")
    try:
        ip = socket.gethostbyname(domain)
        print(f"{Fore.LIGHTGREEN_EX}IP Address: {ip}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Performing custom port scan...{Style.RESET_ALL}")
        fallback_port_scan(ip)
    except Exception as e:
        print(f"{Fore.CYAN}Error during IP dorking: {str(e)}{Style.RESET_ALL}")

def fallback_port_scan(ip):
    print(f"{Fore.LIGHTGREEN_EX}Custom Port Scan (Extended Ports):{Style.RESET_ALL}")
    extended_ports = [21, 22, 23, 25, 80, 443, 8080, 3389, 445, 1433, 3306]
    try:
        for port in extended_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                service = get_service_name(port)
                print(f"{Fore.LIGHTGREEN_EX}Port {port}: Open ({service}){Style.RESET_ALL}")
            else:
                print(f"{Fore.LIGHTGREEN_EX}Port {port}: Closed{Style.RESET_ALL}")
            sock.close()
    except Exception as e:
        print(f"{Fore.CYAN}Error during fallback port scan: {str(e)}{Style.RESET_ALL}")

def get_service_name(port):
    services = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        80: 'HTTP',
        443: 'HTTPS',
        8080: 'HTTP-Alt',
        3389: 'RDP',
        445: 'SMB',
        1433: 'MSSQL',
        3306: 'MySQL'
    }
    return services.get(port, 'Unknown')

def display_menu():
    options = [
        ("1. Ping", ping_domain),
        ("2. WHOIS Lookup", whois_lookup),
        ("3. DNS Lookup", dns_lookup),
        ("4. HTTP Status Check", http_status),
        ("5. SSL Certificate Info", ssl_certificate),
        ("6. Page Load Time", page_load_time),
        ("7. IP Geolocation", ip_geolocation),
        ("8. Port Scan", port_scan),
        ("9. Security Headers", security_headers),
        ("10. Robots.txt Check", robots_txt),
        ("11. Sitemap Detection", sitemap_check),
        ("12. Server Info", server_info),
        ("13. Link Count", link_count),
        ("14. Subdomain Enum", subdomain_enum),
        ("15. Traceroute", traceroute),
        ("16. Favicon Check", favicon_check),
        ("17. DNSSEC Check", dnssec_check),
        ("18. TLS Version Check", tls_version),
        ("19. SQLMap Scan", sqlmap_scan),
        ("20. XSS Protection", check_xss_protection),
        ("21. CORS Policy", check_cors_policy),
        ("22. HSTS Preload", check_hsts_preload),
        ("23. Robots Disallow", check_robots_disallow),
        ("24. Sitemap URLs", check_sitemap_urls),
        ("25. Page Size", check_page_size),
        ("26. Redirect Chain", check_redirect_chain),
        ("27. Cookie Security", check_cookie_security),
        ("28. SSL Cipher Suites", check_ssl_cipher_suites),
        ("29. DNS CAA Records", check_dns_caa_records),
        ("30. SPF Record", check_spf_record),
        ("31. DKIM Records", check_dkim_records),
        ("32. DMARC Policy", check_dmarc_policy),
        ("33. Favicon Hash", check_favicon_hash),
        ("34. Robots.txt Size", check_robots_size),
        ("35. HTML Title", check_html_title),
        ("36. Meta Description", check_meta_description),
        ("37. Canonical URL", check_canonical_url),
        ("38. Image Alt Text", check_alt_text_images),
        ("39. Broken Links", check_broken_links),
        ("40. Page Speed Score", check_page_speed_score),
        ("41. Mobile Friendliness", check_mobile_friendliness),
        ("42. DNS SOA Record", check_dns_soa_record),
        ("43. SSL Cert Chain", check_ssl_certificate_chain),
        ("44. Server Resp Time", check_server_response_time),
        ("45. Content Encoding", check_content_encoding),
        ("46. Open Graph Tags", check_open_graph_tags),
        ("47. Crawl Delay", check_robots_crawl_delay),
        ("48. Subdomain Takeover", check_subdomain_takeover),
        ("49. Email Sec Headers", check_email_security_headers),
        ("50. API Endpoints", check_api_endpoints),
        ("51. CSP Violations", check_csp_violations),
        ("52. Technology Stack", check_technology_stack),
        ("53. DNS TXT Records", check_dns_txt_records),
        ("54. HTTP/2 Support", check_http2_support),
        ("55. Server Location", check_server_location),
        ("56. Content Type", check_content_type),
        ("57. Cache Control", check_cache_control),
        ("58. Last Modified", check_last_modified),
        ("59. H1 Tags", check_h1_tags),
        ("60. External Links", check_external_links),
        ("61. Internal Links", check_internal_links),
        ("62. Nofollow Links", check_nofollow_links),
        ("63. XML-RPC Exposure", check_xmlrpc_exposure),
        ("64. WordPress Version", check_wordpress_version),
        ("65. Schema Markup", check_schema_markup),
        ("66. Twitter Card Tags", check_twitter_card_tags),
        ("67. Language Tag", check_language_tag),
        ("68. DNS PTR Record", check_dns_ptr_record),
        ("69. Robots Sitemap Ref", check_robots_sitemap_reference),
        ("70. Server ETag", check_server_etag),
        ("71. Hreflang Tags", check_hreflang_tags),
        ("72. DNS ANY Query", check_dns_any_record),
        ("73. Security.txt Check", check_security_txt),
        ("74. IP Dorking", ip_dorking),
        ("75. Directory Enum", check_directory_enumeration),
        ("76. Subdomain Bruteforce", check_subdomain_bruteforce),
        ("77. HTTP Methods", check_http_methods),
        ("78. Sensitive Files", check_sensitive_files),
        ("79. Run All Analyses", None),
        ("80. Exit", None)
    ]
    print("\nSelect an option:")
    max_length = max(len(opt[0]) for opt in options) + 2
    for i in range(0, len(options), 5):
        row = options[i:i+5]
        formatted_row = [f"{Fore.LIGHTRED_EX}{opt[0]:<{max_length}}{Style.RESET_ALL}" for opt in row]
        while len(formatted_row) < 5:
            formatted_row.append(" " * max_length)
        print("  ".join(formatted_row))
    return options

def main_menu():
    print(BANNER)
    while True:
        clear_screen()
        print(BANNER)
        print("Jewish Website Fucker")
        print(f"{Fore.CYAN}Enter a website URL (Put A Fucking Website You Jew):{Style.RESET_ALL}")
        url = input("> ").strip()
        domain = get_domain(url)
        if not domain:
            print(f"{Fore.CYAN}Invalid URL or domain. Please enter a valid domain (e.g., example.com). Press Enter to try again.{Style.RESET_ALL}")
            input()
            continue

        while True:
            clear_screen()
            print(BANNER)
            print(f"Analyzing: {domain}")
            options = display_menu()
            print(f"{Fore.CYAN}Enter option (1-80): {Style.RESET_ALL}", end="")
            choice = input().strip()

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= 78:
                    options[choice_num-1][1](domain)
                elif choice_num == 79:
                    for opt in options[:-2]:
                        opt[1](domain)
                elif choice_num == 80:
                    print(f"{Fore.LIGHTGREEN_EX}Exiting...{Style.RESET_ALL}")
                    sys.exit(0)
                else:
                    print(f"{Fore.CYAN}Invalid option. Please choose 1-80.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.CYAN}Invalid input. Please enter a number between 1 and 80.{Style.RESET_ALL}")

            print(f"{Fore.CYAN}\nPress Enter to continue...{Style.RESET_ALL}")
            input()

if __name__ == "__main__":
    main_menu()