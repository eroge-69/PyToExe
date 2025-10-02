import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import json
import os
import threading
import time
import random
from datetime import datetime

class MailRuAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://e.mail.ru/api/v1"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://e.mail.ru',
            'Referer': 'https://e.mail.ru/'
        })
        self.email = None
        self.is_authenticated = False
        self.cookies_dir = "cookies"
        self.proxy_manager = ProxyManager()

    def _ensure_cookies_dir(self):
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)

    def _get_cookie_filename(self, email: str) -> str:
        safe_email = email.replace('@', '_at_').replace('.', '_')
        return os.path.join(self.cookies_dir, f"{safe_email}.txt")

    def save_cookies(self, email: str):
        try:
            self._ensure_cookies_dir()
            cookie_file = self._get_cookie_filename(email)
            
            cookies_dict = {}
            for cookie in self.session.cookies:
                cookies_dict[cookie.name] = {
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure
                }
            
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            return False

    def load_cookies(self, email: str) -> bool:
        try:
            cookie_file = self._get_cookie_filename(email)
            
            if not os.path.exists(cookie_file):
                return False
            
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies_dict = json.load(f)
            
            for name, cookie_data in cookies_dict.items():
                self.session.cookies.set(
                    name=name,
                    value=cookie_data['value'],
                    domain=cookie_data.get('domain', '.mail.ru'),
                    path=cookie_data.get('path', '/')
                )
            
            return True
            
        except Exception as e:
            return False

    def check_cookie_validity(self, email: str) -> bool:
        try:
            if not self.load_cookies(email):
                return False
            
            proxy = self.proxy_manager.get_random_proxy()
            if proxy:
                self.session.proxies.update(proxy)
            
            response = self.session.get("https://e.mail.ru/inbox", allow_redirects=False, timeout=10)
            
            if response.status_code == 200 and email in response.text:
                self.email = email
                self.is_authenticated = True
                return True
            else:
                return False
                
        except Exception:
            return False

    def login(self, email: str, password: str) -> bool:
        try:
            if self.check_cookie_validity(email):
                return True
            
            proxy = self.proxy_manager.get_random_proxy()
            if proxy:
                self.session.proxies.update(proxy)
            
            self.session.get("https://mail.ru", timeout=10)
            
            login_data = {
                'page': 'https://e.mail.ru/inbox',
                'FailPage': '',
                'Username': email,
                'Password': password,
                'Domain': 'mail.ru',
                'saveauth': '1'
            }
            
            response = self.session.post(
                'https://auth.mail.ru/cgi-bin/auth',
                data=login_data,
                allow_redirects=True,
                timeout=10
            )
            
            if response.status_code == 200 and email in response.text:
                self.email = email
                self.is_authenticated = True
                self.save_cookies(email)
                return True
            else:
                return False
                
        except Exception:
            return False

    def get_messages(self, folder: str = "inbox", limit: int = 10):
        try:
            mock_messages = [
                {
                    'id': f'msg_{i}',
                    'subject': f'Тестовое письмо {i}',
                    'from': {'email': f'sender{i}@mail.ru', 'name': f'Отправитель {i}'},
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'snippet': f'Текст письма {i}...'
                }
                for i in range(1, limit + 1)
            ]
            return mock_messages
            
        except Exception:
            return []

    def send_message(self, to: str, subject: str, body: str) -> bool:
        try:
            time.sleep(0.5)
            return True
            
        except Exception:
            return False

    def bulk_send(self, recipients: list, subject: str, body: str) -> dict:
        try:
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            for i, recipient in enumerate(recipients, 1):
                proxy = self.proxy_manager.get_random_proxy()
                if proxy:
                    self.session.proxies.update(proxy)
                
                if self.send_message(recipient, subject, body):
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(recipient)
                
                if i < len(recipients):
                    time.sleep(1)
            
            return results
            
        except Exception as e:
            return {'success': 0, 'failed': len(recipients), 'errors': [str(e)]}

    def logout(self):
        try:
            if self.email:
                cookie_file = self._get_cookie_filename(self.email)
                if os.path.exists(cookie_file):
                    os.remove(cookie_file)
            
            self.session.cookies.clear()
            self.email = None
            self.is_authenticated = False
            
        except Exception:
            pass

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.load_proxies()
    
    def load_proxies(self):
        proxy_files = ['proxy.txt', 'proxies.txt', 'proxy_list.txt']
        for proxy_file in proxy_files:
            if os.path.exists(proxy_file):
                try:
                    with open(proxy_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                self.proxies.append(line)
                except Exception:
                    pass
    
    def get_random_proxy(self):
        if not self.proxies:
            return None
        
        proxy_str = random.choice(self.proxies)
        
        if '://' in proxy_str:
            return {'http': proxy_str, 'https': proxy_str}
        else:
            return {'http': f'http://{proxy_str}', 'https': f'https://{proxy_str}'}

class MailRuCloudClient:
    def __init__(self, session: requests.Session):
        self.session = session
        self.base_url = "https://cloud.mail.ru/api/v2"

    def get_disk_info(self):
        try:
            return {
                'total': 10737418240,
                'used': 2147483648,
                'free': 8589934592,
                'used_percent': 20
            }
        except Exception:
            return {}

    def list_files(self, path: str = "/"):
        try:
            mock_files = [
                {'name': 'document.pdf', 'type': 'file', 'size': 1048576, 'path': '/document.pdf'},
                {'name': 'image.jpg', 'type': 'file', 'size': 524288, 'path': '/image.jpg'},
                {'name': 'Projects', 'type': 'folder', 'size': 0, 'path': '/Projects'},
            ]
            return mock_files
        except Exception:
            return []

class MailRuClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mail.ru Client - Multi-Account Manager")
        self.root.geometry("900x700")
        
        self.accounts = []
        self.current_client = None
        self.cookies_dir = "cookies"
        
        self.setup_gui()
        self.load_accounts()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="🚀 Mail.ru Multi-Account Client", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        accounts_frame = ttk.LabelFrame(main_frame, text="👥 Управление аккаунтами", padding="10")
        accounts_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.accounts_listbox = tk.Listbox(accounts_frame, height=6, width=50)
        self.accounts_listbox.grid(row=0, column=0, rowspan=4, padx=(0, 10))
        self.accounts_listbox.bind('<<ListboxSelect>>', self.on_account_select)
        
        ttk.Button(accounts_frame, text="➕ Добавить аккаунт", 
                  command=self.add_account).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Button(accounts_frame, text="🗑️ Удалить аккаунт", 
                  command=self.delete_account).grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Button(accounts_frame, text="🔄 Проверить все", 
                  command=self.check_all_accounts).grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Button(accounts_frame, text="🚀 Массовая рассылка", 
                  command=self.bulk_send_dialog).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        status_frame = ttk.LabelFrame(main_frame, text="📊 Статус", padding="10")
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=12, width=80)
        self.status_text.grid(row=0, column=0, columnspan=2)
        
        ttk.Button(main_frame, text="📧 Проверить почту", 
                  command=self.check_email).grid(row=3, column=0, pady=5, padx=5)
        ttk.Button(main_frame, text="☁️ Облако", 
                  command=self.check_cloud).grid(row=3, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="🧹 Очистить логи", 
                  command=self.clear_logs).grid(row=3, column=2, pady=5, padx=5)
        
    def log_message(self, message):
        self.status_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def load_accounts(self):
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)
            
        self.accounts = []
        for file in os.listdir(self.cookies_dir):
            if file.endswith('.txt'):
                email = file.replace('_at_', '@').replace('_', '.').replace('.txt', '')
                self.accounts.append(email)
                
        self.update_accounts_list()
        
    def update_accounts_list(self):
        self.accounts_listbox.delete(0, tk.END)
        for account in self.accounts:
            self.accounts_listbox.insert(tk.END, account)
            
    def on_account_select(self, event):
        selection = self.accounts_listbox.curselection()
        if selection:
            account = self.accounts[selection[0]]
            self.log_message(f"Выбран аккаунт: {account}")
            
    def add_account(self):
        def login_thread():
            email = email_entry.get()
            password = password_entry.get()
            
            if not email or not password:
                messagebox.showerror("Ошибка", "Введите email и пароль")
                return
                
            login_dialog.destroy()
            self.log_message(f"Добавление аккаунта: {email}")
            
            client = MailRuAPIClient()
            if client.login(email, password):
                self.accounts.append(email)
                self.update_accounts_list()
                self.log_message(f"✅ Аккаунт {email} успешно добавлен")
            else:
                self.log_message(f"❌ Ошибка добавления аккаунта {email}")
        
        login_dialog = tk.Toplevel(self.root)
        login_dialog.title("Добавление аккаунта")
        login_dialog.geometry("300x150")
        
        ttk.Label(login_dialog, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        email_entry = ttk.Entry(login_dialog, width=30)
        email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(login_dialog, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(login_dialog, width=30, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(login_dialog, text="Войти", 
                  command=lambda: threading.Thread(target=login_thread).start()).grid(row=2, column=1, pady=10)
        
    def delete_account(self):
        selection = self.accounts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите аккаунт для удаления")
            return
            
        account = self.accounts[selection[0]]
        if messagebox.askyesno("Подтверждение", f"Удалить аккаунт {account}?"):
            safe_email = account.replace('@', '_at_').replace('.', '_')
            cookie_file = os.path.join(self.cookies_dir, f"{safe_email}.txt")
            if os.path.exists(cookie_file):
                os.remove(cookie_file)
            self.accounts.remove(account)
            self.update_accounts_list()
            self.log_message(f"🗑️ Аккаунт {account} удален")
            
    def check_all_accounts(self):
        def check_thread():
            self.log_message("🔄 Проверка всех аккаунтов...")
            for account in self.accounts:
                client = MailRuAPIClient()
                if client.check_cookie_validity(account):
                    self.log_message(f"✅ {account} - активен")
                else:
                    self.log_message(f"❌ {account} - неактивен")
            self.log_message("✅ Проверка завершена")
            
        threading.Thread(target=check_thread).start()
        
    def bulk_send_dialog(self):
        if not self.accounts:
            messagebox.showerror("Ошибка", "Нет добавленных аккаунтов")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Массовая рассылка")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Выберите аккаунты для рассылки:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        accounts_frame = ttk.Frame(dialog)
        accounts_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.account_vars = {}
        for i, account in enumerate(self.accounts):
            var = tk.BooleanVar(value=True)
            self.account_vars[account] = var
            ttk.Checkbutton(accounts_frame, text=account, variable=var).grid(row=i, column=0, sticky=tk.W)
        
        ttk.Label(dialog, text="Файл с получателями:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        emails_file = ttk.Entry(dialog, width=30)
        emails_file.grid(row=2, column=1, padx=5, pady=5)
        emails_file.insert(0, "emails.txt")
        
        ttk.Label(dialog, text="Файл с текстом:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        message_file = ttk.Entry(dialog, width=30)
        message_file.grid(row=3, column=1, padx=5, pady=5)
        message_file.insert(0, "message.txt")
        
        ttk.Label(dialog, text="Тема письма:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        subject_entry = ttk.Entry(dialog, width=30)
        subject_entry.grid(row=4, column=1, padx=5, pady=5)
        subject_entry.insert(0, "Важное сообщение")
        
        def start_bulk_send():
            selected_accounts = [acc for acc, var in self.account_vars.items() if var.get()]
            if not selected_accounts:
                messagebox.showerror("Ошибка", "Выберите хотя бы один аккаунт")
                return
                
            dialog.destroy()
            self.start_bulk_send(selected_accounts, emails_file.get(), message_file.get(), subject_entry.get())
            
        ttk.Button(dialog, text="🚀 Начать рассылку", 
                  command=start_bulk_send).grid(row=5, column=1, pady=10)
        
    def start_bulk_send(self, accounts, emails_file, message_file, subject):
        def bulk_send_thread():
            try:
                with open(emails_file, 'r', encoding='utf-8') as f:
                    recipients = [line.strip() for line in f if line.strip()]
                    
                with open(message_file, 'r', encoding='utf-8') as f:
                    body = f.read()
                    
                self.log_message(f"📨 Начинаем массовую рассылку")
                self.log_message(f"👥 Аккаунты: {len(accounts)}")
                self.log_message(f"📧 Получатели: {len(recipients)}")
                
                total_success = 0
                total_failed = 0
                
                for account in accounts:
                    self.log_message(f"🔑 Работаем через: {account}")
                    client = MailRuAPIClient()
                    
                    if client.check_cookie_validity(account):
                        results = client.bulk_send(recipients, subject, body)
                        total_success += results['success']
                        total_failed += results['failed']
                        self.log_message(f"✅ {account}: {results['success']} успешно, {results['failed']} неудачно")
                    else:
                        self.log_message(f"❌ {account}: невалидные куки")
                        total_failed += len(recipients)
                    
                    time.sleep(2)
                
                self.log_message(f"🎯 ИТОГО: {total_success} успешно, {total_failed} неудачно")
                self.log_message("✅ Рассылка завершена!")
                
            except Exception as e:
                self.log_message(f"❌ Ошибка рассылки: {e}")
                
        threading.Thread(target=bulk_send_thread).start()
        
    def check_email(self):
        selection = self.accounts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите аккаунт")
            return
            
        account = self.accounts[selection[0]]
        self.log_message(f"📧 Проверка почты для {account}...")
        
    def check_cloud(self):
        selection = self.accounts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите аккаунт")
            return
            
        account = self.accounts[selection[0]]
        self.log_message(f"☁️ Проверка облака для {account}...")
        
    def clear_logs(self):
        self.status_text.delete(1.0, tk.END)
        self.log_message("🧹 Логи очищены")

if __name__ == "__main__":
    root = tk.Tk()
    app = MailRuClientGUI(root)
    root.mainloop()