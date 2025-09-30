import os
import time
import requests

# The path to the 'hosts' file. Do not change this.
hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
redirect_ip = "127.0.0.1"

# URL of a large, regularly updated list of adult websites
block_list_url = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"

def get_block_list():
    try:
        response = requests.get(block_list_url, timeout=10)
        if response.status_code == 200:
            return response.text.splitlines()
    except requests.exceptions.RequestException:
        return []

def block_websites():
    try:
        os.system(f'takeown /f "{hosts_path}" > nul 2>&1')
        os.system(f'icacls "{hosts_path}" /grant Everyone:F > nul 2>&1')
        block_list_content = get_block_list()
        
        with open(hosts_path, "r+") as file:
            content = file.read()
            for line in block_list_content:
                line = line.strip()
                if line and not line.startswith('#') and ('porn' in line.lower() or 'sex' in line.lower() or 'adult' in line.lower()):
                    parts = line.split()
                    if len(parts) > 1:
                        site = parts[1]
                        if site not in content:
                            file.write(f"\n{redirect_ip} {site}")
        
        os.system(f'icacls "{hosts_path}" /reset > nul 2>&1')
    except Exception:
        pass

if __name__ == "__main__":
    while True:
        block_websites()
        time.sleep(3600)