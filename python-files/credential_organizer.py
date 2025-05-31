# -*- coding: utf-8 -*-
import os
import re
import random
import string
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
import time
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

# Constants
MIN_LINES_PER_DOMAIN = 100
MAX_LINES_PER_FILE = 10000
BAD_PASSWORDS = {'unknown', 'innocent'}
MAX_DOMAIN_LENGTH = 50  # Maximum allowed domain length to prevent errors
SIGNATURES = [
    """ ██▓     ▒█████  ▓█████ ▓█████▄ 
▓██▒    ▒██▒  ██▒▓█   ▀ ▒██▀ ██▌
▒██░    ▒██░  ██▒▒███   ░██   █▌
▒██░    ▒██   ██░▒▓█  ▄ ░▓█▄   ▌
░██████▒░ ████▓▒░░▒████▒░▒████▓ 
░ ▒░▓  ░░ ▒░▒░▒░ ░░ ▒░ ░ ▒▒▓  ▒ 
░ ░ ▒  ░  ░ ▒ ▒░  ░ ░  ░ ░ ▒  ▒ 
  ░ ░   ░ ░ ░ ▒     ░    ░ ░  ░ 
    ░  ░    ░ ░     ░  ░   ░    
                         ░      
  DEV: @L0ed0_backup |      @tesulm
 discord.gg/kA8zajfTRA | t.me/DorkerK_Info""",
    """▓█████▄  ▒█████   ██▀███   ██ ▄█▀▓█████  ██▀███      ██ ▄█▀
▒██▀ ██▌▒██▒  ██▒▓██ ▒ ██▒ ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒    ██▄█▒ 
░██   █▌▒██░  ██▒▓██ ░▄█ ▒▓███▄░ ▒███   ▓██ ░▄█ ▒   ▓███▄░ 
░▓█▄   ▌▒██   ██░▒██▀▀█▄  ▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄     ▓██ █▄ 
░▒████▓ ░ ████▓▒░░██▓ ▒██▒▒██▒ █▄░▒████▒░██▓ ▒██▒   ▒██▒ █▄
 ▒▒▓  ▒ ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░   ▒ ▒▒ ▓▒
 ░ ▒  ▒   ░ ▒ ▒░   ░▒ ░ ▒░░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░   ░ ░▒ ▒░
 ░ ░  ░ ░ ░ ░ ▒    ░░   ░ ░ ░░ ░    ░     ░░   ░    ░ ░░ ░ 
   ░        ░ ░     ░     ░  ░      ░  ░   ░        ░  ░   
 ░                                                         
  DEV: @L0ed0_backup |      @tesulm
 discord.gg/kA8zajfTRA | t.me/DorkerK_Info""",
    """      _            _               _    
   __| | ___  _ __| | _____ _ __  | | __
  / _` |/ _ \| '__| |/ / _ \ '__| | |/ /
 | (_| | (_) | |  |   <  __/ |    |   < 
  \__,_|\___/|_|  |_|\_\___|_|    |_|\_\\
                                        
  DEV: @L0ed0_backup |""",
    """  _     ___  _____ ____  
 | |   / _ \| ____|  _ \ 
 | |  | | | |  _| | | | |
 | |__| |_| | |___| |_| |
 |_____\___/|_____|____/ 
                         
  DEV: @L0ed0_backup |      @tesulm
 discord.gg/kA8zajfTRA | t.me/DorkerK_Info"""
]

class ConsoleUI:
    def __init__(self):
        self.start_time = time.time()
        self.processed_files = 0
        self.processed_lines = 0
        self.valid_lines = 0
        self.skipped_lines = 0
        self.unique_domains = set()
        self.domain_stats = defaultdict(int)
        self.tld_stats = defaultdict(set)
        self.url_length_stats = defaultdict(int)
        self.param_stats = defaultdict(int)
        self.error_log = []
        
    def print_header(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.YELLOW + Style.BRIGHT + "ULTRA-FAST CREDENTIALS ORGANIZER".center(80))
        print(Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.GREEN + "Processing files from: input/")
        print(Fore.CYAN + "-" * 80)
        
    def print_summary(self):
        elapsed = time.time() - self.start_time
        print(Fore.CYAN + "-" * 80)
        print(Fore.YELLOW + Style.BRIGHT + "PROCESSING SUMMARY".center(80))
        print(Fore.CYAN + "-" * 80)
        print(Fore.GREEN + f"Processed files: {self.processed_files}")
        print(Fore.GREEN + f"Total lines read: {self.processed_lines}")
        print(Fore.GREEN + f"Valid lines processed: {self.valid_lines}")
        print(Fore.RED + f"Skipped lines: {self.skipped_lines}")
        print(Fore.GREEN + f"Unique domains found: {len(self.unique_domains)}")
        print(Fore.GREEN + f"Unique TLDs found: {len(self.tld_stats)}")
        print(Fore.CYAN + f"Processing time: {elapsed:.2f} seconds")
        print(Fore.CYAN + f"Processing speed: {self.processed_lines/elapsed:.2f} lines/sec")
        print(Fore.CYAN + "-" * 80)
        
    def print_domain_stats(self):
        print(Fore.YELLOW + Style.BRIGHT + "TOP DOMAINS".center(80))
        print(Fore.CYAN + "-" * 80)
        sorted_domains = sorted(self.domain_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        for domain, count in sorted_domains:
            print(Fore.GREEN + f"{domain.ljust(30)}: {count}")
        print(Fore.CYAN + "-" * 80)
        
    def print_tld_stats(self):
        print(Fore.YELLOW + Style.BRIGHT + "TOP TLDs".center(80))
        print(Fore.CYAN + "-" * 80)
        sorted_tlds = sorted([(tld, len(domains)) for tld, domains in self.tld_stats.items()], 
                            key=lambda x: x[1], reverse=True)[:10]
        for tld, count in sorted_tlds:
            print(Fore.GREEN + f".{tld.ljust(15)}: {count} domains")
        print(Fore.CYAN + "-" * 80)
        
    def update_log(self, message, level="info"):
        colors = {
            "info": Fore.BLUE,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED
        }
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        log_entry = f"[{timestamp}] {message}"
        self.error_log.append(f"{level.upper()}: {log_entry}")
        print(f"{colors.get(level, Fore.WHITE)}{log_entry}")

def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def clean_domain(domain):
    """Remove subdomains and clean domain with length check"""
    if not domain or domain in {'android_apps', 'chrome_extensions'}:
        return domain
    
    parts = domain.split('.')
    if len(parts) < 2:
        return None  # Invalid domain format
    
    # Handle country TLDs
    country_tlds = {'co', 'com', 'gov', 'edu', 'net', 'org', 'ac', 'mil', 'sch'}
    if parts[-2] in country_tlds and len(parts) > 2:
        domain = '.'.join(parts[-3:])
    else:
        domain = '.'.join(parts[-2:])
    
    # Validate domain length
    if len(domain) > MAX_DOMAIN_LENGTH:
        return None
    
    return domain.lower()

def extract_domain(url):
    try:
        url = url.strip()
        if not url:
            return None
            
        # Handle special URLs
        if url.startswith('android://'):
            return 'android_apps'
        if url.startswith('chrome://'):
            return 'chrome_extensions'
            
        # Clean URL string
        url = url.split(' ')[0].split('?')[0].split('#')[0]
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        parsed = urlparse(url)
        domain = parsed.netloc.split(':')[0]
        
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return clean_domain(domain) if '.' in domain else None
    except:
        return None

def extract_tld(domain):
    try:
        if not domain or domain in {'android_apps', 'chrome_extensions'}:
            return None
        parts = domain.split('.')
        return parts[-1] if len(parts) >= 2 else None
    except:
        return None

def is_valid_line(line):
    """Flexible validation for credential lines"""
    try:
        line = line.strip()
        if not line or line.count(':') < 2:
            return False
            
        parts = line.rsplit(':', 2) if line.count(':') > 2 else line.split(':', 2)
        if len(parts) != 3:
            return False
            
        url, login, password = parts
        
        if not url or not login or not password:
            return False
            
        if password.strip().lower() in BAD_PASSWORDS:
            return False
            
        return True
    except:
        return False

def clean_login_pass(login, password):
    return f"{login.strip()}:{password.strip()}"

def add_signature_to_file(file_path):
    try:
        with open(file_path, 'r+', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            f.seek(0, 0)
            signature = random.choice(SIGNATURES)
            f.write(f"{signature}\n\n{content}\n\n{signature}")
    except Exception as e:
        return str(e)
    return None

def add_random_signature_every_100_lines(file_path):
    try:
        with open(file_path, 'r+', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
            new_lines = []
            for i, line in enumerate(lines):
                if i > 0 and i % 100 == 0:
                    pattern = random.choice([
                        f"LOED:{generate_random_password()}",
                        f"@L0ed0_backup:{generate_random_password()}",
                        f"{generate_random_password()}:LOED",
                        f"{generate_random_password()}:@L0ed0_backup"
                    ])
                    new_lines.append(f"{pattern}\n")
                new_lines.append(line)
            
            f.seek(0)
            f.writelines(new_lines)
            f.truncate()
    except Exception as e:
        return str(e)
    return None

def sanitize_filename(name):
    """Sanitize filename to prevent invalid characters"""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def process_url_length_analysis(url_length_map):
    """Organize URLs by length in separate files"""
    length_dir = os.path.join('output', 'url_length_analysis')
    os.makedirs(length_dir, exist_ok=True)
    
    for length, urls in url_length_map.items():
        safe_filename = f"{length}_chars.txt"
        try:
            with open(os.path.join(length_dir, safe_filename), 'w', encoding='utf-8') as f:
                f.write('\n'.join(urls))
        except Exception as e:
            return f"Error saving URL length file {safe_filename}: {str(e)}"
    return None

def process_tld_analysis(tld_stats, domain_url_map):
    """Organize URLs by TLD in separate files with sanitized filenames"""
    tld_dir = os.path.join('output', 'tld_analysis')
    os.makedirs(tld_dir, exist_ok=True)
    
    for tld, domains in tld_stats.items():
        safe_filename = f"{sanitize_filename(tld)}.txt"
        try:
            with open(os.path.join(tld_dir, safe_filename), 'w', encoding='utf-8') as f:
                for domain in domains:
                    f.write('\n'.join(domain_url_map[domain]) + '\n')
        except Exception as e:
            return f"Error saving TLD file {safe_filename}: {str(e)}"
    return None

def process_parameter_analysis(param_stats, param_url_map):
    """Organize URLs by parameter count"""
    param_dir = os.path.join('output', 'parameter_analysis')
    os.makedirs(param_dir, exist_ok=True)
    
    try:
        # Save URLs grouped by parameter count
        for param_count, urls in param_url_map.items():
            safe_filename = f"{param_count}_params.txt"
            with open(os.path.join(param_dir, safe_filename), 'w', encoding='utf-8') as f:
                f.write('\n'.join(urls))
        
        # Save all URLs with parameters in one file
        all_param_urls = []
        for urls in param_url_map.values():
            all_param_urls.extend(urls)
        
        with open(os.path.join(param_dir, 'all.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_param_urls))
    except Exception as e:
        return f"Error saving parameter analysis: {str(e)}"
    return None

def process_file(file_path, ui, url_length_map, domain_url_map, param_url_map):
    domain_data = defaultdict(set)
    skip_reasons = defaultdict(int)
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            ui.processed_lines += 1
            line = line.strip()
            
            if not line:
                skip_reasons['empty_line'] += 1
                continue
                
            if not is_valid_line(line):
                skip_reasons['invalid_format'] += 1
                continue
                
            try:
                parts = line.rsplit(':', 2) if line.count(':') > 2 else line.split(':', 2)
                url, login, password = parts
                
                domain = extract_domain(url)
                if not domain:
                    skip_reasons['invalid_domain'] += 1
                    continue
                    
                ui.valid_lines += 1
                login_pass = clean_login_pass(login, password)
                domain_data[domain].add(login_pass)  # Using set to automatically remove duplicates
                
                ui.unique_domains.add(domain)
                ui.domain_stats[domain] += 1
                
                tld = extract_tld(domain)
                if tld:
                    ui.tld_stats[tld].add(domain)
                
                # URL analysis
                url_length = len(url)
                ui.url_length_stats[url_length] += 1
                url_length_map[url_length].append(url)
                domain_url_map[domain].append(url)
                
                # Parameter analysis
                if '?' in url:
                    params = parse_qs(urlparse(url).query)
                    param_count = len(params)
                    ui.param_stats[param_count] += 1
                    param_url_map[param_count].append(url)
                    
            except Exception as e:
                skip_reasons['processing_error'] += 1
                continue
                
    ui.processed_files += 1
    ui.skipped_lines += sum(skip_reasons.values())
    
    # Log skip reasons
    if skip_reasons:
        ui.update_log(f"Skip reasons for {os.path.basename(file_path)}:", "info")
        for reason, count in skip_reasons.items():
            ui.update_log(f"  {reason}: {count}", "info")
    
    return domain_data

def save_domain_data(domain_data, ui):
    """Save organized credentials by domain with duplicate removal"""
    os.makedirs('output', exist_ok=True)
    os.makedirs('output/mix', exist_ok=True)
    
    mix_data = set()
    errors = []
    
    for domain, credentials in domain_data.items():
        count = len(credentials)
        
        if count >= MIN_LINES_PER_DOMAIN:
            domain_dir = f"output/{sanitize_filename(domain)}"
            if count > MAX_LINES_PER_FILE:
                os.makedirs(domain_dir, exist_ok=True)
                
            creds_list = list(credentials)
            chunks = [creds_list[i:i + MAX_LINES_PER_FILE] for i in range(0, len(creds_list), MAX_LINES_PER_FILE)]
            
            for i, chunk in enumerate(chunks):
                filename = f"{domain_dir}/PART {i+1} {sanitize_filename(domain)}.txt" if len(chunks) > 1 else f"output/{sanitize_filename(domain)}.txt"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(chunk))
                    
                    # Add signatures
                    sig_error = add_signature_to_file(filename)
                    if sig_error:
                        errors.append(f"Signature error in {filename}: {sig_error}")
                    
                    marker_error = add_random_signature_every_100_lines(filename)
                    if marker_error:
                        errors.append(f"Marker error in {filename}: {marker_error}")
                        
                except Exception as e:
                    errors.append(f"Error saving {filename}: {str(e)}")
        else:
            mix_data.update(credentials)
    
    # Save mixed data
    if mix_data:
        try:
            with open('output/mix/poor_sites.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(mix_data))
            
            sig_error = add_signature_to_file('output/mix/poor_sites.txt')
            if sig_error:
                errors.append(f"Signature error in poor_sites.txt: {sig_error}")
            
            marker_error = add_random_signature_every_100_lines('output/mix/poor_sites.txt')
            if marker_error:
                errors.append(f"Marker error in poor_sites.txt: {marker_error}")
                
        except Exception as e:
            errors.append(f"Error saving poor_sites.txt: {str(e)}")
    
    return errors

def save_error_log(ui, filename='error_log.txt'):
    """Save all error messages to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(ui.error_log))
    except Exception as e:
        print(Fore.RED + f"Failed to save error log: {str(e)}")

def main():
    ui = ConsoleUI()
    ui.print_header()
    
    # Initialize analysis data structures
    url_length_map = defaultdict(list)
    domain_url_map = defaultdict(list)
    param_url_map = defaultdict(list)
    
    # Check input directory
    input_dir = 'input'
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        ui.update_log("Created 'input' directory. Please add your files there.", "warning")
        save_error_log(ui)
        return
    
    # Get all text files
    file_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt')]
    
    if not file_paths:
        ui.update_log("No text files found in input directory!", "warning")
        save_error_log(ui)
        return
    
    # Process files
    all_domain_data = defaultdict(set)
    
    for file_path in file_paths:
        try:
            domain_data = process_file(file_path, ui, url_length_map, domain_url_map, param_url_map)
            
            # Merge results
            for domain, credentials in domain_data.items():
                all_domain_data[domain].update(credentials)
                
            # Save periodically to reduce memory usage
            if ui.processed_files % 5 == 0:
                errors = save_domain_data(all_domain_data, ui)
                if errors:
                    for error in errors:
                        ui.update_log(error, "error")
                all_domain_data.clear()
                
        except Exception as e:
            ui.update_log(f"Fatal error processing {file_path}: {str(e)}", "error")
            continue
    
    # Final save
    if all_domain_data:
        errors = save_domain_data(all_domain_data, ui)
        if errors:
            for error in errors:
                ui.update_log(error, "error")
    
    # Save analysis results
    try:
        err = process_url_length_analysis(url_length_map)
        if err:
            ui.update_log(err, "error")
        
        err = process_tld_analysis(ui.tld_stats, domain_url_map)
        if err:
            ui.update_log(err, "error")
        
        err = process_parameter_analysis(ui.param_stats, param_url_map)
        if err:
            ui.update_log(err, "error")
    except Exception as e:
        ui.update_log(f"Error during analysis: {str(e)}", "error")
    
    # Print summary
    ui.print_summary()
    ui.print_domain_stats()
    ui.print_tld_stats()
    
    # Save error log
    save_error_log(ui)
    
    ui.update_log("Processing completed successfully!", "success")
    ui.update_log(f"Error log saved to: error_log.txt", "info")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\nProcess interrupted by user.")
    except Exception as e:
        print(Fore.RED + f"Unexpected error: {str(e)}")
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"CRITICAL ERROR: {str(e)}\n")