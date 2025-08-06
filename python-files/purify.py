import base64
import json
import re
import ipaddress
import socket
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# -----------------------------
# IP to country info via ipinfo.io
# -----------------------------

def get_country_info(host):
    try:
        # Resolve host to IP if it's not an IP
        try:
            ip = str(ipaddress.ip_address(host))
        except ValueError:
            ip = socket.gethostbyname(host)

        print(f"[+] Resolved IP for {host}: {ip}")
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            country_code = data.get('country', '')
            country_name = COUNTRY_NAMES.get(country_code, country_code)
            flag = country_code_to_flag(country_code)
            return flag, country_name
    except Exception as e:
        print(f"[!] Failed to get country info for {host}: {e}")
    return '🏳️', 'Unknown'

def country_code_to_flag(code):
    if not code:
        return '🏳️'
    return ''.join(chr(ord(c) + 127397) for c in code.upper())

COUNTRY_NAMES = {
    'US': 'United States',
    'GB': 'United Kingdom',
    'UK': 'United Kingdom',
    'DE': 'Germany',
    'FR': 'France',
    'CN': 'China',
    'JP': 'Japan',
    'IN': 'India',
    'RU': 'Russia',
    'AU': 'Australia',
    'IR': 'Iran',
    'CA': 'Canada',
    'SG': 'Singapore',
    # Add more as needed
}

# -----------------------------
# VMESS handler
# -----------------------------

def clean_vmess(base64_str):
    try:
        decoded = base64.b64decode(base64_str + '==').decode('utf-8')
        data = json.loads(decoded)

        host = data.get('add', '')
        flag, country = get_country_info(host)

        data['ps'] = f"{flag} {country} | join: @test"
        data['path'] = '/'
        data['tls'] = data.get('tls', '')
        data['aid'] = '0'
        data['net'] = data.get('net', 'ws')
        data['type'] = 'none'

        cleaned = json.dumps(data, separators=(',', ':'))
        encoded_config = base64.b64encode(cleaned.encode()).decode()
        return f"{flag} {country} | join: @test", f"vmess://{encoded_config}"
    except Exception as e:
        print(f"[!] Error cleaning vmess: {e}")
        return None, None

# -----------------------------
# VLESS / TROJAN handler
# -----------------------------

def clean_url_config(url, protocol):
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port
        userinfo = parsed.username

        flag, country = get_country_info(hostname)

        query = parse_qs(parsed.query)
        clean_query = {
            'security': query.get('security', ['tls'])[0] if protocol != 'ss' else None,
            'type': query.get('type', ['ws'])[0],
            'encryption': 'none' if protocol == 'vless' else None,
            'path': '/',
            'host': hostname,
            'sni': hostname,
        }
        clean_query = {k: v for k, v in clean_query.items() if v}

        new_netloc = f"{userinfo}@{hostname}:{port}"
        new_url = urlunparse((
            protocol,
            new_netloc,
            '/',
            '',
            urlencode(clean_query, doseq=True),
            ''
        ))

        return f"{flag} {country} | join: @test", new_url
    except Exception as e:
        print(f"[!] Error cleaning {protocol} config: {e}")
        return None, None

# -----------------------------
# Shadowsocks handler
# -----------------------------

def clean_ss(url):
    try:
        match = re.search(r'@([\w\.-]+)', url)
        host = match.group(1) if match else ''
        flag, country = get_country_info(host)

        if '#' in url:
            url = re.sub(r'#.*', '#' + f"{flag} {country} | join: @test", url)
        else:
            url += '#' + f"{flag} {country} | join: @test"

        return f"{flag} {country} | join: @test", url
    except Exception as e:
        print(f"[!] Error cleaning ss: {e}")
        return None, None

# -----------------------------
# Main processing function
# -----------------------------

def purify_configs(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    cleaned_lines = []
    for i, line in enumerate(lines):
        print(f"[{i+1}/{len(lines)}] Processing...")
        line = line.strip()
        if not line:
            continue

        label, cleaned = None, None

        if line.startswith('vmess://'):
            base64_str = line[8:]
            label, cleaned = clean_vmess(base64_str)
        elif line.startswith(('vless://', 'trojan://')):
            protocol = line.split('://')[0]
            label, cleaned = clean_url_config(line, protocol)
        elif line.startswith('ss://'):
            label, cleaned = clean_ss(line)
        else:
            print(f"[!] Unknown config type, skipping: {line}")
            continue

        if label and cleaned:
            cleaned_lines.append(label)
            cleaned_lines.append(cleaned)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(cleaned_lines) + '\n')

    print(f"\n✅ All configs processed and saved to: {output_file}")

# -----------------------------
# Entry point
# -----------------------------

if __name__ == '__main__':
    purify_configs('working_configs.txt', 'output.txt')
