import os
import platform
import shutil
import subprocess
import time
import requests
import socket
from datetime import datetime

# Enhanced Colors & Effects
class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    CLEAR_SCREEN = '\033[2J\033[H'

def clear_terminal():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def center_text(text, color=""):
    try:
        columns = shutil.get_terminal_size().columns
        return color + text.center(columns) + Colors.RESET
    except:
        return color + text + Colors.RESET

def draw_ascii_art():
    print(Colors.CYAN + """
   _____ _               _ __        __      _                  
  / ___/| |__   __ _ _ __| |\ \      / /_ __ | | ___   ___  ___ 
  \___ \| '_ \ / _` | '__| __\ \ /\ / /| '_ \| |/ _ \ / _ \/ __|
  ___) | | | | (_| | |  | |_ \ V  V / | | | | | (_) |  __/\__ \\
 |____/|_| |_|\__,_|_|   \__| \_/\_/  |_| |_|_|\___/ \___||___/
    """ + Colors.RESET)

def has_vpn():
    try:
        result = subprocess.getoutput("ipconfig" if platform.system() == "Windows" else "ifconfig")
        keywords = ["tun", "ppp", "tap", "vpn", "wireguard", "openvpn"]
        return any(k in result.lower() for k in keywords)
    except:
        return False

def ping_host(host="8.8.8.8", count=1, timeout=1000, retries=2):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    for attempt in range(retries + 1):
        try:
            if platform.system().lower() == "windows":
                ping_cmd = ["ping", param, str(count), "-w", str(timeout), host]
            else:
                ping_cmd = ["ping", param, str(count), "-W", str(timeout//1000), host]
            
            output = subprocess.check_output(ping_cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            import re
            match = re.search(r'time[=<]\s*(\d+\.?\d*)\s*ms', output)
            if match:
                return float(match.group(1))
            else:
                match_avg = re.search(r'Average = (\d+)ms', output)
                if match_avg:
                    return float(match_avg.group(1))
            return None
        except subprocess.CalledProcessError:
            if attempt == retries:
                return None
            time.sleep(1)
        except Exception:
            return None
    return None

def print_banner():
    clear_terminal()
    draw_ascii_art()
    print(center_text("—" * 50, Colors.PURPLE))

    vpn_status = has_vpn()
    vpn_color = Colors.GREEN if vpn_status else Colors.RED
    print(center_text(f"VPN: {Colors.BOLD}{'ACTIVE' if vpn_status else 'INACTIVE'}{Colors.RESET}", vpn_color))

    ping_ms = ping_host()
    if ping_ms is None:
        conn_str = "N/A"
        conn_color = Colors.RED
    else:
        conn_color = Colors.GREEN if ping_ms <= 100 else Colors.YELLOW if ping_ms <= 300 else Colors.RED
        conn_str = f"{ping_ms:.1f} ms"
    print(center_text(f"CONNECTION: {Colors.BOLD}{conn_str}{Colors.RESET}", conn_color))

    print(center_text("—" * 50, Colors.PURPLE))
    print(center_text(f"{Colors.BOLD}TELEGRAM: @STSVKINGDOM{Colors.RESET}", Colors.CYAN))
    print(center_text("—" * 50, Colors.PURPLE))
    print(f"\n{Colors.BOLD}sharkwire{Colors.RESET} • ", end="")

def tools_menu():
    clear_terminal()
    print(f"{Colors.BOLD}{Colors.UNDERLINE}Available Tools:{Colors.RESET}\n")
    print(f"{Colors.BLUE}[A]{Colors.RESET} amira     - Advanced IP analysis tool")
    print(f"{Colors.BLUE}[Z]{Colors.RESET} zarpg     - Web vulnerability scanner")
    print(f"{Colors.BLUE}[R]{Colors.RESET} rcesim    - Remote code execution")
    print(f"{Colors.BLUE}[I]{Colors.RESET} ipmap     - IP geolocation mapper")
    print(f"{Colors.BLUE}[C]{Colors.RESET} c-ip      - AbuseIPDB checker")
    print(f"\n{Colors.YELLOW}Type -rt to return to main menu.{Colors.RESET}\n")
    while True:
        try:
            cmd = input(f"{Colors.BOLD}tools{Colors.RESET} • ").strip()
            if cmd.lower() == "-rt":
                break
            elif cmd.lower().startswith(("a", "amira")):
                parts = cmd.split()
                if len(parts) >= 4 and parts[1] == "-t" and parts[2] == "simpson":
                    target = parts[3]
                    amira_tool(target)
                else:
                    print(f"{Colors.RED}Usage: amira -t simpson [IP]{Colors.RESET}")
            elif cmd.lower().startswith(("z", "zarpg")):
                parts = cmd.split()
                if len(parts) >= 4 and parts[1] == "-vuln" and parts[2] == "-t":
                    url = parts[3]
                    zarpg_tool(url)
                else:
                    print(f"{Colors.RED}Usage: zarpg -vuln -t [URL]{Colors.RESET}")
            elif cmd.lower().startswith(("r", "rcesim")):
                parts = cmd.split()
                if len(parts) >= 5 and parts[1] == "-targz" and parts[2] == "-z":
                    ip = parts[3]
                    port = parts[4]
                    rcesim_tool(ip, port)
                else:
                    print(f"{Colors.RED}Usage: rcesim -targz -z [IP] [PORT]{Colors.RESET}")
            elif cmd.lower().startswith(("i", "ipmap")):
                parts = cmd.split()
                if len(parts) >= 5 and parts[1] == "-t" and parts[2] == "-ip" and parts[3] == "-h":
                    ip = parts[4]
                    ipmap_tool(ip)
                else:
                    print(f"{Colors.RED}Usage: ipmap -t -ip -h [IP]{Colors.RESET}")
            elif cmd.lower().startswith(("c", "c-ip")):
                parts = cmd.split()
                if len(parts) >= 3 and parts[1] == "-abuse":
                    ip = parts[2]
                    cip_abuse_tool(ip)
                else:
                    print(f"{Colors.RED}Usage: c-ip -abuse [IP]{Colors.RESET}")
            else:
                print(f"{Colors.RED}Unknown command. Type -rt to return.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error: {str(e)}{Colors.RESET}")

def help_menu():
    clear_terminal()
    print(f"{Colors.BOLD}{Colors.UNDERLINE}Command Help:{Colors.RESET}\n")
    print(f"  {Colors.GREEN}tools{Colors.RESET}        → List available tools")
    print(f"  {Colors.GREEN}help{Colors.RESET}         → Show this help menu")
    print(f"  {Colors.YELLOW}-rt{Colors.RESET}          → Return to main menu")
    print(f"\n{Colors.YELLOW}Type -rt to return to main menu.{Colors.RESET}\n")
    while True:
        try:
            cmd = input(f"{Colors.BOLD}help{Colors.RESET} • ").strip().lower()
            if cmd == "-rt":
                break
        except:
            break

def amira_tool(ip):
    clear_terminal()
    print(center_text(f"AMIRA ANALYSIS: {ip}", Colors.PURPLE))
    print(center_text("—" * 50, Colors.PURPLE))
    
    try:
        # Get IP information
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}IP Information:{Colors.RESET}")
        ipapi_url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp,org,as,lat,lon,query"
        response = requests.get(ipapi_url, timeout=10)
        data = response.json()
        
        if data.get("status") == "success":
            print(f"  {Colors.BLUE}IP:{Colors.RESET} {data.get('query')}")
            print(f"  {Colors.BLUE}Location:{Colors.RESET} {data.get('city', 'N/A')}, {data.get('regionName', 'N/A')}, {data.get('country', 'N/A')}")
            print(f"  {Colors.BLUE}ISP:{Colors.RESET} {data.get('isp', 'N/A')}")
            print(f"  {Colors.BLUE}Organization:{Colors.RESET} {data.get('org', 'N/A')}")
            print(f"  {Colors.BLUE}AS:{Colors.RESET} {data.get('as', 'N/A')}")
            print(f"  {Colors.BLUE}Coordinates:{Colors.RESET} {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
            print(f"  {Colors.BLUE}Map:{Colors.RESET} https://www.google.com/maps/search/?api=1&query={data.get('lat')},{data.get('lon')}")
        else:
            print(f"  {Colors.RED}Failed to get IP information: {data.get('message', 'Unknown error')}{Colors.RESET}")
        
        # Port scan simulation (real scan would require proper permissions)
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Common Port Status:{Colors.RESET}")
        common_ports = [21, 22, 80, 443, 3389]
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                status = f"{Colors.GREEN}OPEN{Colors.RESET}" if result == 0 else f"{Colors.RED}CLOSED{Colors.RESET}"
                print(f"  Port {port}: {status}")
                sock.close()
            except:
                print(f"  Port {port}: {Colors.YELLOW}ERROR{Colors.RESET}")
        
    except requests.RequestException:
        print(f"\n{Colors.RED}Failed to connect to IP API service{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error during analysis: {str(e)}{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Type -rt to return to tools.{Colors.RESET}")
    while True:
        try:
            if input(f"{Colors.BOLD}amira{Colors.RESET} • ").strip().lower() == "-rt":
                break
        except:
            break

def zarpg_tool(url):
    clear_terminal()
    print(center_text(f"ZARPG SCAN: {url}", Colors.PURPLE))
    print(center_text("—" * 50, Colors.PURPLE))
    
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Scanning Target:{Colors.RESET} {url}")
        
        # Check if target is online
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            print(f"\n  {Colors.BLUE}Status:{Colors.RESET} {Colors.GREEN}ONLINE{Colors.RESET} ({response_time:.2f} ms)")
            print(f"  {Colors.BLUE}Server:{Colors.RESET} {response.headers.get('Server', 'N/A')}")
            print(f"  {Colors.BLUE}Powered-By:{Colors.RESET} {response.headers.get('X-Powered-By', 'N/A')}")
        except requests.RequestException:
            print(f"\n  {Colors.RED}Target appears to be offline or unreachable{Colors.RESET}")
            raise
        
        # Security headers check
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Security Headers:{Colors.RESET}")
        security_headers = {
            'X-Frame-Options': 'Clickjacking protection',
            'Content-Security-Policy': 'Content Security Policy',
            'X-Content-Type-Options': 'MIME sniffing protection',
            'X-XSS-Protection': 'XSS protection',
            'Strict-Transport-Security': 'HTTPS enforcement'
        }
        
        for header, description in security_headers.items():
            if header in response.headers:
                print(f"  {Colors.GREEN}✓{Colors.RESET} {header}: {description}")
            else:
                print(f"  {Colors.RED}✗{Colors.RESET} {header}: Missing")
        
        # Vulnerability checks
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Vulnerability Checks:{Colors.RESET}")
        
        # Open Redirect Test
        try:
            test_url = f"{url}/redirect?url=http://evil.com"
            r = requests.get(test_url, timeout=5, allow_redirects=False)
            if 'location' in r.headers and "evil.com" in r.headers['location']:
                print(f"  {Colors.RED}✗{Colors.RESET} Open Redirect vulnerability detected!")
            else:
                print(f"  {Colors.GREEN}✓{Colors.RESET} No open redirect vulnerability found")
        except:
            print(f"  {Colors.YELLOW}?{Colors.RESET} Could not test for open redirect")
        
        # Basic XSS test
        try:
            test_url = f"{url}/?q=<script>alert('XSS')</script>"
            r = requests.get(test_url, timeout=5)
            if "<script>alert('XSS')</script>" in r.text:
                print(f"  {Colors.RED}✗{Colors.RESET} Possible XSS vulnerability detected!")
            else:
                print(f"  {Colors.GREEN}✓{Colors.RESET} No obvious XSS vulnerability found")
        except:
            print(f"  {Colors.YELLOW}?{Colors.RESET} Could not test for XSS")
        
    except Exception as e:
        print(f"\n{Colors.RED}Scan failed: {str(e)}{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Type -rt to return to tools.{Colors.RESET}")
    while True:
        try:
            if input(f"{Colors.BOLD}zarpg{Colors.RESET} • ").strip().lower() == "-rt":
                break
        except:
            break

def rcesim_tool(ip, port):
    clear_terminal()
    print(center_text(f"RCESIM TARGET: {ip}:{port}", Colors.PURPLE))
    print(center_text("—" * 50, Colors.PURPLE))
    
    try:
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Target Information:{Colors.RESET}")
        print(f"  {Colors.BLUE}IP:{Colors.RESET} {ip}")
        print(f"  {Colors.BLUE}Port:{Colors.RESET} {port}")
        
        # Check if port is open
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, int(port)))
            if result == 0:
                print(f"  {Colors.BLUE}Status:{Colors.RESET} {Colors.GREEN}PORT OPEN{Colors.RESET}")
            else:
                print(f"  {Colors.BLUE}Status:{Colors.RESET} {Colors.RED}PORT CLOSED{Colors.RESET}")
                sock.close()
                raise Exception("Port is closed")
            sock.close()
        except:
            print(f"  {Colors.BLUE}Status:{Colors.RESET} {Colors.RED}PORT CLOSED{Colors.RESET}")
            raise Exception("Port is closed")
        
        # Try to identify service
        try:
            service = socket.getservbyport(int(port))
            print(f"  {Colors.BLUE}Likely Service:{Colors.RESET} {service}")
        except:
            print(f"  {Colors.BLUE}Likely Service:{Colors.RESET} Unknown")
        
        # Try basic interaction
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Basic Interaction:{Colors.RESET}")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((ip, int(port)))
            s.send(b"HELO\n")
            banner = s.recv(1024).decode().strip()
            s.close()
            print(f"  {Colors.BLUE}Banner:{Colors.RESET}\n{banner}")
        except:
            print(f"  {Colors.RED}Could not retrieve banner{Colors.RESET}")
        
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Type -rt to return to tools.{Colors.RESET}")
    while True:
        try:
            if input(f"{Colors.BOLD}rcesim{Colors.RESET} • ").strip().lower() == "-rt":
                break
        except:
            break

def ipmap_tool(ip):
    clear_terminal()
    print(center_text(f"IPMAP LOCATION: {ip}", Colors.PURPLE))
    print(center_text("—" * 50, Colors.PURPLE))
    
    try:
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Fetching Geolocation Data:{Colors.RESET}")
        
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query", timeout=10)
        data = response.json()
        
        if data.get("status") == "success":
            print(f"  {Colors.BLUE}IP Address:{Colors.RESET} {data.get('query')}")
            print(f"  {Colors.BLUE}Location:{Colors.RESET} {data.get('city', 'N/A')}, {data.get('regionName', 'N/A')}, {data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})")
            print(f"  {Colors.BLUE}ZIP Code:{Colors.RESET} {data.get('zip', 'N/A')}")
            print(f"  {Colors.BLUE}Timezone:{Colors.RESET} {data.get('timezone', 'N/A')}")
            print(f"  {Colors.BLUE}ISP:{Colors.RESET} {data.get('isp', 'N/A')}")
            print(f"  {Colors.BLUE}Organization:{Colors.RESET} {data.get('org', 'N/A')}")
            print(f"  {Colors.BLUE}AS:{Colors.RESET} {data.get('as', 'N/A')}")
            print(f"  {Colors.BLUE}Coordinates:{Colors.RESET} {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
            
            print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Google Maps:{Colors.RESET}")
            print(f"  https://www.google.com/maps/search/?api=1&query={data.get('lat')},{data.get('lon')}")
            
            print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Additional Services:{Colors.RESET}")
            print(f"  {Colors.BLUE}Shodan:{Colors.RESET} https://www.shodan.io/host/{ip}")
            print(f"  {Colors.BLUE}AbuseIPDB:{Colors.RESET} https://www.abuseipdb.com/check/{ip}")
        else:
            print(f"  {Colors.RED}Error: {data.get('message', 'Unknown error')}{Colors.RESET}")
            
    except requests.RequestException:
        print(f"\n{Colors.RED}Failed to connect to geolocation service{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Type -rt to return to tools.{Colors.RESET}")
    while True:
        try:
            if input(f"{Colors.BOLD}ipmap{Colors.RESET} • ").strip().lower() == "-rt":
                break
        except:
            break

def cip_abuse_tool(ip):
    clear_terminal()
    print(center_text(f"C-IP ABUSE CHECK: {ip}", Colors.PURPLE))
    print(center_text("—" * 50, Colors.PURPLE))
    
    ABUSEIPDB_API_KEY = "b17d1cae32f73c6fa068768ff8df3d7a4ead97fa9a0704349f8ff20b3c7959c5d1e26026e53ecddb"  # Replace with your actual API key
    
    try:
        if not ABUSEIPDB_API_KEY or ABUSEIPDB_API_KEY == "YOUR_API_KEY_HERE":
            raise Exception("API key not configured")
        
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Checking AbuseIPDB:{Colors.RESET}")
        
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {
            'Key': ABUSEIPDB_API_KEY,
            'Accept': 'application/json'
        }
        params = {
            'ipAddress': ip,
            'maxAgeInDays': '90',
            'verbose': ''
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            report_data = data.get('data', {})
            
            print(f"  {Colors.BLUE}IP:{Colors.RESET} {report_data.get('ipAddress', 'N/A')}")
            print(f"  {Colors.BLUE}Domain:{Colors.RESET} {report_data.get('domain', 'N/A')}")
            print(f"  {Colors.BLUE}Hostnames:{Colors.RESET} {', '.join(report_data.get('hostnames', [])) or 'N/A'}")
            print(f"  {Colors.BLUE}Country:{Colors.RESET} {report_data.get('countryCode', 'N/A')}")
            print(f"  {Colors.BLUE}ISP:{Colors.RESET} {report_data.get('isp', 'N/A')}")
            print(f"  {Colors.BLUE}Usage Type:{Colors.RESET} {report_data.get('usageType', 'N/A')}")
            
            print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Abuse Reports:{Colors.RESET}")
            print(f"  {Colors.BLUE}Total Reports:{Colors.RESET} {report_data.get('totalReports', 0)}")
            print(f"  {Colors.BLUE}Distinct Users:{Colors.RESET} {report_data.get('numDistinctUsers', 0)}")
            print(f"  {Colors.BLUE}Last Reported:{Colors.RESET} {report_data.get('lastReportedAt', 'Never')}")
            
            confidence = report_data.get('abuseConfidenceScore', 0)
            if confidence > 75:
                confidence_color = Colors.RED
            elif confidence > 40:
                confidence_color = Colors.YELLOW
            else:
                confidence_color = Colors.GREEN
            print(f"  {Colors.BLUE}Abuse Confidence:{Colors.RESET} {confidence_color}{confidence}%{Colors.RESET}")
            
            print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Additional Information:{Colors.RESET}")
            print(f"  {Colors.BLUE}Is Public:{Colors.RESET} {'Yes' if report_data.get('isPublic', False) else 'No'}")
            print(f"  {Colors.BLUE}Is Whitelisted:{Colors.RESET} {'Yes' if report_data.get('isWhitelisted', False) else 'No'}")
            print(f"  {Colors.BLUE}Is Tor:{Colors.RESET} {'Yes' if report_data.get('isTor', False) else 'No'}")
            
            if 'reports' in report_data:
                print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Recent Reports:{Colors.RESET}")
                for report in report_data['reports'][:3]:  # Show only 3 most recent
                    print(f"  {Colors.BLUE}Date:{Colors.RESET} {report.get('reportedAt', 'N/A')}")
                    print(f"  {Colors.BLUE}Reporter:{Colors.RESET} {report.get('reporterId', 'Anonymous')}")
                    print(f"  {Colors.BLUE}Categories:{Colors.RESET} {', '.join(str(c) for c in report.get('categories', []))}")
                    print(f"  {Colors.BLUE}Comment:{Colors.RESET} {report.get('comment', 'None')[:100]}...")
                    print("  " + "-"*40)
        else:
            error_msg = f"API Error: HTTP {response.status_code}"
            if response.status_code == 429:
                error_msg = "API rate limit exceeded (try again later)"
            elif response.status_code == 401:
                error_msg = "Invalid API key"
            print(f"  {Colors.RED}{error_msg}{Colors.RESET}")
            
    except requests.RequestException:
        print(f"\n{Colors.RED}Failed to connect to AbuseIPDB API{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Type -rt to return to tools.{Colors.RESET}")
    while True:
        try:
            if input(f"{Colors.BOLD}c-ip{Colors.RESET} • ").strip().lower() == "-rt":
                break
        except:
            break

def handle_command(cmd):
    cmd = cmd.lower().strip()
    if cmd == "tools":
        tools_menu()
    elif cmd == "help":
        help_menu()
    elif cmd == "-rt":
        return
    elif cmd.startswith("amira"):
        parts = cmd.split()
        if len(parts) >= 4 and parts[1] == "-t" and parts[2] == "simpson":
            target = parts[3]
            amira_tool(target)
        else:
            print(f"{Colors.RED}Usage: amira -t simpson [IP]{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}Unknown command. Type 'help' for assistance.{Colors.RESET}")

def main():
    while True:
        try:
            print_banner()
            cmd = input(f"{Colors.BOLD}sharkwire{Colors.RESET} • ").strip()
            if cmd.lower() in ["exit", "quit", "q"]:
                print(f"\n{Colors.BLUE}Shutting down...{Colors.RESET}")
                break
            else:
                handle_command(cmd)
        except KeyboardInterrupt:
            print(f"\n{Colors.BLUE}Shutting down...{Colors.RESET}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error: {str(e)}{Colors.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()